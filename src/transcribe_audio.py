import time
import os
from dotenv import load_dotenv
from datetime import datetime
from pyannote.audio import Pipeline
import torch
from pydub import AudioSegment
import openai
import json


start = time.perf_counter()
dotenv_path = os.path.join('config', '.env')
load_dotenv(dotenv_path=dotenv_path)

# env vars
HF_ACCESS_TOKEN = os.getenv('HF_ACCESS_TOKEN')
OPENAI_KEY = os.getenv("OPENAI_KEY")

# file paths
AUDIO_FP = os.path.join('data', 'external', 'youtube', '10_03_2024_14_19_14', 'Murder on the Web: Catfish Gone Wrong! | Mystery & Makeup | Bailey Sarian.mp3')
OUTPUT_FP = os.path.join("data", "processed", datetime.now().strftime("%d_%m_%Y_%H_%M_%S"))
os.makedirs(OUTPUT_FP, exist_ok=True)

print("Running diarization...")
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

print("Segmenting original audio file...")
# load the original audio file for segmenting
original_audio = AudioSegment.from_file(AUDIO_FP)

diarization_results_full = {}

# process each segment
for i, segment_info in enumerate(diarization_results):
    # segment output fp
    SEGMENT_FP = os.path.join(OUTPUT_FP, f"segment_{i}_{segment_info['speaker']}.wav")

    # store id
    diarization_results_full[i] = {'fp': SEGMENT_FP, 'data': segment_info}

    # convert start and stop times to milliseconds
    start_ms = segment_info["start"] * 1000 // 1 # take floor
    stop_ms = (segment_info["stop"] * 1000 // 1) + 1 # take ceiling
    
    # extract the segment
    segment = original_audio[start_ms:stop_ms]
    
    # optionally, save the segment to a new file
    segment.export(SEGMENT_FP, format="wav")

    # print confirmation
    print(f"Segment {i} for {segment_info['speaker']} saved.")

# openai client
client = openai.OpenAI(api_key=OPENAI_KEY)

print("Transcribing...")
for i, res in diarization_results_full.items():
    # transcribe each file
    audio_file = open(res['fp'], "rb")
    updated_res = res.copy()

    try:
        transcription = client.audio.transcriptions.create(
          model="whisper-1", 
          file=audio_file
        )
        updated_res['transcription'] = transcription.text
    except Exception as e:
        updated_res['transcription'] = "ERROR"

    diarization_results_full[i] = updated_res

# save json
with open(os.path.join(OUTPUT_FP, 'analysis.json'), 'w') as f:
    json.dump(obj=diarization_results_full, fp=f)

stop = time.perf_counter()
print(f"Done. Seconds: {stop - start}")
