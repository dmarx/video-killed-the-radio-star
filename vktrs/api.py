import io
import os
from PIL import Image, ImageDraw, ImageFont
import warnings

from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


def get_image_for_prompt(prompt, max_retries=3, **kargs):
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'], 
        verbose=False,
    )


    # auto-retry if mitigation triggered
    while max_retries:

        try:
            answers = stability_api.generate(prompt=prompt, **kargs)

            response = process_response(answers)

            for img in response:

                yield img

            break # whoops... this breaks us out of the while loop, not the for loop.
        except RuntimeError:
            print("runtime error")
            max_retries -= 1
            warnings.warn(f"mitigation triggered, retries remaining: {max_retries}")


def process_response(answers):

    # iterating over the generator produces the api response
    for resp in answers:

        for artifact in resp.artifacts:

            #print(artifact.finish_reason)
            if artifact.finish_reason == generation.FILTER:

                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
                #raise RuntimeError
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                yield img

