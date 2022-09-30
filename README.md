# Video Killed The Radio Star [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dmarx/video-killed-the-radio-star/blob/main/Video_Killed_The_Radio_Star_Defusion.ipynb)



## Requirements

* ffmpeg - https://ffmpeg.org/
* pytorch - https://pytorch.org/get-started/locally/
* vktrs - (this repo) - `pip install vktrs[api]`
* stability_sdk api token - https://beta.dreamstudio.ai/ > circular icon in top right > membership > API Key
* whisper - `pip install git+https://github.com/openai/whisper`

## FAQ

**What is this?**

TLDR: Automated music video maker, given an mp3 or a youtube URL

**How does this animation technique work?**

For each text prompt you provide, the notebook will...

1. Generate an image based on that text prompt (using stable diffusion)
2. Use the generated image as the `init_image` to recombine with the text prompt to generate variations similar to the first image. This produces a sequence of extremely similar images based on the original text prompt
3. Images are then intelligently reordered to find the smoothest animation sequence of those frames
3. This image sequence is then repeated to pad out the animation duration as needed

The technique demonstrated in this notebook was inspired by a [video](https://www.youtube.com/watch?v=WJaxFbdjm8c) created by Ben Gillin.

**How are lyrics transcribed?**

This notebook uses openai's recently released 'whisper' model for performing automatic speech recognition. 
OpenAI was kind of to offer several different sizes of this model which each have their own pros and cons. 
This notebook uses the largest whisper model for transcribing the actual lyrics. Additionally, we use the 
smallest model for performing the lyric segmentation. Neither of these models is perfect, but the results 
so far seem pretty decent.

The first draft of this notebook relied on subtitles from youtube videos to determine timing, which was
then aligned with user-provided lyrics. Youtube's automated captions are powerful and I'll update the
notebook shortly to leverage those again, but for the time being we're just using whisper for everything
and not referencing user-provided captions at all.

**Something didn't work quite right in the transcription process. How do fix the timing or the actual lyrics?**

The notebook is divided into several steps. Between each step, a "storyboard" file is updated. If you want to
make modifications, you can edit this file directly and those edits should be reflected when you next load the
file. Depending on what you changed and what step you run next, your changes may be ignored or even overwritten.
Still playing with different solutions here.

**Can I provide my own images to 'bring to life' and associate with certain lyrics/sequences?**

Yes, you can! As described above: you just need to modify the storyboard. Will describe this functionality in
greater detail after the implementation stabilizes a bit more.

**This gave me an idea and I'd like to use just a part of your process here. What's the best way to reuse just some of the machinery you've developed here?**

Most of the functionality in this notebook has been offloaded to library I published to pypi called `vktrs`. I strongly encourage you to import anything you need 
from there rather than cutting and pasting function into a notebook. Similarly, if you have ideas for improvements, please don't hesitate to submit a PR!

## Dev notes

installing unreleased package in colab:

```
!pip install --upgrade setuptools build
!git clone --branch hf https://github.com/dmarx/video-killed-the-radio-star/
!cd video-killed-the-radio-star;  python -m build; python -m pip install .[api,hf]
```
