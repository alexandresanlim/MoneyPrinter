import os
from utils import *
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")
# Check if all required environment variables are set
# This must happen before importing video which uses API keys without checking
check_env_vars()

from gpt import *
from video import *
from search import *
from news import *
from uuid import uuid4
from tiktokvoice import *
from flask_cors import CORS
from termcolor import colored
from youtube import upload_video
from googleapiclient.errors import HttpError
from flask import Flask, request, jsonify
import sys
# from moviepy.config import change_settings



# Set environment variables
SESSION_ID = os.getenv("TIKTOK_SESSION_ID")
openai_api_key = os.getenv('OPENAI_API_KEY')
# change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGEMAGICK_BINARY")})

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Constants
HOST = "0.0.0.0"
PORT = 8080
AMOUNT_OF_STOCK_VIDEOS = 5
GENERATING = False


# Generation Endpoint
@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        # Set global variable
        global GENERATING
        GENERATING = True

        # Parse JSON
        data = request.get_json()
        print(colored(data, "blue"))
        paragraph_number = int(data.get('paragraphNumber', 1))  # Default to 1 if not provided
        ai_model = data.get('aiModel')  # Get the AI model selected by the user
        n_threads = data.get('threads')  # Amount of threads to use for video generation
        subtitles_position = data.get('subtitlesPosition')  # Position of the subtitles in the video
        text_color = data.get('color') # Color of subtitle text

        # Get 'useMusic' from the request data and default to False if not provided
        use_music = data.get('useMusic', False)

        # Get 'automateYoutubeUpload' from the request data and default to False if not provided
        automate_youtube_upload = data.get('automateYoutubeUpload', False)

        # Get the ZIP Url of the songs
        songs_zip_url = data.get('zipUrl')
        
        titlesData = data.get('videoTitles')
        
        imagesData = data.get('videoImages')
        
        subject = data.get('videoSubject') #data["videoSubject"]
        
        voice = data["voice"]
        voice_prefix = voice[:2]
        
        # Clean
        clean_dir("../temp/")
        clean_dir("../subtitles/")
        clean_dir("../titles/")
        #clean_dir(f"../video_result/{subject}/long")
        clean_dir(f"../video_result/{subject}/short")

        # Download songs
        if use_music:
            # Downloads a ZIP file containing popular TikTok Songs
            if songs_zip_url:
                fetch_songs(songs_zip_url)
            else:
                # Default to a ZIP file containing popular TikTok Songs
                fetch_songs("https://filebin.net/2avx134kdibc4c3q/drive-download-20240209T180019Z-001.zip")

        # Print little information about the video which is to be generated
        print(colored("[Video to be generated]", "blue"))
        print(colored("   Subject: " + data["videoSubject"], "blue"))
        print(colored("   News: " + data["videoTitles"], "blue"))
        print(colored("   Titles: " + data["videoNews"], "blue"))
        print(colored("   Images: " + data["videoImages"], "blue"))
        print(colored("   Voice: " + voice, "blue"))  # Print the AI model being used
        print(colored("   Voice Prefix: " + voice_prefix, "blue"))  # Print the AI model being used
        print(colored("   AI Model: " + ai_model, "blue"))  # Print the AI model being used
        print(colored("   Custom Prompt: " + data["customPrompt"], "blue"))  # Print the AI model being used
        



        if not GENERATING:
            return jsonify(
                {
                    "status": "error",
                    "message": "Video generation was cancelled.",
                    "data": [],
                }
            )
        
        if not voice:
            print(colored("[!] No voice was selected. Defaulting to \"en_us_001\"", "yellow"))
            voice = "en_us_001"
            voice_prefix = voice[:2]


        data_news = data["videoNews"]
        paragraph_number = len(data_news.split("\n"))
        
        # Generate a script
        script = generate_script_to_news(paragraph_number, data_news)  # Pass the AI model to the script generation
        
         # Split script into sentences
        sentences = script.split("\n")
        titleList = []
        imageList = imagesData.split("\n")
        
        
        sentences = [string.replace("\n", "") for string in sentences]
        sentences = [string.strip() for string in sentences]
        sentences = list(filter(lambda x: x != "", sentences))
        titlesData = titlesData.replace("\n", "")
   
        imageList = [string.replace("\n", "") for string in imageList]
        imageList = list(filter(lambda x: x != "", imageList))
        
        lenght = len(sentences)
        
        for i in range(lenght):
            titleList.append(titlesData)
            
        

        
        
        print(colored(f"[+] Generating video", "green"))
        
        # Generate search terms
        # search_terms = get_news(
        #     data["videoSubject"], paragraph_number, script, ai_model
        # )

        # Search for a video of the given search term
        video_urls = []

        # Defines how many results it should query and search through
        it = 15

        # Defines the minimum duration of each clip
        min_dur = 10

        # Loop through all search terms,
        # and search for a video of the given search term
        # for search_term in search_terms:
        #     if not GENERATING:
        #         return jsonify(
        #             {
        #                 "status": "error",
        #                 "message": "Video generation was cancelled.",
        #                 "data": [],
        #             }
        #         )
        #     found_urls = search_for_stock_videos(
        #         search_term, os.getenv("PEXELS_API_KEY"), it, min_dur
        #     )
        #     # Check for duplicates
        #     for url in found_urls:
        #         if url not in video_urls:
        #             video_urls.append(url)
        #             break

        # # Check if video_urls is empty
        # if not video_urls:
        #     print(colored("[-] No videos found to download.", "red"))
        #     return jsonify(
        #         {
        #             "status": "error",
        #             "message": "No videos found to download.",
        #             "data": [],
        #         }
        #     )
            
        # Define video_paths
        video_paths = []
        
        # for search_term in search_terms:
        #     print(colored(f"[+] Set video to {search_term}", "yellow"))
        video_paths.append(f"../templates/{subject}.mp4")

        # Let user know
        #print(colored(f"[+] Downloading {len(video_urls)} videos...", "blue"))

        # Save the videos
        # for video_url in video_urls:
        #     if not GENERATING:
        #         return jsonify(
        #             {
        #                 "status": "error",
        #                 "message": "Video generation was cancelled.",
        #                 "data": [],
        #             }
        #         )
        #     try:
        #         saved_video_path = save_video(video_url)
        #         video_paths.append(saved_video_path)
        #     except Exception:
        #         print(colored(f"[-] Could not download video: {video_url}", "red"))

        # Let user know
        #print(colored("[+] Videos downloaded!", "green"))
        
        print(colored(f"[+] Downloading {len(imageList)} images...", "blue"))
        
        image_paths = []

        #Save the url
        for image_url in imageList:
            if not GENERATING:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Video generation was cancelled.",
                        "data": [],
                    }
                )
            try:
                saved_image_path = save_image(image_url)
                image_paths.append(saved_image_path)
            except Exception:
                print(colored(f"[-] Could not download image: {image_url}", "red"))
                return jsonify(
                {
                    "status": "error",
                    "message": "Invalid image",
                    "data": [],
                })
                
                
        print(colored("[+] Images downloaded!", "green"))

        # Let user know
        print(colored("[+] Script generated!\n", "green"))

        if not GENERATING:
            return jsonify(
                {
                    "status": "error",
                    "message": "Video generation was cancelled.",
                    "data": [],
                }
            )
        
        if(len(imageList) != lenght):
            print(colored(f"[+] Images has invalid lenght: {len(imageList)}! {imageList} and {lenght}\n", "red"))
            return jsonify(
            {
                "status": "error",
                "message": f"Images has invalid lenght: {len(imageList)} and {lenght}!",
                "data": [],
            }
        )
        
        if(len(sentences) != lenght):
            print(colored(f"[+] Sentence has invalid lenght: {len(sentences)}! {sentences} and {lenght}\n", "red"))
            return jsonify(
            {
                "status": "error",
                "message": f"Sentence has invalid lenght: {len(sentences)} and {lenght}!",
                "data": [],
            })
        
        paths = []

        # Generate TTS for every sentence
        for sentence in sentences:
            if not GENERATING:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Video generation was cancelled.",
                        "data": [],
                    }
                )
                
            current_tts_path = f"../temp/{uuid4()}.mp3"
            tts(sentence, voice, filename=current_tts_path)
            audio_clip = AudioFileClip(current_tts_path)
            paths.append(audio_clip)
            print(colored(f"[*] sentence: {sentence}", "blue"))
            # try:
            #     title_path = generate_titles(audio_path=current_tts_path, sentences=sentence, audio_clips=paths, voice=voice_prefix)
            # except Exception as e:
            #     print(colored(f"[-] Error generating subtitles: {e}", "red"))
            #     title_path = None

        # Combine all TTS files using moviepy
        final_audio = concatenate_audioclips(paths)
        tts_path = f"../temp/{uuid4()}.mp3"
        final_audio.write_audiofile(tts_path)
        
        
        print(colored(f"[⚠️] titles: {titleList}", "blue"))
        print(colored(f"[⚠️] descriptions: {sentences}", "blue"))
        
        try:
            titles_path = generate_titles_locally(sentences=titleList, audio_clips=paths)
        except Exception as e:
            print(colored(f"[-] Error generating titles: {e}", "red"))
            titles_path = None

        try:
            subtitles_path = generate_subtitles(audio_path=tts_path, sentences=sentences, audio_clips=paths, voice=voice_prefix)
        except Exception as e:
            print(colored(f"[-] Error generating subtitles: {e}", "red"))
            subtitles_path = None
            
        try:
            description_path = generate_description_locally(sentences, audio_clips=paths)
        except Exception as e:
            print(colored(f"[-] Error generating description: {e}", "red"))
            description_path = None

        # Concatenate videos
        temp_audio = AudioFileClip(tts_path)
        
        video_types = []
        
        video_types.append('short')
        #video_types.append('long')
        
        for video_type in video_types:
            print(colored(f"[+] Generaring {video_type} video...", "blue"))
            
            # if(is_short_video_type(video_type)):
            #     titleList = titleList[:3]
            #     image_paths = image_paths[:3]
            #     sentences = sentences[:3]
            #     paths = paths[:3]
            #     titles_path = titles_path[:3]
            #     subtitles_path = subtitles_path[:3]
            
            try:
                final_video_path = generate_video(
                    video_type,
                    image_paths, 
                    titleList, 
                    sentences, 
                    paths, 
                    tts_path, 
                    temp_audio.duration, 
                    description_path, 
                    titles_path, 
                    subtitles_path, 
                    n_threads or 2, 
                    text_color or "#FFFF00",
                    subject
                    )
            
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(colored(f"[-] Error generating final video: {e} {exc_type} {fname} {exc_tb.tb_lineno}", "red"))
                final_video_path = None

            if False:
                # Define metadata for the video, we will display this to the user, and use it for the YouTube upload
                title, description, keywords = generate_metadata(data["videoSubject"], script, ai_model)

                print(colored("[-] Metadata for YouTube upload:", "blue"))
                print(colored("   Title: ", "blue"))
                print(colored(f"   {title}", "blue"))
                print(colored("   Description: ", "blue"))
                print(colored(f"   {description}", "blue"))
                print(colored("   Keywords: ", "blue"))
                print(colored(f"  {', '.join(keywords)}", "blue"))

            if automate_youtube_upload:
                # Start Youtube Uploader
                # Check if the CLIENT_SECRETS_FILE exists
                client_secrets_file = os.path.abspath("./client_secret.json")
                SKIP_YT_UPLOAD = False
                if not os.path.exists(client_secrets_file):
                    SKIP_YT_UPLOAD = True
                    print(colored("[-] Client secrets file missing. YouTube upload will be skipped.", "yellow"))
                    print(colored("[-] Please download the client_secret.json from Google Cloud Platform and store this inside the /Backend directory.", "red"))

                # Only proceed with YouTube upload if the toggle is True  and client_secret.json exists.
                if not SKIP_YT_UPLOAD:
                    # Choose the appropriate category ID for your videos
                    video_category_id = "28"  # Science & Technology
                    privacyStatus = "private"  # "public", "private", "unlisted"
                    video_metadata = {
                        'video_path': os.path.abspath(f"../temp/{final_video_path}"),
                        'title': title,
                        'description': description,
                        'category': video_category_id,
                        'keywords': ",".join(keywords),
                        'privacyStatus': privacyStatus,
                    }

                    # Upload the video to YouTube
                    try:
                        # Unpack the video_metadata dictionary into individual arguments
                        video_response = upload_video(
                            video_path=video_metadata['video_path'],
                            title=video_metadata['title'],
                            description=video_metadata['description'],
                            category=video_metadata['category'],
                            keywords=video_metadata['keywords'],
                            privacy_status=video_metadata['privacyStatus']
                        )
                        print(f"Uploaded video ID: {video_response.get('id')}")
                    except HttpError as e:
                        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")

            video_clip = VideoFileClip(f"../temp/{final_video_path}")
            
            if use_music:
                # Select a random song
                song_path = choose_random_song()

                # Add song to video at 30% volume using moviepy
                original_duration = video_clip.duration
                original_audio = video_clip.audio
                song_clip = AudioFileClip(song_path).set_fps(44100)

                # Set the volume of the song to 10% of the original volume
                song_clip = song_clip.volumex(0.1).set_fps(44100)

                # Add the song to the video
                comp_audio = CompositeAudioClip([original_audio, song_clip])
                video_clip = video_clip.set_audio(comp_audio)
                video_clip = video_clip.set_fps(30)
                video_clip = video_clip.set_duration(original_duration)
                video_clip.write_videofile(f"../video_result/{subject}/{video_type}/{final_video_path}", threads=n_threads or 1)
            else:
                video_clip.write_videofile(f"../video_result/{subject}/{video_type}/{final_video_path}", threads=n_threads or 1)


            # Let user know
            print(colored(f"[🎉] {video_type} video of {subject} generated: {final_video_path}!", "green"))

            # Stop FFMPEG processes
            if os.name == "nt":
                # Windows
                os.system("taskkill /f /im ffmpeg.exe")
            else:
                # Other OS
                os.system("pkill -f ffmpeg")

            GENERATING = False

        # Return JSON
        return jsonify(
            {
                "status": "success",
                "message": f"Video generated! See for result.",
                "data": final_video_path,
            }
        )
        
    except Exception as err:
        print(colored(f"[-] Error: {str(err)}", "red"))
        return jsonify(
            {
                "status": "error",
                "message": f"Could not retrieve stock videos: {str(err)}",
                "data": [],
            }
        )


@app.route("/api/cancel", methods=["POST"])
def cancel():
    print(colored("[!] Received cancellation request...", "yellow"))

    global GENERATING
    GENERATING = False

    return jsonify({"status": "success", "message": "Cancelled video generation."})

@app.route("/api/getnews", methods=["POST"])
def getnews():
    print(colored("[!] Received get news request...", "yellow"))
    
    data = request.get_json()
    
    print(colored(f"{data}", "yellow"))
    
    subject = data["videoSubject"]
    voice = data["voice"]
    voice_prefix = voice[:2]
    
    language = 'pt' if voice_prefix == 'br' else 'en'
    
   
    
    found_news = search_news(subject, os.getenv('GNEWS_API_KEY'), language=language)
    
    
    titles = found_news[0]
    sentences = found_news[1]
    images = found_news[2]

    

    return jsonify({"status": "success", "message": "News was filled.", "titles": titles, "sentences": sentences, "images": images})

if __name__ == "__main__":

    # Run Flask App
    app.run(debug=True, host=HOST, port=PORT)
