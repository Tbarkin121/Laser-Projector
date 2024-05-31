import pyaudio
import numpy as np

# Constants
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate
CHUNK = 1024  # Number of audio samples per frame

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Streaming started")

# Stream processing loop
try:
    while True:
        data = stream.read(CHUNK)
        # Convert data to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Compute the RMS (root mean square) value for volume
        volume = np.sqrt(np.mean(audio_data**2))
        
        # Example: Update laser intensity based on volume
        # You can map 'volume' to 'intensity' of your laser points
        
        print("Volume:", volume)  # You can replace this with any function that handles volume

except KeyboardInterrupt:
    # Handle clean-up on CTRL+C (interrupt)
    print("Streaming stopped")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate PyAudio
    p.terminate()