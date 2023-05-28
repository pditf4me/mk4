import re
import os
import pickle
import subprocess
from lib.utils import print_red
from lib.config import config


def match_and_load(var, str, file_name='subData.pkl'):
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



# Check if the file has subtitles
def has_subtitles(filename: str) -> None:
    print(f"    ⌛️ Checking if file: \033[33m" + filename + "\033[0m has subtitles ...")
    result = subprocess.run(["ffmpeg", "-i", filename], capture_output=True, text=True)

    # Check if the file contains srts
    return "Subtitle:" in result.stderr or "subtitle:" in result.stdout

# Extract the srt file from the mkv file
def extract_srt(filename: str, subtitle_file: str) -> None:
    try:
        print(f"    ⌛️ Extracting srt from \033[33m" + filename + "\033[0m ...")

        # check all the subtitles in the mkv file
        result = subprocess.run(["ffmpeg", "-i", filename], capture_output=True, text=True)
        subtitles = [line for line in result.stderr.splitlines() if "Subtitle:" in line or "subtitle:" in line]

        # if there is more than one subtitle, ask the user which one to use for the mp4 video
        if len(subtitles) > 1:
            print(f"    ⌛️ \033[33m" + filename + "\033[0m has multiple subtitles, please select the one you want to use:")
            # get the subtitles list
            subtitles = [line for line in result.stderr.splitlines() if "Subtitle:" in line or "subtitle:" in line]
            print("Bypass subtitle selection:")
            print(not bypassCheck(os.path.dirname(filename)))
            if bypassCheck(os.path.dirname(filename)):
                # print the subtitles list
                for i, line in enumerate(subtitles):
                    parts = line.split(':')
                    language = parts[1].strip()
                    languages = language.split('(')
                    code = languages[1][:-1].upper()
                    stream = f"({code}): {parts[2]}: {parts[3]}"
                    print(f"            \033[33m{i}\033[0m: {stream}")

                # ask the user to select the subtitle
                while True:
                    try:
                        selected_subtitle = int(input("    Please select the subtitle you want to use: "))
                        if selected_subtitle < 0 or selected_subtitle >= len(subtitles):
                            print_red("    ❌ Please select a valid subtitle")
                        else:
                            selected_subtitle = match_and_load(selected_subtitle, os.path.dirname(filename))
                            break
                    except ValueError:
                        print_red("    ❌ Please select a valid subtitle")

            else:
                selected_subtitle = 0
                selected_subtitle = match_and_load(selected_subtitle, os.path.dirname(filename))
            # extract the selected subtitle
            subprocess.run([
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel", "error",
                "-i", filename,
                "-c", "srt",
                "-map", "0:s:" + str(selected_subtitle),
                subtitle_file
            ])
        else:
            subprocess.run([
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel", "error",
                    "-i", filename,
                    "-c", "srt",
                    "-map", "0:s:0",
                    subtitle_file
            ])
    except Exception as e:
        print_red("    ❌ Failed to extract srt from: " + filename)
        print_red("    ❌ Error: " + str(e))
        exit(1)

# Beautify the srt file by adding font balises
def beautify_srt(filename: str) -> None:
    try:
        print(f"    ⌛️ Beautifying subtitles: \033[33m" + filename + "\033[0m ...")
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        formatted_lines = []
        line_num = 0

        # Add font balises to the srt file
        while line_num < len(lines):
            # Check if the line is a number (subtitle number)
            if lines[line_num].strip().isdigit():
                formatted_lines.append(lines[line_num])
                formatted_lines.append(lines[line_num + 1])
                line_num += 2
                dialog = ''
                # Add the dialog to the formatted line until we reach a new line
                while line_num < len(lines) and lines[line_num] != '\n':
                    dialog += lines[line_num]
                    line_num += 1
                # Add the font balises to the dialog and add it to the formatted lines list
                formatted_line = "<font size=\"{}\" face=\"{}\">{}</font>".format(config['FONT']["Size"], config["FONT"]["Name"], dialog)
                formatted_lines.append(formatted_line)
                formatted_lines.append('\n\n')
            else:
                line_num += 1
        with open(filename, "w", encoding="utf-8") as f:
            # Write the formatted lines to the srt file
            for line in formatted_lines:
                f.write(line)

        print(f"    ✅ \033[33m" + filename + "\033[0m has been beautified")
    except Exception as e:
        print_red("    ❌ Failed to beautify the subtitles: " + filename)
        print_red("    ❌ Error: " + str(e))
        exit(1)

# Remove font balises from the srt file
def remove_font_balise(subtitle_file: str) -> None:
    try:
        print(f"    ⌛️ Removing font balises from file: \033[33m" + subtitle_file + "\033[0m ...")
        with open(subtitle_file, "r", encoding="utf-8") as f:
            lines = f.read()

        # Remove font balises from the srt file (if any) to avoid double font balises in the final file
        pattern = r"<font.*?>|</font>"
        lines = re.sub(pattern, "", lines)

        with open(subtitle_file, "w", encoding="utf-8") as f:
            f.write(lines)
        print(f"    ✅ Font balises has been removed from file: \033[33m" + subtitle_file+"\033[0m")
    except Exception as e:
        print_red("    ❌ Failed to remove font balises from subtitles: " + subtitle_file)
        print_red("    ❌ Error: " + str(e))
        exit(1)
