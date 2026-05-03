import math

from typing import List
from moviepy.editor import *
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.crop import crop
import moviepy.video.fx.all as vfx
from moviepy.video.fx.make_loopable import make_loopable
from termcolor import colored


from moviepy.video.tools.subtitles import SubtitlesClip
from extensions.string_extension import *
from extensions.urlchecks import *
import numpy as np
from utils import *
from templates.common.masks import *


SHORT_MARGIN_TOP = 722
LONG_MARGIN_TOP = 520

VIDEO_SIZE = 1920
VIDELO_SIZE_2 = 1080

#VIDEO_SIZE = 3840
#VIDELO_SIZE_2 = 2160

SHORT_VIDEO_HEIGHT = VIDEO_SIZE
SHORT_VIDEO_WIDTH = VIDELO_SIZE_2

LONG_VIDEO_HEIGHT = VIDELO_SIZE_2
LONG_VIDEO_WIDTH = VIDEO_SIZE

secounds_for_end_of_video = 6

font_bebeaus_neue = "../fonts/bebas_neue.ttf"



def get_base_video(max_duration: int, video_type: str, subject: str) -> ImageClip:
    
    
    duration = max_duration + secounds_for_end_of_video
    
    video_size = (SHORT_VIDEO_WIDTH, SHORT_VIDEO_HEIGHT) if is_short_video_type(video_type) else (LONG_VIDEO_WIDTH, LONG_VIDEO_HEIGHT)
    
    color_clip = ColorClip(size=video_size, color=(0, 0, 0), duration=duration)
    
    return color_clip

def get_base_image(max_duration: int, video_type: str, subject: str):

    positionImageTop = ("center","top") if is_short_video_type(video_type) else ("center","center")
    clip = ImageClip(f"../templates/{video_type}/base/{subject}/background.png").set_duration(max_duration).set_position(positionImageTop)
    #clip = fadein(clip, 0.2)
    #clip = clip.resize(lambda t: 1 - 0.01 * t)
    
    return clip   

positionImageTop = ("center","top") 

def get_concatene_images(is_short_video: bool, image_paths: List[str], titles: List[str], sentences: List[str], audio_clips: List[AudioFileClip]) -> list:
    
    print(colored(f"[+] Combining video from images: {image_paths}", "blue"))
    
    top_image_width = SHORT_VIDEO_WIDTH + 100 if is_short_video else LONG_VIDEO_WIDTH+600
    tot_dur = 0
    start_time = 0
    
    image_clip_list = []
    chapter = ''
    
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
    return ImageClip(f"../templates/{video_type}/foreground/foreground30.png").set_duration(max_duration).set_position(positionImageTop)

def get_ad(max_duration: int) -> ImageClip:
    position = (1080,1200)
    return ImageClip("../templates/short/ad/politica.png").set_duration(max_duration).set_position(position)


margin_left = 52

width_text_clip_without_margin = SHORT_VIDEO_WIDTH - (2 * margin_left)
width_text_clip_without_margin_long = LONG_VIDEO_WIDTH - (2 * margin_left)
size_comments_and_description = width_text_clip_without_margin - 184

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
            fontsize=32,
            color="white",
            align="West",
            method="caption",
            size=(size_comments_and_description, None),
        )
    
    margin_top_description = SHORT_MARGIN_TOP + 604 if is_short_video else LONG_MARGIN_TOP + 290
    
    clip = SubtitlesClip(description_path, generator_description).set_position((margin_left + 88, margin_top_description))
    
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



def get_title_scroll(max_duration: int, video_type: str, title_list: list[str], is_short_video, head_lines: list):
    bullet = '   •   '
    position_top = 1076 if is_short_video else LONG_MARGIN_TOP + 144
    
    text = ''
    text += bullet.join(head_lines) + bullet
    text += 'INSCREVA-SE PARA RECEBER VÍDEOS NOVOS TODOS OS DIAS' + bullet
    text += 'COMPARTILHE NO WHATSAPP' + bullet
    text_color = 'white'
    text_size = center_text_size
    speed = 7
    
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
    top = SHORT_MARGIN_TOP + 426 if is_short_video else LONG_MARGIN_TOP + 208
    gif = VideoFileClip("../templates/images/gifs/follow4.gif")
    gif = gif.resize(height=center_text_size)
    gif = gif.loop(duration=duration)
    gif = gif.set_position((44, top))
    
    return gif


bar_width_total = SHORT_VIDEO_WIDTH
bar_height = 52
bar_x = (SHORT_VIDEO_WIDTH - bar_width_total) / 2
bar_y = 0

def get_goal_subscribe(subscriber_count: int) -> int:
    if subscriber_count < 1000:
        return 1000
    
    if subscriber_count < 2000:
        return 2000
    
    if subscriber_count < 5000:
        return 5000
    
    if subscriber_count < 10000:
        return 10000
    
    if subscriber_count < 100000:
        return 100000
    
    if subscriber_count < 1000000:
        return 1000000
    
    return 100000000

def get_subscribe_text(duration, stat_channel):
    
    subscriber_count = int(stat_channel["subscriberCount"])
    goal = get_goal_subscribe(subscriber_count)
    
    txt = (TextClip(f"Meta de inscritos ({subscriber_count}/{goal})", 
                    fontsize=32, 
                    color="black",
                    font="../fonts/roboto_bold.ttf")
        .set_position(("center", bar_y + 8))
        .set_duration(duration))
     
    return txt

def get_subscribe_bar_background(duration):
    bar_background = (ColorClip(size=(bar_width_total, bar_height), color=(149, 165, 166))
                    .set_position((bar_x, bar_y))
                    .set_duration(duration))
    
    return bar_background

def get_subscribe_bar_progress(duration, stat_channel):
    
    subscriber_count = int(stat_channel["subscriberCount"])
    goal = get_goal_subscribe(subscriber_count)
    
    progress_ratio = subscriber_count / goal
    bar_width_progress = bar_width_total * progress_ratio
    
    bar_progress = (ColorClip(size=(int(bar_width_progress), bar_height), color=(0, 255, 0))
                    .set_position((bar_x, bar_y))
                    .set_duration(duration))
    
    return bar_progress

def get_progress_bar(duration, is_short_video=True):
    video_width = SHORT_VIDEO_WIDTH if is_short_video else LONG_VIDEO_WIDTH
    bar_height = 4
    
    def make_progress_bar(t):
        frame = np.zeros((bar_height, video_width, 3), dtype=np.uint8)
        progress_width = int((t / duration) * video_width)
        frame[:, :, :] = [50, 50, 50]
        frame[:, :progress_width, :] = [255, 0, 0]
        
        return frame
    
    return VideoClip(make_frame=make_progress_bar, duration=duration)

def get_concatene_progress(is_short_video: bool, audio_clips: List[AudioFileClip]) -> list[VideoClip]:
   
    progress_list = []
    
    for i, audio_clip in enumerate(audio_clips, start=0):
        duration = audio_clip.duration
        
        progress_bar = get_progress_bar(duration=duration, is_short_video=is_short_video)
        
        progress_list.append(progress_bar)
    
    concatenated = concatenate_videoclips(progress_list)
    concatenated = concatenated.set_position(('center', 1062))
    
    return concatenated
    
    

def get_over_top_image_gif(duration, is_short_video):
    
    top_image_width = SHORT_VIDEO_WIDTH + 100 if is_short_video else LONG_VIDEO_WIDTH + 600
    
    vintage_clip = VideoFileClip("../templates/images/gifs/vintage_croma5.mp4", has_mask=True, audio=False).set_position(positionImageTop, relative=True).resize(width=top_image_width)
    
    if(is_short_video):
        vintage_clip = vintage_clip.resize(height=1300)
        
    vintage_clip = vintage_clip.fx(vfx.mask_color, color=[0, 255, 0], thr=100, s=5)

    vintage_clip = vintage_clip.loop(duration=duration)
 
    return vintage_clip


# Configurações
VIDEO_WIDTH = SHORT_VIDEO_WIDTH
VIDEO_HEIGHT = SHORT_VIDEO_HEIGHT
DURATION_PER_COMMENT = 4
PROFILE_IMAGE_SIZE = 76
IMAGE_SIZE = (PROFILE_IMAGE_SIZE, PROFILE_IMAGE_SIZE)
COMMENT_START_ON_TOP = 1232
COMMENT_SIZE = 308
COMMENT_LEFT = 60
COMMENT_TOP_START = 118



def get_comment_img(comment_data):

    clip = ImageClip(comment_data["imagem"]).resize(IMAGE_SIZE).set_duration(DURATION_PER_COMMENT)
    mask = circle_mask(PROFILE_IMAGE_SIZE)

    clip = clip.set_mask(ImageClip(mask, ismask=True))
    #clip = clip.fx(vfx.fadein, 0.2)
    
    return clip

def get_comment_name(comment_data):
    
    name = comment_data["nome"]
    
    clip = TextClip(
        name,
        fontsize=16,
        color="white",
        font="../fonts/roboto_bold.ttf",
    ).set_duration(DURATION_PER_COMMENT)
    
    #clip = fadein(clip, 0.2)
    return clip

def get_comment_sub_name():
    
    text = "Comentou em um vídeo"
    
    clip = TextClip(
        text,
        fontsize=14,
        color="white",
        font="../fonts/roboto_bold.ttf",
    ).set_duration(DURATION_PER_COMMENT)
    
    #clip = fadein(clip, 0.2)
    return clip
    
def get_comment_description(comment_data):
    clip = TextClip(
        comment_data["comentario"],
        fontsize=24,
        color="white",
        stroke_width = 1,
        stroke_color = "white",
        font="../fonts/roboto.ttf",
        size=(362, None),
        align="West",
        method="caption",
    ).set_duration(DURATION_PER_COMMENT)
    
    #clip = fadein(clip, 0.2)
    return clip

    
def get_concatene_comments_img(comments, max_duration):
    
    comment_clips = [get_comment_img(comment) for comment in comments]
    
    concatenated = concatenate_videoclips(comment_clips)
    concatenated = concatenated.set_position((62, 74))
    concatenated = concatenated.set_duration(max_duration)
    
    return concatenated

def get_concatene_comments_name(comments, max_duration):
    
    comment_clips = [get_comment_name(comment) for comment in comments]
    
    concatenated = concatenate_videoclips(comment_clips)
    concatenated = concatenated.set_position((152, 90))
    concatenated = concatenated.set_duration(max_duration)
    
    
    return concatenated

def get_concatene_comments_sub_name(comments, max_duration):
    
    comment_clips = get_comment_sub_name()
    comment_clips = comment_clips.set_position((152, 112))
    comment_clips = comment_clips.set_duration(max_duration)
    
    
    return comment_clips

def get_concatene_comments_description(comments, max_duration):
    
    comment_clips = [get_comment_description(comment) for comment in comments]
    
    concatenated = concatenate_videoclips(comment_clips)
    concatenated = concatenated.set_position((152, 140))
    concatenated = concatenated.set_duration(max_duration)
    
    return concatenated




def get_compose_video_clip(video_type: str, image_paths, titles, sentences, audio_clips, max_duration: int, description_path: list, titles_path: list, subtitles_path: str,  text_color : str, subject: str, comments: list, stat_channel, head_lines: list):
    
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
        
        title_scroll = get_title_scroll(max_duration, video_type, titles, is_short_video, head_lines)
        end_subscribe_gif = get_end_subscribe_gif(max_duration)
        
        subscribe_text = get_subscribe_text(max_duration, stat_channel)
        subscribe_bar_background = get_subscribe_bar_background(max_duration)
        subscribe_bar_progress = get_subscribe_bar_progress(max_duration, stat_channel)
                
        concatene_progress = get_concatene_progress(is_short_video, audio_clips)
        
        comments_img = get_concatene_comments_img(comments, max_duration)
        comments_name = get_concatene_comments_name(comments, max_duration)
        comments_sub_name = get_concatene_comments_sub_name(comments, max_duration)
        comments_description = get_concatene_comments_description(comments, max_duration)
        
        
        
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
                subscribe_bar_background,
                subscribe_bar_progress,
                subscribe_text,
                concatene_progress,
                bottom_center_line_follow_gif,
                follow_center_subscribe_gif,
                comments_img,
                comments_name,
                comments_sub_name,
                comments_description,
                end_subscribe_gif, 
            ]
        
        if(is_short_video):
            subtitles = get_subtitle(subtitles_path)
            subtitleLine = get_subtitle_line(is_short_video, max_duration, text_color)
            #bottom_gif = get_bottom_gif(max_duration)
            composite_videos.extend([subtitles, subtitleLine])

        return CompositeVideoClip(composite_videos)
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(colored(f"[-] Error get_compose_video_clip to generating {video_type} video: {e} {exc_type} {fname} {exc_tb.tb_lineno}", "red"))
        return None
    
def get_final_clip(video_type: str, image_paths, titles, sentences, audio_clips, tts_path: str, max_duration: int, description_path: list, titles_path: list, subtitles_path: str,  text_color : str, subject: str, comments: list, stat_channel, head_lines: list):
    final_clip = get_compose_video_clip(video_type, image_paths, titles, sentences, audio_clips, max_duration,description_path,titles_path,subtitles_path,text_color, subject, comments, stat_channel, head_lines)
    audio = AudioFileClip(tts_path)
    final_clip = final_clip.set_audio(audio)
    
    return final_clip





