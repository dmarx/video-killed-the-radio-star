from pathlib import Path
import torch
from torch import autocast
from diffusers import (
    StableDiffusionImg2ImgPipeline,
    StableDiffusionPipeline,
)

# weird, why didn't this install with vktrs?
#!pip install pytokenizations yt-dlp python-tsp webvtt-py

#use_stability_api = False


# to do: rename "start_schedule" to "strength"
# start_schedule=(1-image_consistency))


class HfHelper:
    def __init__(
        self,
        device = 'cuda',
        device_img2img = None,
        device_text2img = None,
        model_path = '.',
        model_id = "CompVis/stable-diffusion-v1-4",
        download=True,
    ):
        if not device_img2img:
            device_img2img = device
        if not device_text2img:
            device_text2img = device
        self.device = device
        self.device_img2img = device_img2img
        self.device_text2img = device_text2img
        self.model_path = model_path
        self.model_id = model_id
        self.download = download
        self.load_pipelines()

    def load_pipelines(
        self,
    ):
        if self.download:
            img2img = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.model_id,
                revision="fp16", 
                torch_dtype=torch.float16,
                use_auth_token=True
            )
            img2img = img2img.to(self.device)
            img2img.save_pretrained(self.model_path)
        else:
            img2img = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.model_path,
                local_files_only=True
            ).to(self.device)

        text2img = StableDiffusionPipeline(
            vae=img2img.vae,
            text_encoder=img2img.text_encoder,
            tokenizer=img2img.tokenizer,
            unet=img2img.unet,
            feature_extractor=img2img.feature_extractor,
            scheduler=img2img.scheduler,
            safety_checker=img2img.safety_checker,
        )
        #return text2img, img2img
        text2img.enable_attention_slicing()
        img2img.enable_attention_slicing()
        self.text2img = text2img
        self.img2img = img2img

    def get_image_for_prompt(
        self,
        prompt,
        **kwargs
    ):
        f = self.text2img if kwargs.get('init_image') is None else self.img2img
        #if kwargs.get('image_consistency') is not None:
        #kwargs['strength'] = 1- kwargs['image_consistency'] 
        if kwargs.get('start_schedule') is not None:
            #kwargs['strength'] = kwargs['start_schedule']
            kwargs['strength'] = kwargs.pop('start_schedule')
        with autocast(self.device):
            return f(prompt, **kwargs)
