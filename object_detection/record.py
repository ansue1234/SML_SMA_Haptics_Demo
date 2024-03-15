import pyaudio
import wave
import assemblyai as aai
import string

class AudioProcessor:
    def __init__(self):
        self.FORMAT = pyaudio.paInt16  # Audio format
        self.CHANNELS = 1  # Number of audio channels
        self.RATE = 44100  # Sample rate
        self.CHUNK = 1024  # Frame size
        self.RECORD_SECONDS = 5  # Duration of recording
        self.WAVE_OUTPUT_FILENAME = "output.wav"  # Output file

    def record_voice_input(self):
        # Initialize pyaudio
        audio = pyaudio.PyAudio()

        # Start recording
        stream = audio.open(format=self.FORMAT, channels=self.CHANNELS,
                            rate=self.RATE, input=True,
                            frames_per_buffer=self.CHUNK)
        print("Recording...")

        frames = []

        # Record data for RECORD_SECONDS
        for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        print("Finished recording.")

        # Stop recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save the recorded data as a WAV file
        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print("saved")

    def transcribe_audio(self):
        # Initialize the transcriber
        aai.settings.api_key = "69b09d7815f0441897026ac1eb78378b"
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe("./output.wav")
        return transcript.text.lower().translate(str.maketrans('', '', string.punctuation))
