from observer import Observer
from filtres import Sound
from models import WaveModel
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class View(Observer):
    def __init__(self, parent):
        super().__init__()
        self.sound = np.zeros(200)
        self.parent = parent
        self.gui()

    def gui(self):
        self.parent.title("Waveform Display")

        self.frame = tk.Frame(self.parent, bd=2, relief="groove")

        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self._style_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.draw()

    def layout(self):
        self.frame.pack(fill="both", expand=True)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _style_axes(self):
        self.ax.set_facecolor("#0a1a2f")
        self.ax.tick_params(colors="gray")
        for spine in self.ax.spines.values():
            spine.set_color("gray")

    def draw_spectrum(self, sound, event=None):
        if sound is None:
            return
        t = sound.get_vecteur_temps()
        audio = sound.get_audio()
        self.ax.clear()
        self._style_axes()
        self.ax.plot(t, audio, color="#06b6d4", linestyle="--")
        self.canvas.draw()

    def update(self, subject):
        sound = subject.get_sound()
        t = sound.get_vecteur_temps_spectre()
        audio = sound.get_filtred_sound()
        self.ax.clear()
        self._style_axes()
        if audio is not None:
            self.ax.plot(t, audio, color="#06b6d4", linestyle="--")
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()

    root.option_readfile("main.opt")

    model = WaveModel("test_Model")
    view = View(root)
    view.layout()

    model.attach(view)
    root.mainloop()
