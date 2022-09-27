import datetime as dt
import re

from bs4 import BeautifulSoup
import yt_dlp


# embedding yt-dlp instead of CLI let's us hold on to the output filepaths
# probably way more trouble than it's worth and should just use yt-dlp CLI
#video_url = 'https://www.youtube.com/watch?v=WJaxFbdjm8c'
#!yt-dlp --write-auto-subs {video_url}


# I still have mixed feelings about using this helper class vs. just using the yt-dlp cli
class YoutubeHelper:
    def __init__(
        self, 
        video_url,
        ydl_opts = {
            #'outtmpl':{'default':"ytdlp_content.%(ext)s"},
            'writeautomaticsub':True,
            'subtitlesformat':'srv2/vtt'
            },
    ):
        self.url = video_url
        #with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        self.info = self.ydl.extract_info(video_url, download=True)
        #self.subs = self.get_subtitles()
        #self.audio = self.get_audio()

    def get_subtitles(
        self,
        lang='en',
        fmt='vtt', # 'vtt','ttml','srv3','srv2','srv1','json3'
    ):
        cc_targets = self.info['automatic_captions'][lang]
        item = [item for item in cc_targets if item['ext']==fmt]
        try:
            assert len(item) > 0
        except AssertionError:
            print(
                f"Captions for language [{lang}] and format [{fmt}] not available. "
                "Please try a different language or subtitle format"
            )
            return
        return item[0]

def parse_timestamp(ts):
    t = dt.datetime.strptime(ts,"%H:%M:%S.%f")
    return dt.timedelta(
        hours=t.hour,
        minutes=t.minute,
        seconds=t.second,
        microseconds=t.microsecond,
        )

def vtt_to_token_timestamps(captions):

    all_word_starts_raw = []
    chunk_starts = {}
    for cap in captions:
      chunks = cap.text.split('\n')
      chunks_raw = cap.raw_text.split('\n')
      for c, cr in zip(chunks, chunks_raw):
          if not c.strip():
              continue
          if '<c>' in cr:
              cr=f"<{cap.start}>{cr}"
              all_word_starts_raw.append(cr)
              chunk_starts[c] = cap.start

    # write once, read never.
    pat = re.compile("<?(([0-9:.]{12})>(<c>){0,1}(.+?))<")

    token_start_times = []
    for line in all_word_starts_raw:
      starts_ = [
          {'ts':hit[1], 
           'tok':hit[3].strip(),
           'td':parse_timestamp(hit[1])
           } 
           for hit in re.findall(pat, line)]
      token_start_times.extend(starts_)

    return token_start_times

def srv2_to_token_timestamps(srv2_xml):
    srv2_soup = BeautifulSoup(srv2_xml, 'xml')
    return [
        {
         'ts':e['t'], 
         'tok':e.text,
         #'td':dt.timedelta(microseconds=int(e['t']))
         'td':dt.timedelta(milliseconds=int(e['t']))
         } 
        for e in srv2_soup.find_all('text')
        if e.text.strip() 
    ]