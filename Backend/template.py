import math

from typing import List
from moviepy.editor import *
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.crop import crop
import moviepy.video.fx.all as vfx
from moviepy.video.fx.make_loopable import make_loopable
from termcolor import colored


from moviepy.video.tools.subtitles import SubtitlesClip
from extensions.string_extension import *
from extensions.urlchecks import *
import numpy as np
from utils import *


SHORT_MARGIN_TOP = 722
LONG_MARGIN_TOP = 520

VIDEO_SIZE = 1920
VIDELO_SIZE_2 = 1080

SHORT_VIDEO_HEIGHT = VIDEO_SIZE
SHORT_VIDEO_WIDTH = VIDELO_SIZE_2

LONG_VIDEO_HEIGHT = VIDELO_SIZE_2
LONG_VIDEO_WIDTH = VIDEO_SIZE

secounds_for_end_of_video = 6



def get_base_video(max_duration: int, video_type: str, subject: str) -> ImageClip:
    
    
    duration = max_duration + secounds_for_end_of_video
    
    video_size = (SHORT_VIDEO_WIDTH, SHORT_VIDEO_HEIGHT) if is_short_video_type(video_type) else (LONG_VIDEO_WIDTH, LONG_VIDEO_HEIGHT)
    
    color_clip = ColorClip(size=video_size, color=(0, 0, 0), duration=duration)
    
    return color_clip

def get_base_image(max_duration: int, video_type: str, subject: str):
    
    image_for_not_valid_url = choose_random_image(subject)
    
    video_size = (SHORT_VIDEO_WIDTH, SHORT_VIDEO_HEIGHT) if is_short_video_type(video_type) else (LONG_VIDEO_WIDTH, LONG_VIDEO_HEIGHT)
    
    clip = ImageClip(image_for_not_valid_url, duration=max_duration).resize(video_size)
    #clip = fadein(clip, 0.2)
    #clip = clip.resize(lambda t: 1 - 0.01 * t)
    
    return clip   

positionImageTop = ("center","top") 

def get_concatene_images(is_short_video: bool, image_paths: List[str], titles: List[str], sentences: List[str], audio_clips: List[AudioFileClip]) -> list:
    
    print(colored(f"[+] Combining video from images: {image_paths}", "blue"))
    
    #positionImageTop = ("center","top") if is_short_video else ("right","center")
    
    #clip2.set_position((0.4,0.7), relative=True)
    topImageHeight = 1080 if is_short_video else LONG_VIDEO_HEIGHT
    topImageWidth= LONG_VIDEO_WIDTH
    top_image_width = SHORT_VIDEO_WIDTH + 100 if is_short_video else LONG_VIDEO_WIDTH+600
    tot_dur = 0
    start_time = 0
    
    image_clip_list = []
    chapter = ''
    #clip = ''
    
    
    # def make_frame(t, duration):
    #     progress = t / duration
    #     bar_width = int(progress * SHORT_VIDEO_WIDTH) / 2
    #     bar = TextClip(txt=' ' * 50, fontsize=70, color='red', bg_color='blue', size=(bar_width, 50))
    #     bar = bar.set_position(('center', 'bottom')).set_duration(duration)
    #     return bar.img
    
    for i, (title, sentence, audio_clip, image) in enumerate(zip(titles, sentences, audio_clips, image_paths), start=0):
    
        duration = audio_clip.duration
        
        if(image.endswith('.png')):
            clip = ImageClip(image, duration=duration).set_position(positionImageTop, relative=True).resize(width=top_image_width)
            
            if(is_short_video):
                clip = clip.resize(height=1300)
            
            clip = fadein(clip, 0.2)
            clip = clip.resize(lambda t: 1 - 0.014 * t)
            image_clip_list.append(clip)
            
        else:
            clip = VideoFileClip(filename=image, audio=False).set_duration(duration)
            
            if(is_short_video):
                clip = crop(clip, x_center=1080, y_center=1080, width=SHORT_VIDEO_WIDTH, height=SHORT_VIDEO_HEIGHT)
                
            clip = clip.set_position(('center', 'top')) if is_short_video else clip.set_position(('center', 'center'))
            
            if(is_short_video):
                clip = clip.resize(height=1400)
                
            image_clip_list.append(clip)
        
        #clip = clip.fl(lambda gf, t: make_frame(t, duration))

        #image_clip_list.append(clip)
        
        if(i == 0):
            chapter += f"0:00 {title}\n"
        
        else:
            chapter += f"0:{str(math.floor(start_time))} {title}\n"

        start_time += duration
        tot_dur += clip.duration
        
    print(colored(f"[+] Chapter generated!\n{chapter}", "green"))
    print(colored("[+] Combining video from images success!", "green"))
    
    return concatenate_videoclips(image_clip_list)
    

    
def get_foreground(video_type: str, max_duration: int, subject: str) -> ImageClip:
    positionImageTop = ("center","top") if is_short_video_type(video_type) else ("center","center")
    return ImageClip(f"../templates/{video_type}/foreground/bitcoin.png").set_duration(max_duration).set_position(positionImageTop)

def get_ad(max_duration: int) -> ImageClip:
    position = (1080,1200)
    return ImageClip("../templates/short/ad/politica.png").set_duration(max_duration).set_position(position)




margin_left = 52

width_text_clip_without_margin = SHORT_VIDEO_WIDTH - (2 * margin_left)
width_text_clip_without_margin_long = LONG_VIDEO_WIDTH - (2 * margin_left)

def get_title(is_short_video, titles_path):
    
    margint_top = SHORT_MARGIN_TOP + 180 if is_short_video else LONG_MARGIN_TOP
    
    generator_title_dynamic = lambda txt: TextClip(
        txt,
        font="../fonts/bebas_neue.ttf",
        fontsize=50,
        color = "white",
        align="Center",
        method="caption",
        size=(width_text_clip_without_margin if is_short_video else width_text_clip_without_margin_long, None),
    )

    clip = SubtitlesClip(titles_path, generator_title_dynamic).set_position((margin_left, margint_top))
    clip = fadein(clip, 0.2)
    
    return clip

def get_description(is_short_video, description_path) -> SubtitlesClip:
    generator_description = lambda txt: TextClip(
            txt,
            font="../fonts/source_code.ttf",
            fontsize=38,
            color="white",
            align="West",
            method="caption",
            size=(width_text_clip_without_margin if is_short_video else width_text_clip_without_margin_long, None),
        )
    
    margin_top_description = SHORT_MARGIN_TOP + 520 if is_short_video else LONG_MARGIN_TOP + 290
    
    clip = SubtitlesClip(description_path, generator_description).set_position((margin_left, margin_top_description))
    
    clip = fadein(clip, 0.2)
    
    return clip



def get_subtitle(subtitles_path):
    generator_subtitle = lambda txt: TextClip(
        txt,
        font="../fonts/bebas_neue.ttf",
        fontsize=120,
        color="white",
        align="Center",
        method="caption",
        size=(1080, None),
    )
    
    return SubtitlesClip(subtitles_path, generator_subtitle, encoding='utf-8').set_position((0, SHORT_MARGIN_TOP))

def get_subtitle_line(is_short_video: bool, max_duration, text_color):
    generatorLine = lambda txt: TextClip(
            txt,
            font="../fonts/bebas_neue.ttf",
            fontsize=100,
            color=text_color,
            align="Center",
            method="caption",
            size=(1080 if is_short_video else 1920, None),
        )
    
    subsLine = [((0, max_duration), '____________')]

    return SubtitlesClip(subsLine, generatorLine).set_position((0, SHORT_MARGIN_TOP + 48 if is_short_video else LONG_MARGIN_TOP + 24))

def get_center_line(is_short_video: bool, max_duration, text_color):
    
    line = '_________________________________'
    font_size = 100 if is_short_video else 40
    
    generatorLine = lambda txt: TextClip(
            txt,
            fontsize=font_size,
            color=text_color,
            align="Center",
            stroke_width = 70,
            stroke_color = text_color
        )
    
    if(not is_short_video):
        line = line + '_______________________________________________________'
    
    subsLine = [((0, max_duration), line)]

    return SubtitlesClip(subsLine, generatorLine).set_position((-50, SHORT_MARGIN_TOP + 250 if is_short_video else LONG_MARGIN_TOP + 94))

center_text_size = 52

def get_bottom_center_line(is_short_video: bool, max_duration, text_color):
    
    color = "white"
    line = '_________________________________'
    font_size = 100 if is_short_video else 40
    
    generatorLine = lambda txt: TextClip(
            txt,
            fontsize=font_size,
            color=color,
            align="Center",
            stroke_width = center_text_size,
            stroke_color = color
        )
    
    
    
    if(not is_short_video):
        line = line + '_______________________________________________________'
    
    subsLine = [((0, max_duration), line)]

    return SubtitlesClip(subsLine, generatorLine).set_position((-50, SHORT_MARGIN_TOP + 328 if is_short_video else LONG_MARGIN_TOP + 164))



def get_title_scroll(max_duration: int, video_type: str, title_list: list[str], is_short_video):
    bullet = '   •   '
    position_top = 1090 if is_short_video else LONG_MARGIN_TOP + 144
    
    text = ''
    text += 'INSCREVA-SE PARA RECEBER VÍDEOS NOVOS TODOS OS DIAS' + bullet
    text += 'COMPARTILHE NO WHATSAPP' + bullet
    text += 'INSCREVA-SE PARA RECEBER VÍDEOS NOVOS TODOS OS DIAS' + bullet
    text += 'COMPARTILHE NO WHATSAPP' + bullet
    text += bullet.join(title_list) + bullet
    text += bullet.join(title_list) + bullet
    text_color = 'white'
    text_size = center_text_size
    speed = 10
    
    text_clip = TextClip(text, fontsize=text_size, color=text_color, font="../fonts/bebas_neue.ttf")
    text_clip = text_clip.set_position(lambda t: (int(SHORT_VIDEO_WIDTH * (1 - t / speed)), position_top))
    text_clip = text_clip.set_duration(max_duration)

    return text_clip

def get_bottom_gif(duration):
    gif = VideoFileClip("../templates/images/gifs/2.gif").resize((250,250))
    gif = gif.loop(duration=duration)
    gif = gif.set_position((800, 1600))
    
    return gif

def get_end_subscribe_gif(duration):
    gif = VideoFileClip("../templates/images/gifs/subscribe_end4.gif")
    gif = gif.set_start(duration).set_duration(6)
    gif = gif.set_position(lambda t: ('center', 800+t))
    
    return gif

def get_follow_center_subscribe_gif(duration, is_short_video):
    top = SHORT_MARGIN_TOP + 436 if is_short_video else LONG_MARGIN_TOP + 208
    gif = VideoFileClip("../templates/images/gifs/follow4.gif")
    gif = gif.resize(height=center_text_size)
    gif = gif.loop(duration=duration)
    gif = gif.set_position((44, top))
    
    return gif

def get_over_top_image_gif(duration, is_short_video):
    
    top_image_width = SHORT_VIDEO_WIDTH + 100 if is_short_video else LONG_VIDEO_WIDTH + 600
    
    vintage_clip = VideoFileClip("../templates/images/gifs/vintage_croma5.mp4", has_mask=True, audio=False).set_position(positionImageTop, relative=True).resize(width=top_image_width)
    
    if(is_short_video):
        vintage_clip = vintage_clip.resize(height=1300)
        
    vintage_clip = vintage_clip.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)

    vintage_clip = vintage_clip.loop(duration=duration)
 
    return vintage_clip

def get_compose_video_clip(video_type: str, image_paths, titles, sentences, audio_clips, max_duration: int, description_path: list, titles_path: list, subtitles_path: str,  text_color : str, subject: str):
    
    try:
        is_short_video = is_short_video_type(video_type)
        video_for_base = get_base_video(max_duration, video_type, subject)
        image_for_base = get_base_image(max_duration, video_type, subject)
        
        concatene_images = get_concatene_images(is_short_video, image_paths, titles, sentences, audio_clips)
        #over_top_image_gif = get_over_top_image_gif(max_duration, is_short_video)
        #ad = get_ad(max_duration)
        foreground = get_foreground(video_type, max_duration, subject)
        concatened_title = get_title(is_short_video, titles_path)
        concatened_description = get_description(is_short_video, description_path)
        center_line = get_center_line(is_short_video, max_duration, text_color)
        
        
        bottom_center_line_follow_gif = get_bottom_center_line(is_short_video, max_duration, text_color)
        follow_center_subscribe_gif = get_follow_center_subscribe_gif(max_duration, is_short_video)
        
        title_scroll = get_title_scroll(max_duration, video_type, titles, is_short_video)
        end_subscribe_gif = get_end_subscribe_gif(max_duration)
        
        composite_videos = [
                video_for_base,
                image_for_base,
                concatene_images,
                #over_top_image_gif,
                foreground,
                concatened_title,
                center_line,
                concatened_description,
                title_scroll,
                bottom_center_line_follow_gif,
                follow_center_subscribe_gif,
                end_subscribe_gif
            ]
        
        if(is_short_video):
            subtitles = get_subtitle(subtitles_path)
            subtitleLine = get_subtitle_line(is_short_video, max_duration, text_color)
            bottom_gif = get_bottom_gif(max_duration)
            composite_videos.append(subtitles)
            composite_videos.append(subtitleLine)
            composite_videos.append(bottom_gif)

        return CompositeVideoClip(composite_videos)
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(colored(f"[-] Error get_compose_video_clip to generating {video_type} video: {e} {exc_type} {fname} {exc_tb.tb_lineno}", "red"))
    
def get_final_clip(video_type: str, image_paths, titles, sentences, audio_clips, tts_path: str, max_duration: int, description_path: list, titles_path: list, subtitles_path: str,  text_color : str, subject: str):
    final_clip = get_compose_video_clip(video_type, image_paths, titles, sentences, audio_clips, max_duration,description_path,titles_path,subtitles_path,text_color, subject)
    audio = AudioFileClip(tts_path)
    final_clip = final_clip.set_audio(audio)
    
    return final_clip





