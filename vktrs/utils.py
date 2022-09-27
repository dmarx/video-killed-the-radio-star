from pathlib import Path
import random
import string
import subprocess
import textwrap

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

def gpu_info():
    outv = subprocess.run([
        'nvidia-smi',
            # these lines concatenate into a single query string
            '--query-gpu='
            'timestamp,'
            'name,'
            'utilization.gpu,'
            'utilization.memory,'
            'memory.used,'
            'memory.free,'
            ,
         '--format=csv'
        ],
        stdout=subprocess.PIPE).stdout.decode('utf-8')

    header, rec = outv.split('\n')[:-1]
    return pd.DataFrame({' '.join(k.strip().split('.')).capitalize():v for k,v in zip(header.split(','), rec.split(','))}, index=[0]).T


def remove_punctuation(s):
    # https://stackoverflow.com/a/266162/819544
    return s.translate(str.maketrans('', '', string.punctuation))



def add_caption2image(
      image, 
      caption, 
      text_font='LiberationSans-Regular.ttf', 
      font_size=20,
      fill_color=(255, 255, 255),
      stroke_color=(0, 0, 0), #stroke_fill
      stroke_width=2,
      align='center',
      ):
    # via https://stackoverflow.com/a/59104505/819544
    wrapper = textwrap.TextWrapper(width=50) 
    word_list = wrapper.wrap(text=caption) 
    caption_new = ''
    for ii in word_list[:-1]:
        caption_new = caption_new + ii + '\n'
    caption_new += word_list[-1]

    draw = ImageDraw.Draw(image)

    # Download the Font and Replace the font with the font file. 
    font = ImageFont.truetype(text_font, size=font_size)
    w,h = draw.textsize(caption_new, font=font, stroke_width=stroke_width)
    W,H = image.size
    x,y = 0.5*(W-w),0.90*H-h
    draw.text(
        (x,y), 
        caption_new,
        font=font,
        fill=fill_color, 
        stroke_fill=stroke_color,
        stroke_width=stroke_width,
        align=align,
    )

    return image


def rand_str(n_char=5):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n_char))


def save_frame(
    img: Image,
    idx:int=0,
    root_path=Path('./frames'),
    name=None,
):
    root_path.mkdir(parents=True, exist_ok=True)
    if name is None:
        name = rand_str()
    outpath = root_path / f"{idx}-{name}.png"
    img.save(outpath)
    return str(outpath)