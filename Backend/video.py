import os
import uuid

import requests
import requests._internal_utils
import srt_equalizer
import assemblyai as aai
import math
from utils import *

from typing import List
from moviepy.editor import *
from moviepy.video.fx.fadein import fadein
from termcolor import colored
from dotenv import load_dotenv
from datetime import timedelta
from datetime import datetime as dateTimePy
from moviepy.video.fx.all import crop


from moviepy.video.tools.subtitles import SubtitlesClip
from extensions.string_extension import *
from extensions.urlchecks import *
import numpy as np
from utils import *
from template import *

load_dotenv("../.env")

ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")


def save_video(video_url: str, directory: str = "../temp") -> str:
    """
    Saves a video from a given URL and returns the path to the video.

    Args:
        video_url (str): The URL of the video to save.
        directory (str): The path of the temporary directory to save the video to

    Returns:
        str: The path to the saved video.
    """
    video_id = uuid.uuid4()
    video_path = f"{directory}/{video_id}.mp4"
    with open(video_path, "wb") as f:
        f.write(requests.get(video_url).content)

    return video_path

def save_image(image_url: str, directory: str = "../temp") -> str:
    """
    Saves a video from a given URL and returns the path to the video.

    Args:
        video_url (str): The URL of the video to save.
        directory (str): The path of the temporary directory to save the video to

    Returns:
        str: The path to the saved video.
    """
    
    if(not is_url(image_url)):
       video_path = choose_random_video(image_url)
       return video_path
    
    image_id = uuid.uuid4()
    image_path = f"{directory}/{image_id}.png"
    
    with open(image_path, "wb") as f:
        f.write(requests.get(image_url).content)

    return image_path


def __generate_subtitles_assemblyai(audio_path: str, voice: str) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.

    Returns:
        str: The generated subtitles
    """

    language_mapping = {
        "br": "pt",
        "id": "en", #AssemblyAI doesn't have Indonesian 
        "jp": "ja",
        "kr": "ko",
    }

    if voice in language_mapping:
        lang_code = language_mapping[voice]
    else:
        lang_code = voice

    aai.settings.api_key = ASSEMBLY_AI_API_KEY
    config = aai.TranscriptionConfig(language_code=lang_code)
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(audio_path)
    subtitles = transcript.export_subtitles_srt()

    return subtitles

def generate_description_locally(sentences: List[str], audio_clips: List[AudioFileClip]) -> list:

    start_time = 0
    descriptions = []

    for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):
                
        duration = audio_clip.duration
        end_time = start_time + duration

        descriptions.append(((start_time, end_time), f"{sentence}"))

        start_time += duration  # Update start time for the next subtitle
        
    print(colored(f"[+] descriptions generated.{descriptions}", "green"))

    return descriptions

def generate_pre_titles_locally(sentences: List[str], audio_clips: List[AudioFileClip]) -> list:

    start_time = 0
    titles = []

    for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):        
        duration = audio_clip.duration
        end_time = start_time + duration
        
        if(i < len(sentences)):
            titles.append(((start_time, end_time), f"Next: {i+1}. {sentences[i]}"))
            
        else:
            titles.append(((start_time, end_time), f"Thank you! Subscribe."))
            
            

        start_time += duration  # Update start time for the next subtitle
        
    print(colored(f"[+] Pre Titles generated.{titles}", "green"))

    return titles

def generate_titles_locally(sentences: List[str], audio_clips: List[AudioFileClip]) -> list:

    start_time = 0
    titles = []

    for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):
                
        duration = audio_clip.duration
        end_time = start_time + duration

        titles.append(((start_time, end_time), sentence))

        start_time += duration  # Update start time for the next subtitle
        
    print(colored(f"[+] Titles generated.{titles}", "green"))

    return titles

def __generate_subtitles_locally(sentences: List[str], audio_clips: List[AudioFileClip]) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track
    Returns:
        str: The generated subtitles
    """

    def convert_to_srt_time_format(total_seconds):
        # Convert total seconds to the SRT time format: HH:MM:SS,mmm
        if total_seconds == 0:
            return "0:00:00,0"
        return str(timedelta(seconds=total_seconds)).rstrip('0').replace('.', ',')

    start_time = 0
    subtitles = []
    
    for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):
        duration = audio_clip.duration
        end_time = start_time + duration

        # Format: subtitle index, start time --> end time, sentence
        subtitle_entry = f"{i}\n{convert_to_srt_time_format(start_time)} --> {convert_to_srt_time_format(end_time)}\n{sentence}\n"
        subtitles.append(subtitle_entry)

        start_time += duration  # Update start time for the next subtitle

    return "\n".join(subtitles)

def generate_titles(audio_path: str, titles: List[str], audio_clips: List[AudioFileClip], voice: str) -> str:
    """
    Generates titles from a given audio file and returns the path to the titles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track

    Returns:
        str: The path to the generated subtitles.
    """

    # def equalize_subtitles(srt_path: str, max_chars: int = 10) -> None:
    #     # Equalize subtitles
    #     srt_equalizer.equalize_srt_file(srt_path, srt_path, max_chars)

    # Save subtitles
    titles_path = f"../titles/{uuid.uuid4()}.srt"

    if ASSEMBLY_AI_API_KEY is not None and ASSEMBLY_AI_API_KEY != "":
        print(colored("[+] Creating titles using AssemblyAI", "blue"))
        titles = __generate_subtitles_assemblyai(audio_path, voice)
    else:
        print(colored("[+] Creating titles locally", "blue"))
        titles = generate_titles_locally(titles, audio_clips)
        # print(colored("[-] Local subtitle generation has been disabled for the time being.", "red"))
        # print(colored("[-] Exiting.", "red"))
        # sys.exit(1)
        
    print(colored("[*] titles: " + titles, "blue"))

    with open(titles_path, "w") as file:
        file.write(titles)

    # Equalize subtitles
    # equalize_subtitles(titles_path)

    print(colored("[+] Titles generated.", "green"))

    return titles_path

def generate_subtitles(audio_path: str, sentences: List[str], audio_clips: List[AudioFileClip], voice: str) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.
        sentences (List[str]): all the sentences said out loud in the audio clips
        audio_clips (List[AudioFileClip]): all the individual audio clips which will make up the final audio track

    Returns:
        str: The path to the generated subtitles.
    """

    def equalize_subtitles(srt_path: str, max_chars: int = 20) -> None:
        # Equalize subtitles
        srt_equalizer.equalize_srt_file(srt_path, srt_path, max_chars)

    # Save subtitles
    subtitles_path = f"../subtitles/{uuid.uuid4()}.srt"

    if ASSEMBLY_AI_API_KEY is not None and ASSEMBLY_AI_API_KEY != "":
        print(colored("[+] Creating subtitles using AssemblyAI", "blue"))
        subtitles = __generate_subtitles_assemblyai(audio_path, voice)
    else:
        print(colored("[+] Creating subtitles locally", "blue"))
        subtitles = __generate_subtitles_locally(sentences, audio_clips)
        # print(colored("[-] Local subtitle generation has been disabled for the time being.", "red"))
        # print(colored("[-] Exiting.", "red"))
        # sys.exit(1)

    with open(subtitles_path, "w", encoding='utf-8') as file:
        file.write(subtitles)

    # Equalize subtitles
    equalize_subtitles(subtitles_path)

    print(colored("[+] Subtitles generated.", "green"))

    return subtitles_path

# def draw_line_center(frame):
#     """Draw a rectangle in the frame"""
#     # change (top, bottom, left, right) to your coordinates
#     frame[top, left: right] = color
#     frame[bottom, left: right] = color
#     frame[top: bottom, left] = color
#     frame[top: bottom, right] = color
#     return frame




def combine_videos(video_paths: List[str], max_duration: int, max_clip_duration: int, threads: int) -> str:
    """
    Combines a list of videos into one video and returns the path to the combined video.

    Args:
        video_paths (List): A list of paths to the videos to combine.
        max_duration (int): The maximum duration of the combined video.
        max_clip_duration (int): The maximum duration of each clip.
        threads (int): The number of threads to use for the video processing.

    Returns:
        str: The path to the combined video.
    """
    video_id = uuid.uuid4()
    combined_video_path = f"../temp/{video_id}.mp4"
    
    # Required duration of each clip
    req_dur = max_duration / len(video_paths)

    print(colored("[+] Combining videos...", "blue"))
    print(colored(f"[+] Each clip will be maximum {req_dur} seconds long.", "blue"))

    clips = []
    tot_dur = 0
    # Add downloaded clips over and over until the duration of the audio (max_duration) has been reached
    while tot_dur < max_duration:
        for video_path in video_paths:
            clip = VideoFileClip(video_path)
            clip = clip.without_audio()
            # Check if clip is longer than the remaining audio
            if (max_duration - tot_dur) < clip.duration:
                clip = clip.subclip(0, (max_duration - tot_dur))
            # Only shorten clips if the calculated clip length (req_dur) is shorter than the actual clip to prevent still image
            elif req_dur < clip.duration:
                clip = clip.subclip(0, req_dur)
            clip = clip.set_fps(30)

            # Not all videos are same size,
            # so we need to resize them
            if round((clip.w/clip.h), 4) < 0.5625:
                clip = crop(clip, width=clip.w, height=round(clip.w/0.5625), \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            else:
                clip = crop(clip, width=round(0.5625*clip.h), height=clip.h, \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            clip = clip.resize((1080, 1920))

            if clip.duration > max_clip_duration:
                clip = clip.subclip(0, max_clip_duration)

            clips.append(clip)
            tot_dur += clip.duration


    #add clip on final
    # clipFinal = VideoFileClip("../templates/final.mp4")
    # clipFinal = clipFinal.without_audio()
    # clipFinal = clipFinal.set_fps(30)
    # clips.append(clipFinal)

    final_clip = concatenate_videoclips(clips)
    final_clip = final_clip.set_fps(30)
    final_clip.write_videofile(combined_video_path, threads=threads)
    
    print(colored("[+] Video was combined", "blue"))

    return combined_video_path


def generate_titles_locally(sentences: List[str], audio_clips: List[AudioFileClip]) -> list:

    start_time = 0
    titles = []

    for i, (sentence, audio_clip) in enumerate(zip(sentences, audio_clips), start=1):
                
        duration = audio_clip.duration
        end_time = start_time + duration

        titles.append(((start_time, end_time), sentence))

        start_time += duration  # Update start time for the next subtitle
        
    print(colored(f"[+] Titles generated.{titles}", "green"))

    return titles


def  generate_video(video_type:str, image_paths: list, titles: List[str], sentences: List[str], audio_clips: list, tts_path: str, max_duration: int, description_path: list, titles_path: list, subtitles_path: str, threads: int,  text_color : str, subject: str) -> str:
    """
    This function creates the final video, with subtitles and audio.

    Args:
        combined_video_path (str): The path to the combined video.
        tts_path (str): The path to the text-to-speech audio.
        subtitles_path (str): The path to the subtitles.
        threads (int): The number of threads to use for the video processing.
        subtitles_position (str): The position of the subtitles.

    Returns:
        str: The path to the final video.
    """
    
    try:
        switch = {
            "politica": "#011efe",
            "futebol": "#0bff01",
            "fofoca": "#f000ff",
            "dorama": "#fe0000",
            "bitcoin": "#ffac00",
            "curiosidades": "#200589",
            "financas": "#200589",
            "tecnologia": "#ab20fd",
        }
        
        text_color = switch.get(subject, text_color)
            
        final_clip = get_final_clip(video_type, image_paths,titles,sentences, audio_clips, tts_path, max_duration,description_path,titles_path,subtitles_path,text_color, subject)
        #subscribe_clip = get_subscribe_clip(video_type)
  
        fileName = dateTimePy.now().strftime("%m_%d_%Y_%H%M%S")
        
        last_title = remove_special_character(titles[0]).replace(" ", "_")
        fileName += f'_{last_title}'
        
        #clips = []
        
        #clips.append(final_clip)
        #clips.append(subscribe_clip)
        
        #result = concatenate_videoclips(clips)
        
        final_clip.write_videofile(f"../temp/{fileName}.mp4", threads=threads or 2)

        print(colored(f"[+] Final video file name: {fileName}", "green"))

        return f"{fileName}.mp4"
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(colored(f"[-] Error generating {video_type} video: {e} {exc_type} {fname} {exc_tb.tb_lineno}", "red"))

def radius_mask(size, radius):
    mask = 255 * np.ones((size, size, 3), dtype=np.uint8)
    Y, X = np.ogrid[:size, :size]
    mask_area = (X <= radius) | (X >= size - radius) | (Y <= radius) | (Y >= size - radius) | ((X - size + radius)**2 + (Y - radius)**2 <= radius**2) | ((X - radius)**2 + (Y - size + radius)**2 <= radius**2)
    mask[~mask_area] = 0
    return mask

def circle_mask(size):
    mask = 255 * np.ones((size, size, 3), dtype=np.uint8)
    center = size // 2
    Y, X = np.ogrid[:size, :size]
    mask_area = (X - center) ** 2 + (Y - center) ** 2 <= center ** 2
    mask[~mask_area] = 0
    return mask