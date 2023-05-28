#!/usr/bin/python3
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import sys


file = sys.argv[1]
ffmpeg_extract_subclip(file, 0, 30000, targetname="00000test.mkv")
