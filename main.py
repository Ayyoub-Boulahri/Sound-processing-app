import sys
major = sys.version_info.major
minor = sys.version_info.minor
if major == 2 and minor == 7:
    import Tkinter as tk
    import tkFileDialog as filedialog
elif major == 3:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog
else:
    if __name__ == "__main__":
        print("Your python version is : ", major, minor)
        print("... I guess it will work !")
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog

from pathlib import Path
import sqlite3

from models import WaveModel
from views import View
from controllers import WaveController


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice Workstation Pro")

        self.model = WaveModel("model")
        self.screen = View(self)
        self.model.attach(self.screen)
        self.option_readfile("main.opt")
        self.controller = WaveController(self, self.model, self.screen)

        self.create_menubar()

    def create_menubar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        actions = {
            "File": [
                ("New", "<Control-n>"),
                ("Load", "<Control-l>"),
                ("Save", "<Control-s>"),
                ("SaveAs", "<Control-S>"),
                ("Exit", "<Control-e>")
            ],
            "Help": [
                ("About Us", "<Control-u>"),
                ("About Application", "<Control-a>"),
                ("About TkInter", "<Control-t>")
            ]
        }

        for key, items in actions.items():
            menu = tk.Menu(menubar, tearoff=0)
            for item, ctrl in items:
                if key == "File":
                    menu.add_command(
                        label=item,
                        accelerator=ctrl,
                        command=lambda name=item: self.on_file_actions(name)
                    )
                    self.bind_all(ctrl, lambda e, name=item: self.on_file_actions(name))
                elif key == "Help":
                    menu.add_command(
                        label=item,
                        accelerator=ctrl,
                        command=lambda name=item: self.on_help_actions(name)
                    )
                    self.bind_all(ctrl, lambda e, name=item: self.on_help_actions(name))
            menubar.add_cascade(label=key, underline=0, menu=menu)

    def on_file_actions(self, name):
        if name == "New":
            self.new_action()
        elif name == "Load":
            self.load_action()
        elif name == "Save":
            self.save_action()
        elif name == "SaveAs":
            self.saveAs_action()
        elif name == "Exit":
            self.quit()
        else:
            print(name + " : action non implémentée")

    def quit(self):
        result = messagebox.askyesno(
                title="Exit",
                message="Voulez vous vraiment quitter l'application ?"
        )
        if result:
            exit(0)

    def new_action(self):
        if self.model.get_sound_instance().get_audio() is not None:
            result = messagebox.askyesno(
                title="Exit",
                message="Voulez vous enregistrer le son actuel ?"
            )
            if result:
                self.save_action()
        voice_name = tk.simpledialog.askstring(title="Test", prompt="donner le nom du Nouveau Voix : ")
        self.model.set_name(voice_name)
        self.model.reset_model()
        

    def load_action(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            title="Charger un fichier audio"
        )

        if not file_path:  
            return

        try:
            sound = self.model.get_sound_instance()
            sound.load(file_path)

            voice_name = Path(file_path).stem
            self.model.set_name(voice_name)

            messagebox.showinfo(
                title="Load",
                message=f"Fichier {file_path} chargé avec succès !"
            )

            self.model.notify()

        except Exception as e:
            messagebox.showerror(
                title="Load Error",
                message=f"Erreur lors du chargement du fichier : {e}"
            )


    def saveAs_action(self):
        sound = self.model.get_sound_instance()

        if sound.get_audio() is None:
            messagebox.showwarning(
                title="Save",
                message="Aucun son à sauvegarder"
            )
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
            initialfile=str(self.model.get_name()),
            title="Enregistrer le fichier audio"
        )

        if not file_path:  
            return

        state = sound.save_as_wav(filename=file_path)
        if state:
            messagebox.showinfo(
                title="Save",
                message=f"Fichier sauvegardé sous {file_path}"
            )
        else:
            messagebox.showerror(
                title="Save",
                message=f"Erreur lors de la sauvegarde du fichier {file_path}"
            )

    def save_action(self):
        sound = self.model.get_sound_instance()

        if sound.get_audio() is None:
            messagebox.showwarning(
                title="Save",
                message="Aucun son à sauvegarder"
            )
            return

        file_name = simpledialog.askstring(
            title="Save",
            prompt="Donner le nom du nouveau son : "
        )

        if not file_name:
            return
        
        self.model.set_name(file_name)    
        if self.model.exists():
            result = tk.messagebox.askyesno("Confirm", "Model deja exist, voulez vous faire un mis a jour ?")
            if result:
                self.model.update()
        else:
            self.model.create()
            self.controller.history_list.add_command(label=self.model.get_name(), command=lambda n=file_name: self.controller.load_model(n))
            messagebox.showinfo(
                title="Save",
                message=f"Model {file_name} sauvegardé avec succès dans la base de données !"
            )


    def on_help_actions(self, name):
        if name == "About Us":
            messagebox.showinfo(
                title=name,
                message="Contacts",
                detail="a24boulah@enib.fr, k24drhour@enib.fr"
            )
        elif name == "About Application":
            messagebox.showinfo(title=name, message="Voice Workstation Pro v1.0")
        elif name == "About TkInter":
            messagebox.showinfo(title=name, message="TkInter - Python GUI toolkit")
        else:
            print(name + " : non reconnu")


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
