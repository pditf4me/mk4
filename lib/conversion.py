# Convert the mkv file to mp4 with the beautified srt file and select the audio track
import os
import pickle
from pathlib import Path
import subprocess
from lib.subtitles import beautify_srt, extract_srt, has_subtitles, remove_font_balise
from lib.utils import delete_mkv, get_file_name, get_subtitle_file, print_red
from lib.config import config


def match_and_load(var, str, file_name='audioData.pkl'):
    if os.path.exists(file_name):
        # Load the previously saved data
        with open(file_name, 'rb') as f:
            saved_var, saved_str = pickle.load(f)

        # Check if the saved string matches the new string
        if saved_str == str:
            # If the strings match, return the saved variable
            return saved_var
        else:
            # If the strings do not match, save the new variable and string
            with open(file_name, 'wb') as f:
                pickle.dump((var, str), f)
            return var
    else:
        # If no saved data exists, save the new variable and string
        with open(file_name, 'wb') as f:
            pickle.dump((var, str), f)
        return var


def bypassCheck(str, file_name='audioData.pkl'):
    if os.path.exists(file_name):
        # Load the previously saved data
        with open(file_name, 'rb') as f:
            saved_var, saved_str = pickle.load(f)
        
        # Check if the saved string matches the new string
        if saved_str == str:
            # If the strings match, return the saved variable
            return False
        else:
            # If the directory is different from saved
            return True
    return True



def convert_file(filename: str, subtitles: str) -> None:
    try:
        print(f"    ⌛️ Converting file: \033[33m" + filename + "\033[0m to mp4 ...")
        print("Bypass audio selection:")
        print(not bypassCheck(os.path.dirname(filename)))
        if bypassCheck(os.path.dirname(filename)):
            # check if the mkv file have multiple audio tracks and ask the user which one to use
            result = subprocess.run(["ffmpeg", "-i", filename], capture_output=True, text=True)
            audio_tracks = [line for line in result.stderr.splitlines() if "Audio:" in line or "audio:" in line]
            if len(audio_tracks) > 1:
                print(f"    ⌛️ \033[33m" + filename + "\033[0m has multiple audio tracks, please select the one you want to use: ")
                for i, line in enumerate(audio_tracks):
                    print(f"            \033[33m{i}\033[0m: {line}")
                while True:
                    try:
                        selected_audio_track = int(input("    Please select the audio track you want to use: "))
                        if selected_audio_track < 0 or selected_audio_track >= len(audio_tracks):
                            print_red("    ❌ Please select a valid audio track")
                        else:
                            break
                    except ValueError:
                        print_red("    ❌ Please select a valid audio track")
                audio_track = "0:a:" + str(selected_audio_track)
            else:
                audio_track = "0:a:0"
        else:
            audio_track = "0:a:0"
        audio_track = match_and_load(audio_track, os.path.dirname(filename))
        
        output = Path(get_file_name(filename) + "-mk4.mp4")
        
        subprocess.run([
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-v", "error",
            "-stats",
            "-i", str(filename),
            "-vf", "subtitles=" + subtitles,
            "-c:v", config['FFMPEG']["ENCODER"],
            "-pix_fmt", "yuv420p",
            "-crf", config['FFMPEG']["CRF"],
            "-c:a", "aac",
            "-map", audio_track,
            "-map", "0:v:0",

            # keeping the below lines only for dev mode. please keep them commented
            # "-ss", "00:00:00",
            # "-to", "00:00:20",
            str(output)
        ])
        os.remove(subtitles)
        print(f"    ✅ File: \033[33m" + filename + "\033[0m has been converted")
    except Exception as e:
        print_red("    ❌ Failed to convert file: " + filename)
        print_red("    ❌ Error: " + str(e))
        exit(1)

# process to the conversion from mkv to mp4
def process(filename: str, delete: bool) -> None:
    subtitle_file = get_subtitle_file()

    if not has_subtitles(filename):
        print(f"    ❌ \033[33m" + filename + "\033[0m has no subtitles")
    else:
        try:
            print(f"    ✅ \033[33m" + filename + "\033[0m has subtitles")
            extract_srt(filename, subtitle_file)
            remove_font_balise(subtitle_file)
            beautify_srt(subtitle_file)
            convert_file(filename, subtitle_file)
            if delete:
                delete_mkv(filename)
        except KeyboardInterrupt:
            print_red("    ❌ Conversion cancelled")
            mk4_filename = Path(get_file_name(filename) + "-mk4.mp4")
            if os.path.exists(subtitle_file):
                os.remove(subtitle_file)
            if os.path.exists(mk4_filename):
                os.remove(mk4_filename)
            exit(1)
        except Exception as e:
            print_red("    ❌ Failed to process file: " + filename)
            print_red("    ❌ Error: " + str(e))
            exit(1)