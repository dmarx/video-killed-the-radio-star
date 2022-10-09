"""
# Automatic Speech Recognition utilities

Currently uses openai/whisper. To install: 
  pip install git+https://github.com/openai/whisper
"""

import time

import tokenizations
from vktrs.utils import remove_punctuation
import whisper


def whisper_transcribe(
    audio_fpath="audio.mp3",
):
    whispers = {
        'tiny':None, # 5.83 s
        'large':None # 3.73 s
    }
    # accelerated runtime required for whisper
    # to do: pypi package for whisper
    
    for k in whispers.keys():
        options = whisper.DecodingOptions(
            language='en',
        )
        # to do: be more proactive about cleaning up these models when we're done with them
        model = whisper.load_model(k).to('cuda')
        start = time.time()
        print(f"Transcribing audio with whisper-{k}")
        
        # to do: calling transcribe like this unnecessarily re-processes audio each time.
        whispers[k] = model.transcribe(audio_fpath) # re-processes audio each time, ~10s overhead?
        print(f"elapsed: {time.time()-start}")
    return whispers


def whisper_align(whispers):
    # sanitize and tokenize
    whispers_tokens = {}
    for k in whispers:
        whispers_tokens[k] = [
        remove_punctuation(tok) for tok in whispers[k]['text'].split()
        ]

    # align sequences
    tiny2large, large2tiny = tokenizations.get_alignments( #seqdiff.diff( #= tokenizations.get_alignments(
        whispers_tokens['tiny'],
        whispers_tokens['large']
    )
    return tiny2large, large2tiny, whispers_tokens


def whisper_transmit_meta_across_alignment(
    whispers,
    large2tiny,
    whispers_tokens,
):
    idx=0
    tokenized_prompts_tiny = []
    for phrase_idx, phrase in enumerate(whispers['tiny']['segments']):
        rec = {
            'start': phrase['start'],
            'end': phrase['end'],
            'tokens':[],
            'indices':[],
        }

        # TO DO: I should really use this tokenization for the alignment step to ensure the indices match up
        for tok in phrase['text'].split():
            tok = remove_punctuation(tok)
            rec['tokens'].append(tok)
            rec['indices'].append(idx)
            idx+=1

        tokenized_prompts_tiny.append(rec)

    # flatten
    token_tinyindex_segmentations = {}
    for rec in tokenized_prompts_tiny:
        for j, idx in enumerate(rec['indices']):
            token_tinyindex_segmentations[idx] ={
                'token':rec['tokens'][j],
                'start':rec['start'],
                'end':rec['end'],
            }
    
    #token_tinyindex_segmentations
    token_large_index_segmentations = {}
    for i, result in enumerate(large2tiny):
        rec_large = {'token':whispers_tokens['large'][i]}
        for j in result:
            rec_tiny = token_tinyindex_segmentations[j]
            if not rec_large.get('start'):
                rec_large['start'] = rec_tiny['start']
                rec_large['end'] = rec_tiny['end']
        
        # handle null result. this could be more elegant/DRY, but this way is less confusing to me at least.
        # basically, we're just backfilling here, so each entry will have a start and end time
        if not rec_large.get('start'):
            if i == 0:
                rec_large['start'] = 0
            else:
                rec_prev = token_large_index_segmentations[i-1]
                rec_large['start'] = rec_prev['start']
                rec_large['end'] = rec_prev.get('end')
        
        token_large_index_segmentations[i] = rec_large
    
    return token_large_index_segmentations


def whisper_segment_transcription(
    token_large_index_segmentations,
):
    """
    apply whisper-tiny segmentations to whisper-large transcriptions

    """
    token_large_phrase_segmentations = []
    start_prev = 0
    end_prev=0
    current_phrase = []
    for rec in token_large_index_segmentations.values():

        # we're in the same phrase as previous step
        if rec['start'] == start_prev:
            current_phrase.append(rec['token'])
            start_prev = rec['start']
            end_prev = rec.get('end')
            continue

        # we're in the next phrase, 
        token_large_phrase_segmentations.append({
            'tokens': current_phrase,
            'start':start_prev,
            'end':end_prev,
        })
        current_phrase = []

        # ...which starts immediately after the previous phrase
        if rec['start'] == end_prev:
            current_phrase.append(rec['token'])
            start_prev = rec['start']
            end_prev = rec['end']
            continue
        
        # ...or else there's a gap between when the last phrase ended and this one starts,
        # and I'm frankly not sure how I want to adress that yet.
        else:
            #raise NotImplementedError
            # let's just do.. this? for now? I guess?
            current_phrase.append(rec['token'])
            start_prev = rec['start']
            end_prev = rec['end']
            continue

    # how about we not drop the last lyric?
    # should this be a for-finally clause?
    token_large_phrase_segmentations.append({
            'tokens': current_phrase,
            'start':start_prev,
            'end':end_prev,
        })

    # reshape the data structure
    prompt_starts = [
            {'ts':rec['start'],
            'prompt':' '.join(rec['tokens'])
            }
        for rec in token_large_phrase_segmentations]
    
    return prompt_starts


def whisper_lyrics(audio_fpath="audio.mp3"):
    whispers = whisper_transcribe(audio_fpath)
    tiny2large, large2tiny, whispers_tokens = whisper_align(whispers)
    token_large_index_segmentations = whisper_transmit_meta_across_alignment(
        whispers,
        large2tiny,
        whispers_tokens,
    )
    prompt_starts = whisper_segment_transcription(
        token_large_index_segmentations,
    )
    return prompt_starts