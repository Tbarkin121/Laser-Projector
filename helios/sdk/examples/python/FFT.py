import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


#%%
# Constants
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Mono audio
# RATE = 44100  # Sample rate
RATE = 96000  # Sample rate
CHUNK = 1024*4  # Number of audio samples per frame
N_BUCKETS = 32  # Number of frequency buckets


# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Streaming started")

# Prepare the matplotlib plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# FFT plot
x_fft = np.linspace(0, RATE // 2, CHUNK // 2)
line, = ax1.plot(x_fft, np.zeros(CHUNK // 2))
ax1.set_title('FFT Spectrum')
ax1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Amplitude')
ax1.set_xlim(0, RATE // 2)
ax1.set_ylim(0, 100)
ax1.grid('True')

# Energy buckets plot
x_buckets = np.linspace(0, RATE // 2, N_BUCKETS)
bars = ax2.bar(x_buckets, np.zeros(N_BUCKETS), width=RATE / (2 * N_BUCKETS))
ax2.set_title('Energy in Frequency Buckets')
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Energy')
ax2.set_xlim(-2000, RATE // 2)
ax2.set_ylim(0, 1024)
ax2.grid('True')


def update_plot(frame):
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        fft_data = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(fft_data), 1 / RATE)
        mag = np.abs(fft_data)**2 / (CHUNK**2)
        
        y = 2 / CHUNK * np.abs(fft_data[0:CHUNK // 2])
        line.set_ydata(y)  # Update FFT line plot
        
        bucket_width = len(freqs) // 2 // N_BUCKETS
        energy_buckets = np.array([np.sum(mag[i*bucket_width:(i+1)*bucket_width]) for i in range(N_BUCKETS)]) 
        
        for i, bar in enumerate(bars):
            bar.set_height(energy_buckets[i])  # Update energy bucket bar plot
        
        # Optional: Calculate and print the volume (RMS)
        volume = np.sqrt(np.mean(audio_data**2))
        print(f"Volume: {volume:.2f}")
        
    except IOError as e:
        print("Error reading from stream:", e)
        return (line, *bars)
    return (line, *bars)



# Animation function
ani = FuncAnimation(fig, update_plot, blit=True, interval=1, save_count=1000)


try:
    plt.tight_layout()
    plt.show()
    
except KeyboardInterrupt:
    # Handle clean-up on CTRL+C (interrupt)
    print("Streaming stopped")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()

    # Terminate PyAudio
    p.terminate()
    


