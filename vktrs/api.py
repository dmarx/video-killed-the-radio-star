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
    print("built client")

    # auto-retry if mitigation triggered
    while max_retries:
        print("top of loop")
        try:
            answers = stability_api.generate(prompt=prompt, **kargs)
            print("requesting answers")
            response = process_response(answers)
            print("processing responses")
            for img in response:
                print("got us an image")
                yield img
                break # yeah this would be what we need to change to request multiple images at a time...
        except RuntimeError:
            print("runtime error")
            max_retries -= 1
            warnings.warn(f"mitigation triggered, retries remaining: {max_retries}")


def process_response(answers):
    print("inside response processor")
    # iterating over the generator produces the api response
    for resp in answers:
        print("inside response")
        for artifact in resp.artifacts:
            print("inside artifact")
            #print(artifact.finish_reason)
            if artifact.finish_reason == generation.FILTER:
                print("emitting warning")
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
                #raise RuntimeError
            if artifact.type == generation.ARTIFACT_IMAGE:
                print("got us an image")
                img = Image.open(io.BytesIO(artifact.binary))
                yield img
