import numpy as np
import sounddevice as sd

def generate_tone(frequency, duration, sampling_rate=44100):
    """Generate a tone of a specific frequency and duration."""
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * frequency * t)

def generate_polyrhythm(frequencies, durations, inter_note_intervals, total_duration, sampling_rate=44100):
    """Generate a polyrhythm from multiple frequencies with specified durations and intervals."""
    # Initialize an empty array for the final mix
    mix = np.zeros(int(sampling_rate * total_duration))
    
    for frequency, duration, interval in zip(frequencies, durations, inter_note_intervals):
        note_count = int(total_duration // (duration + interval))
        rhythm = np.concatenate([np.concatenate([generate_tone(frequency, duration), np.zeros(int(sampling_rate * interval))]) for _ in range(note_count)])
        mix[:len(rhythm)] += rhythm  # Add the rhythm to the mix
    
    return mix

# Parameters
sampling_rate = 44100
frequencies = np.array([261.63, 293.66, 329.63, 349.23, 392.00, 440.0, 493.88])  # Frequencies for each rhythm
# frequencies = frequencies/2

durations = np.ones(7)*0.05  # Duration of each note
# inter_note_intervals = [0.1, 0.2, 0.25, 0.3]  # Time between notes
inter_note_intervals = (np.arange(7)+1)/4

total_duration = 10  # Total duration of the polyrhythm

# Generate the polyrhythm
polyrhythm = generate_polyrhythm(frequencies, durations, inter_note_intervals, total_duration)

# Play the polyrhythm
sd.play(polyrhythm, sampling_rate)

# Wait for it to finish playing
sd.wait()
