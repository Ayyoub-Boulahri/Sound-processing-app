import tkinter as tk
from views import View
from models import WaveModel
from filtres import Sound
import matplotlib.pyplot as plt
import threading

class WaveController:
    def __init__(self, parent, model, view):
        self.parent = parent
        self.model = model
        self.view = view
        self.isFiltred = 0
        self.play_thread = None
        self.stop_event = threading.Event()
        self.gui()
        self.layout()
        self.actions_binding()

    def gui(self):
        self.frame = tk.LabelFrame(self.parent, text="", bd=0, name="main_frame")
        self.title_label = tk.Label(self.frame, text="Voice WORKSTATION PRO",   
                                font=("Arial", 24, "bold"), name="title_label")
        self.subtitle_label = tk.Label(
            self.frame,
            text="Professional Audio Recording • Real-time Effects • Spectrum Analysis",
            font=("Arial", 10), name="subtitle_label"
        )
        self.header = tk.Frame(self.frame, bg="#0891b2", height=40)
        self.title = tk.Label(self.header, text="🎵 WAVEFORM DISPLAY", 
                        bg="#0891b2", fg="white", font=("Arial", 10, "bold"))
        self.btn = tk.Button(self.header, text="SPECTRUM", relief="ridge", font=("Arial", 9))

        self.canvas_frame = tk.Frame(self.parent, name="canvas_frame")
        self.canvas = tk.Canvas(self.canvas_frame, name="canvas")
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview, name="scrollbar")
        self.scrollable_frame = tk.Frame(self.canvas, name="scrollable_frame")

        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.main_frame = tk.Frame(self.scrollable_frame, name="main_content_frame")

        self.voice_rec_frame = tk.Frame(self.main_frame, relief="flat", bd=0, name="voice_rec_frame")
        self.label = tk.Label(
            self.voice_rec_frame, text="🎙 Voice Recorder",
        font=("Arial", 18, "bold"),
             name="voice_rec_label"
        )
        self.button_voice_rec_frame = tk.Frame(self.voice_rec_frame, name="voice_buttons_frame")
        self.record_button = tk.Button(
            self.button_voice_rec_frame, text="⏺ Record", font=("Arial", 12, "bold"), width=10, relief="flat",
            name="record_button"
        )
        self.play_button = tk.Button(
            self.button_voice_rec_frame, text="▶ Play",font=("Arial", 12, "bold"), width=10, relief="flat", name="play_button"
        )
        self.stop_button = tk.Button(
            self.button_voice_rec_frame, text="⏹ Stop",font=("Arial", 12, "bold"), width=10, relief="flat", name="stop_button"
        )

        self.effectsFrame = tk.LabelFrame(self.main_frame, text="🎛️ Effects",    bd=2,
                                        relief="groove", name="effects_frame")
        self.pitch_label = tk.Label(self.effectsFrame, text="PITCH",    font=("Arial", 10, "bold"), name="pitch_label")
        self.pitch = tk.Scale(self.effectsFrame, from_=-15, to=15, orient="horizontal",
                            length=300, sliderlength=20, showvalue=False,   
                            troughcolor="#7f8c8d", sliderrelief="flat", highlightthickness=0, name="pitch_scale")
        self.pitch_value = tk.Label(self.effectsFrame, text="0 semitones",   name="pitch_value")
        self.reverb_label = tk.Label(self.effectsFrame, text="REVERB",  font=("Arial", 10, "bold"), name="reverb_label")
        self.reverb = tk.Scale(self.effectsFrame, from_=0, to=100, orient="horizontal",
                            length=300, sliderlength=20, showvalue=False,   
                            troughcolor="#7f8c8d", sliderrelief="flat", highlightthickness=0, name="reverb_scale")
        self.reverb_value = tk.Label(self.effectsFrame, text="0%",   name="reverb_value")
        self.echo_label = tk.Label(self.effectsFrame, text="ECHO",  font=("Arial", 10, "bold"), name="echo_label")
        self.echo = tk.Scale(self.effectsFrame, from_=0, to=100, orient="horizontal",
                            length=300, sliderlength=20, showvalue=False,   
                            troughcolor="#7f8c8d", sliderrelief="flat", highlightthickness=0, name="echo_scale")
        self.echo_value = tk.Label(self.effectsFrame, text="0%",     name="echo_value")

        self.equalizerFrame = tk.LabelFrame(self.main_frame, text="🎚️ Equalizer",    bd=2,
                                            relief="groove", name="equalizer_frame")
        self.low_label = tk.Label(self.equalizerFrame, text="LOW PASS", font=("Arial", 10, "bold"), name="low_label")
        self.low = tk.Scale(self.equalizerFrame, from_=600, to=1200, orient="horizontal",
                            length=300, sliderlength=20,     troughcolor="#7f8c8d",
                            sliderrelief="flat", highlightthickness=0, name="low_scale")
        self.high_label = tk.Label(self.equalizerFrame, text="HIGH PASS",   font=("Arial", 10, "bold"), name="high_label")
        self.high = tk.Scale(self.equalizerFrame, from_=1200, to=600, orient="horizontal",
                            length=300, sliderlength=20,     troughcolor="#7f8c8d",
                            sliderrelief="flat", highlightthickness=0, name="high_scale")
        self.dist_label = tk.Label(self.equalizerFrame, text="DISTORTION",  font=("Arial", 10, "bold"), name="dist_label")
        self.dist = tk.Scale(self.equalizerFrame, from_=0, to=100, orient="horizontal",
                            length=300, sliderlength=20, showvalue=False,   
                            troughcolor="#7f8c8d", sliderrelief="flat", highlightthickness=0, name="dist_scale")
        self.dist_value = tk.Label(self.equalizerFrame, text="0%",   name="dist_value")

        self.rec_manage_frame = tk.LabelFrame(
            self.scrollable_frame, text="📂 Recording Management",   bd=2, relief="groove", padx=10, pady=10, name="rec_manage_frame"
        )
        self.rec_name_label = tk.Label(
            self.rec_manage_frame, text="Recording Name:",
        font=("Arial", 10, "bold"),
             name="rec_name_label"
        )
        self.text_box_name = tk.Entry(
            self.rec_manage_frame, font=("Arial", 10),
            fg="#2c3e50", bg="#ecf0f1", width=100,
            relief="solid"
        )
        self.save_button = tk.Button(
            self.rec_manage_frame, text="💾 Save",font=("Arial", 9, "bold"), width=10, height=1, relief="flat", name="save_button"
        )
        self.lib_button = tk.Button(
            self.rec_manage_frame, text="📚 Library",font=("Arial", 9, "bold"), width=10, height=1, relief="flat", name="lib_button"
        )
        self.history_list = tk.Menu(self.parent, tearoff=0, name="history_menu")

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.scrollable_window, width=event.width)

    def layout(self):
        screen_height = self.parent.winfo_screenheight()
        self.parent.geometry(f"1200x{screen_height}")

        self.title.pack(side="left", padx=10)
        self.frame.pack(side="top", fill="x", pady=10)
        self.title_label.pack()
        self.subtitle_label.pack(pady=(0, 10))

        self.view.layout()
        self.view.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.header.pack(fill="x")
        self.btn.pack(side="right", padx=10, pady=5)

        self.canvas_frame.pack(fill="both", expand=True)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.rec_manage_frame.pack(fill="x", padx=20, pady=10)

        self.voice_rec_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.effectsFrame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.equalizerFrame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.label.pack(pady=15)
        self.button_voice_rec_frame.pack(pady=10)
        self.record_button.grid(row=0, column=0, padx=10, pady=5)
        self.play_button.grid(row=0, column=1, padx=10, pady=5)
        self.stop_button.grid(row=0, column=2, padx=10, pady=5)

        self.pitch_label.pack(anchor="w", padx=10, pady=(10, 0))
        self.pitch.pack(padx=10, pady=5)
        self.pitch_value.pack(pady=(0, 10))
        self.reverb_label.pack(anchor="w", padx=10, pady=(10, 0))
        self.reverb.pack(padx=10, pady=5)
        self.reverb_value.pack(pady=(0, 10))
        self.echo_label.pack(anchor="w", padx=10, pady=(10, 0))
        self.echo.pack(padx=10, pady=5)
        self.echo_value.pack(pady=(0, 10))

        self.low_label.pack(anchor="w", padx=10, pady=(10, 0))
        self.low.pack(padx=10, pady=5)
        self.high_label.pack(anchor="w", padx=10, pady=(10, 0))
        self.high.pack(padx=10, pady=5)
        self.dist_label.pack(anchor="w", padx=10, pady=(10, 0))
        self.dist.pack(padx=10, pady=5)
        self.dist_value.pack(pady=(0, 10))

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        self.rec_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.text_box_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        self.lib_button.grid(row=0, column=3, padx=5, pady=5)
        self.rec_manage_frame.grid_columnconfigure(1, weight=1)



    def actions_binding(self):
        self.record_button.bind("<Button-1>" , self.record_sound)
        self.play_button.bind("<Button-1>" , self.play_sound)
        self.stop_button.bind("<Button-1>" , self.stop_sound)
        self.save_button.bind("<Button-1>", self.save_sound)
        self.lib_button.bind("<Button-1>", self.show_history_list)
        self.pitch.config(command=lambda val: (
            self.pitch_value.config(text=f"{val}%"),
            self.apply_pitch(float(val))
        ))
        self.reverb.config(command=lambda val: (
            self.reverb_value.config(text=f"{val}%"),
            self.apply_reverb(float(val))
        ))
        self.echo.config(command=lambda val: (
            self.echo_value.config(text=f"{val}%"),
            self.apply_echo(float(val))
        ))
        self.low.config(command=lambda val: (
            self.apply_pass_bas(int(val))
        ))
        self.high.config(command=lambda val: (
            self.apply_pass_haut(int(val))
        ))
        self.dist.config(command=lambda val: (
            self.dist_value.config(text=f"{val}%"),
            self.apply_distortion(float(val))
        ))
        self.btn.bind("<Button-1>" , self.affichage_spectrum)
        for name in self.model.get_all():
            self.history_list.add_command(label=name, command=lambda n=name: self.load_model(n))

    def load_model(self, name):
        self.model.set_name(name)
        self.model.read()
    
    def affichage_spectrum(self , event):
        sound= self.model.get_sound_instance()
        plt.plot(sound.get_vecteur_freqs() , sound.filtredSpectrum)
        plt.show()
    
    def set_model(self, model):
        self.model = model

    def show_history_list(self, event):
        self.history_list.tk_popup(event.x_root, event.y_root)

    def save_sound(self, event):
        if self.model.get_sound_instance().get_audio() is None:
            tk.messagebox.showwarning(
                title="Save",
                message="Aucun son à sauvegarder"
            )
            return

        name = self.text_box_name.get().strip()
        self.model.set_name(name)
        if name and self.model.get_sound_instance():
            if self.model.exists():
                result = tk.messagebox.askyesno("Confirm", "Model deja exist, voulez vous faire un mis a jour ?")
                if result:
                    self.model.update()
                    self.model.update_samples()
            else:
                self.model.create()
                tk.messagebox.showinfo(
                    title="Save",
                    message=f"Model {self.model.get_name()} sauvegardé avec succès dans la base de données !"
                )
                self.history_list.add_command(label=self.model.get_name(), command=lambda n=name: self.load_model(n))
        else:
            tk.messagebox.showwarning(
                title="Save",
                message="le nom est vide !!"
            )
        

    def record_sound(self,event):
        if self.model.get_sound_instance().get_audio() is not None:
            result = tk.messagebox.askyesno(
                title="Exit",
                message="Voulez Sauvgarder le son actuel avant d'enregistrer un autre ?"
            )
            if result:
                self.save_sound(event)
        value = tk.simpledialog.askstring(title="Test", prompt="la durée de la voix en secondes")
        if value is None:
            return

        try:
            duration = int(value)
            if duration <= 0:
                return
        except ValueError:
            tk.messagebox.showerror("Erreur", "Veuillez entrer un nombre entier valide.")
            return
        sound = Sound(duration) 
        sound.record()
        self.model.set_sound(sound)

    def play_sound(self, event):
        self.stop_event.clear()

        def target():
            self.model.get_sound().hear_voice(self.isFiltred, stop_event=self.stop_event)

        self.play_thread = threading.Thread(target=target)
        self.play_thread.start()

    def stop_sound(self, event):
        if self.play_thread and self.play_thread.is_alive():
            self.stop_event.set()
            self.play_thread.join() 

    def apply_reverb(self  , val):
        self.isFiltred = 1
        value = val /100
        self.model.apply_reverb(value)
        self.model.set_effect("reverbe")
        self.model.set_effect_value(value)

    def apply_echo(self  , val):
        self.isFiltred = 1
        value = val /100
        self.model.apply_echo(value)
        self.model.set_effect("echo")
        self.model.set_effect_value(value)

    def apply_pass_bas(self , freq):
        self.isFiltred = 1
        self.model.apply_pass_bas(freq)
        self.model.set_filter_type("pass_bas")

    def apply_pitch(self , pitch):
        self.isFiltred = 1
        pitch /= 10
        if pitch < 0 :
            pitch -=1
        self.model.apply_pitch(pitch)

    def apply_pass_haut(self , freq):
        self.isFiltred = 1
        self.model.apply_pass_haut(freq)
        self.model.set_filter_type("pass_haut")

    def apply_distortion(self , value):
        print(value/100)
        self.isFiltred = 1
        self.model.apply_distortion(value)
        self.model.set_effect("distortion")
        self.model.set_effect_value(value)




if __name__ == "__main__":
    root = tk.Tk()
    root.title("User's View")
    
    model = WaveModel("tst")
  
    v = View(root)  
    model.attach(v)
    controller = WaveController(root, model, v)

    root.mainloop()
