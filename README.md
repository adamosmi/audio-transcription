# Audio conversion command for pyannote.audio
```bash
ffmpeg -i input.m4a -acodec pcm_s16le -ar 44100 -ac 2 output.wav
```
Here's what each part of the command does:

-i input.m4a: Specifies the input file.
-acodec pcm_s16le: Sets the audio codec to PCM signed 16-bit little-endian, which is a common format for WAV files.
-ar 44100: Sets the audio sampling rate to 44.1 kHz, which is standard for CD audio.
-ac 2: Sets the number of audio channels to 2 for stereo sound. You can change this to 1 for mono.
output.wav: Specifies the output file name.

Why?
PCM signed 16-bit little-endian (pcm_s16le codec) is a widely supported audio format that pyannote.audio can process.
A sample rate of 44.1 kHz (-ar 44100) is standard for audio processing and should be compatible with most tools, including pyannote.audio.
Stereo (-ac 2) or mono (-ac 1) channels are both acceptable, though the specific requirement might depend on your task or dataset. For many audio processing tasks, mono is preferred to reduce file size and complexity unless channel information is crucial to your analysis.

