import os
from datetime import datetime
from pytube import YouTube
import re
import subprocess


VIDEO_URL = 'https://www.youtube.com/watch?v=SDFZwJ_zb0s'
OUTPUT_FP = os.path.join('data', 'external', 'youtube', datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
os.makedirs(OUTPUT_FP, exist_ok=True)

yt = YouTube(VIDEO_URL)
audio_streams = yt.streams.filter(only_audio=True)
# download lowest quality audio stream to minimize file size
stream = audio_streams.order_by('abr').first() # ascending sort on bit rate

stream_name = stream.title
stream_subtype = stream.subtype
stream_bitrate = stream.abr
stream_bitrate_ffmpeg = ''.join(re.findall(pattern=r'\d+', string=stream_bitrate)) + 'k'
output_filename = '.'.join([stream_name, stream_subtype])

stream.download(output_path=OUTPUT_FP, filename=output_filename)

# convert into mp3 using ffmpeg
command = [
    'ffmpeg',
    '-i', os.path.join(OUTPUT_FP, output_filename), # input
    '-b:a', stream_bitrate_ffmpeg, # set bitrate to match input
    '-ar', 16000, # 16kHz sample rate for pyannote
    '-ac', 1, # mono channel for pyannote
    os.path.join(OUTPUT_FP, stream_name + '.mp3') 
]

subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


