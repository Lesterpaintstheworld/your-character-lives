import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # Standard sample rate
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "test_output.wav"

p = pyaudio.PyAudio()

device_index = None

# List devices
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"Input Device id {i} - {info['name']}")
        if device_index is None:
            device_index = i

if device_index is None:
    print("No input device found")
    exit()

print(f"Using device {device_index}")

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK)

print("* recording")

frames = []

for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow=False)
    frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"Saved recording to {WAVE_OUTPUT_FILENAME}")

# Playback
import pygame

pygame.mixer.init(frequency=RATE)
pygame.mixer.music.load(WAVE_OUTPUT_FILENAME)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pass

print("Playback finished")
