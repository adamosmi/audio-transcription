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
# download highest quality audio stream
stream = audio_streams.order_by('abr').last() # ascending sort on bit rate, last is best

stream_name = stream.title
stream_subtype = stream.subtype
stream_bitrate = stream.abr
stream_bitrate_ffmpeg = ''.join(re.findall(pattern=r'\d+', string=stream_bitrate)) + 'k'
output_filename = '.'.join([stream_name, stream_subtype])

stream.download(output_path=OUTPUT_FP, filename=output_filename)

# convert into wav using ffmpeg
# ffmpeg -i input_file.wav -acodec pcm_s16le -ac 1 -ar 16000 -ab 256k output_file.wav
command = [
    'ffmpeg',
    '-i', os.path.join(OUTPUT_FP, output_filename), # input
    '-acodec', 'pcm_s16le' # wav codec
    '-ac', '1', # mono channel for pyannote
    '-ar', '16000', # 16kHz sample rate for pyannote
    '-ab', '256k', # set bitrate
    os.path.join(OUTPUT_FP, stream_name + '.wav') 
]

subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


