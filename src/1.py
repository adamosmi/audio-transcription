import os
from dotenv import load_dotenv
from datetime import datetime
from pyannote.audio import Pipeline
import torch
from pydub import AudioSegment
import json
import openai

dotenv_path = os.path.join('config', '.env')
load_dotenv(dotenv_path=dotenv_path)

# env vars
HF_ACCESS_TOKEN = os.getenv('HF_ACCESS_TOKEN')
OPENAI_KEY = os.getenv("OPENAI_KEY")

# file paths
AUDIO_FP = os.path.join("data", "external", "transcription_test.wav")
OUTPUT_FP = os.path.join("data", "processed", datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
os.makedirs(OUTPUT_FP, exist_ok=True)

# start diarization pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HF_ACCESS_TOKEN)

# send pipeline to GPU (when available)
pipeline.to(torch.device("cuda"))

# apply pretrained pipeline
diarization = pipeline(AUDIO_FP)

diarization_results = []
# print the result
for turn, _, speaker in diarization.itertracks(yield_label=True):
    diarization_results.append({"start": turn.start, "stop": turn.end, "speaker": speaker})
    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")

# load the original audio file for segmenting
original_audio = AudioSegment.from_file(AUDIO_FP)

# process each segment
for i, segment_info in enumerate(diarization_results):
    # convert start and stop times to milliseconds
    start_ms = segment_info["start"] * 1000 // 1 # take floor
    stop_ms = (segment_info["stop"] * 1000 // 1) + 1 # take ceiling
    
    # extract the segment
    segment = original_audio[start_ms:stop_ms]
    
    # optionally, save the segment to a new file
    segment.export(os.path.join(OUTPUT_FP, f"segment_{i}_{segment_info['speaker']}.wav"), format="wav")

    # print confirmation
    print(f"Segment {i} for {segment_info['speaker']} saved.")

# save json
with open(os.path.join(OUTPUT_FP, 'diarization.json'), 'w') as f:
    json.dump(obj=diarization_results, fp=f)

# run transcriptions with openai whisper
for file in os.listdir(OUTPUT_FP):
    if file == 'diarization.json':
        continue
    print(file)

# openai client
client = openai.OpenAI(api_key=OPENAI_KEY)



