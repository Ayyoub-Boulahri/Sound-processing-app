import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft, fftfreq
from scipy.signal import butter, lfilter
import sounddevice as sd
from scipy.signal import resample
from scipy.io.wavfile import write, read


class Sound:
    def __init__(self , duration , fe = 48000):
        self.duration = duration
        self.fe = fe
        self.N = self.fe * self.duration
        self.t = np.arange(0, self.duration, 1/self.fe)
        self.freqs = fftfreq(self.N, 1/self.fe)
        self.audio = None
        self.filtredSound = None
        self.filtredSpectrum = None
        self.spectrum = None

    def record(self):
        print("Recording !!!")
        self.audio = sd.rec(int(self.duration * self.fe), samplerate=self.fe,
               channels=1, dtype='float32', device=8)
        self.filtredSound = self.audio

        sd.wait()
        print("Finished !!!")
        self.spectrum = abs(fft(self.audio[:, 0]))
        self.filtredSpectrum = self.spectrum

    def set_audio(self,audio):
        self.audio = audio
        self.spectrum = abs(fft(audio))
        self.filtredSpectrum = abs(fft(audio))
        self.filtredSound = audio
    
    def set_spectrum(self , spectrum):
        self.spectrum = spectrum


    def get_vecteur_temps(self):
        return self.t
    
    def get_vecteur_temps_spectre(self):
        if self.filtredSound is not None:
            return np.arange(0 , self.filtredSound.size / self.fe , 1/self.fe)
        return self.filtredSound

    def get_vecteur_freqs(self):
        return fftfreq(self.filtredSound.size , 1/self.fe)
        
    def get_audio(self):
        return self.audio
    
    def get_spectrum(self):
        return self.spectrum
    
    def get_filtred_sound(self):
        return self.filtredSound
    
    def get_filtred_spectrum(self):
        return self.filtredSpectrum
    
    def get_duration(self):
        return self.duration
    
    def hear_voice(self, isFiltred, stop_event=None, block_size=1024):
        if self.audio is None:
            print("record audio first !!")
            return
        audio = self.filtredSound

        if audio.ndim == 1:
            audio = audio[:, np.newaxis]

        audio = audio.astype(np.float32)

        stream = sd.OutputStream(samplerate=self.fe, channels=audio.shape[1], blocksize=block_size)
        stream.start()

        start = 0
        while start < len(audio):
            if stop_event is not None and stop_event.is_set():
                print("Playback stopped!")
                break
            end = min(start + block_size, len(audio))
            stream.write(audio[start:end])
            start = end

        stream.stop()
        stream.close()

    
    def temp(self):
        lowcut, highcut = 400, self.fe
        mask = (np.abs(self.freqs) > 600) & (np.abs(self.freqs) < 2000)
        self.filtredSpectrum = self.spectrum * mask
        self.filtredSound =  np.real(ifft(self.filtredSpectrum))

    def filtre_passBas(self , Wc , ordre):
        if self.audio is None:
            print("record the audio first")
        else :
            print(Wc)
            b, a = butter(ordre, Wc, btype='low', fs=self.fe)
            self.filtredSound = lfilter(b, a, self.audio[:,0]) 
            self.filtredSpectrum = np.abs(fft(self.filtredSound))

    def distortion(self , gain) :
        if self.audio is None:
            print("record the audio first")
        else :
            self.filtredSound = np.tanh(gain * self.audio)
            self.filtredSpectrum =np.abs(fft(self.filtredSound))

    def filtre_passHaut(self , Wc , ordre):
        if self.audio is None:
            print("record the audio first")
        else :
            b, a = butter(ordre, Wc, btype='high', fs=self.fe)
            self.filtredSound = lfilter(b, a, self.audio[:,0]) 
            self.filtredSpectrum = np.abs(fft(self.filtredSound))

    def echo(self , attenuation , decalage):
        self.filtredSound = np.zeros(self.N)
        for i in range(decalage , self.audio.size):
            self.filtredSound[i] = self.audio[i] + attenuation * self.audio[i - decalage]
        self.filtredSpectrum = np.abs(fft(self.filtredSound))

    def reverbe(self , attenuation , decalage):
        self.filtredSound = np.zeros(self.N)
        for i in range(decalage , self.audio.size):
            self.filtredSound[i] = self.audio[i] + attenuation * self.filtredSound[i - decalage]
        self.filtredSpectrum = np.abs(fft(self.filtredSound))

    def apply_pitch(self, factor):
        n_samples = int(len(self.audio) / factor)
        self.filtredSound = resample(self.audio, n_samples)
        self.filtredSpectrum = abs(fft(self.filtredSound))

    def show_sound(self , isFiltred):
        if self.audio is None:
            print("record audio first !!")
        else:
            fig, (ax1, ax2) = plt.subplots(2, 1)
            fig.suptitle('singals of the sound')
            if not isFiltred:
                ax1.plot(self.t , self.audio)
                ax1.set_ylabel("signal in time")
                ax2.plot(self.freqs , self.spectrum)
                ax2.set_ylabel("spectrum of signal")
                plt.show()
            else :
                if self.filtredSpectrum is None :
                    print("the voice is not filtred yet!!")
                else:
                    ax1.plot(self.t , self.filtredSound)
                    ax1.set_ylabel("signal in time")
                    ax2.plot(self.freqs , self.filtredSpectrum)
                    ax2.set_ylabel("spectrum of signal")
                    plt.show()


    def save_as_wav(self, filename="output.wav"):
        if self.filtredSound is None:
            print("No audio to save!")
            return False
        
        data = self.filtredSound[:, 0] if self.filtredSound.ndim > 1 else self.filtredSound

        data_int16 = np.int16(data / np.max(np.abs(data)) * 32767)
        write(filename, self.fe, data_int16)
        print(f"Audio saved as {filename}")
        return True

    def load(self, filename):
        self.fe, data = read(filename)  
        if data.ndim > 1: 
            data = data[:, 0]

        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32767.0
        else:
            data = data.astype(np.float32)

        self.audio = data

        self.duration = len(self.audio) / self.fe
        self.N = len(self.audio)
        self.t = np.arange(0, self.duration, 1/self.fe)
        self.freqs = fftfreq(self.N, 1/self.fe)

        self.spectrum = np.abs(fft(self.audio))
        self.filtredSound = self.audio
        self.filtredSpectrum = self.spectrum
        print(f"Loaded {filename}: {self.duration:.2f} seconds, {self.fe} Hz")


