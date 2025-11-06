import sys
import tkinter as tk
import sqlite3

from observer import Subject
from filtres import Sound
import numpy as np

class WaveModel(Subject):
    def __init__(self, name):
        Subject.__init__(self)
        self.name = name
        self.sound_instance = Sound(duration=8)
        self.effect = None
        self.effect_value = 0.0
        self.filter_type = None
        self.low_cut = 0.0
        self.high_cut = 0.0
        self.db = "VoiceManager.db"
        self.connection = sqlite3.connect(self.db)
    
    def get_name(self):
        return self.name
    
    def get_low_cut(self):
        return self.low_cut
    
    def set_low_cut(self, low_cut):
        self.low_cut = low_cut

    def get_high_cut(self):
        return self.high_cut
    
    def set_high_cut(self, high_cut):
        self.high_cut = high_cut

    def set_name(self, name):
        self.name = name

    def get_filtred_sound(self):
        return self.sound_instance.get_filtred_sound()

    def get_sound_samples(self):
        return self.sound_instance.get_audio()
    
    def get_sound_instance(self):
        return self.sound_instance
    
    def set_sound_samples(self, samples):
        if hasattr(samples, '__iter__') and len(samples) > 0 and isinstance(samples[0], tuple):
            if isinstance(samples[0][0], (bytes, bytearray)):
                arr = np.frombuffer(b''.join(row[0] for row in samples), dtype=np.float32).reshape(-1, 1)
            else:
                arr = np.array([[row[0]] for row in samples], dtype=np.float32)
        else:
            arr = np.array(samples, dtype=np.float32)
            if arr.ndim == 1:
                arr = arr.reshape(-1, 1)

        self.sound_instance.set_audio(arr)


    def get_filter_type(self):
        return self.filter_type
    
    def set_filter_type(self, filter_type):
        self.filter_type = filter_type

    def get_freq_c(self):
        return self.freq_c
    
    def set_freq_c(self, freq_c):
        self.freq_c = freq_c

    def get_effect(self):
        return self.effect
    
    def set_effect(self, effect):
        self.effect = effect

    def set_effect_value(self, value):
        self.effect_value = value

    def get_effect_value(self):
        return self.effect_value

    def get_sound(self):
        return self.sound_instance
    

    def apply_reverb(self , value):
        self.sound_instance.reverbe(value, 20000)
        self.effect = "reverbe"
        self.effect_value = value
        self.notify()


    def apply_echo(self , value):
        self.sound_instance.echo(value, 20000)
        self.effect = "echo"
        self.effect_value = value
        self.notify()


    def apply_pass_bas(self , value):
        self.sound_instance.filtre_passBas(value , 6)
        self.low_cut = value
        self.high_cut = 0
        self.notify()

    def apply_distortion(self , value) :
        self.sound_instance.distortion(value)
        self.notify()

    def apply_pass_haut(self , value):
        self.sound_instance.filtre_passHaut(value , 6)
        self.high_cut = value
        self.low_cut = 0
        self.notify()

    def apply_pitch(self , value):
        self.sound_instance.apply_pitch(value)
        self.effect = "pitch"
        self.effect_value = value
        self.notify()

    def reset_model(self):
        self.sound_instance = Sound(duration=8)
        self.effect = None
        self.effect_value = 0.0
        self.filter_type = None
        self.low_cut = 0.0
        self.high_cut = 0.0
        self.notify()


    def set_sound(self, sound):
        self.sound_instance = sound
        self.notify()
    
    def create(self, db="VoiceManager.db"):
        cursor = self.connection.cursor()
        query = "INSERT OR IGNORE INTO waves(name, type_filter, low_cut, high_cut, duration, effect, effect_value) VALUES (?,?,?,?,?,?,?)"
        cursor.execute(query, (self.name, self.filter_type, self.low_cut, self.high_cut, self.sound_instance.duration, self.effect, self.effect_value))

        query = "INSERT OR IGNORE INTO samples (id, fragment, wave_id) VALUES (?,?,?)"
        id_sample = 1
        for fragment in self.get_sound_samples():
            cursor.execute(query, (id_sample, float(fragment[0]), self.get_name()))
            id_sample += 1

        
        self.connection.commit()
        cursor.close()

    def read(self, db="VoiceManager.db"):
        cursor = self.connection.cursor()

        query = "SELECT type_filter, low_cut, high_cut, duration, effect, effect_value FROM waves WHERE name=?"
        results = cursor.execute(query, (self.get_name(),)).fetchone()
        self.filter_type = results[0]
        self.low_cut = int(results[1])
        self.high_cut = int(results[2])
        self.sound_instance = Sound(duration=int(results[3]))
        self.effect = results[4]
        self.effect_value = results[5]


        query = "SELECT fragment FROM samples WHERE wave_id=? ORDER BY id"
        rows = cursor.execute(query, (self.get_name(),)).fetchall()
        if rows:
            self.set_sound_samples(rows)
        
        self.applique_effect_db()
        self.applique_filter_db()

        cursor.close()
        self.notify()

    def applique_effect_db(self):
        if self.effect == "distortion":
            self.apply_distortion(self.effect_value)
        if self.effect == "echo":
            self.apply_echo(self.effect_value)
        if self.effect == "reverbe":
            self.apply_reverb(self.effect_value)
    
    def applique_filter_db(self):
        if self.filter_type == "pass_bas":
            self.apply_pass_bas(self.low_cut)
        if self.filter_type == "pass_haut":
            self.apply_pass_haut(self.high_cut)

    def update(self, db="VoiceManager.db"):
        cursor = self.connection.cursor()
        query = "UPDATE waves SET type_filter=?, low_cut=?, high_cut=?, duration=?, effect=?, effect_value=? WHERE name=?"
        cursor.execute(query, (self.filter_type, self.low_cut, self.high_cut, self.sound_instance.get_duration(), self.effect, self.effect_value, self.get_name()))
        self.connection.commit()
        cursor.close()
        self.notify()

    def update_samples(self, db="VoiceManager.db"):
        cursor = self.connection.cursor()
        add_query = "UPDATE samples SET fragment=? WHERE id=? AND wave_id=?"
        sample_id = 1
        for sample in self.get_sound_samples() :
            cursor.execute(add_query, ( sample[0], sample_id, self.get_name()))
            sample_id += 1
        self.connection.commit()
        cursor.close()
        self.notify()

    def delete(self, db="VoiceManager.db"):
        cursor = self.connection.cursor()
        query = "DELETE FROM samples WHERE wave_id=?"
        cursor.execute(query, (self.get_name(),))
        query = "DELETE FROM waves WHERE name=?"
        cursor.execute(query, (self.get_name(),))
        self.connection.commit()
        cursor.close()
        self.notify()

    def exists(self, db="VoiceManager.db"):
        cursor = self.connection.cursor()
        query = "SELECT 1 FROM waves WHERE name = ? LIMIT 1"
        cursor.execute(query, (self.name,))
        result = cursor.fetchone()
        cursor.close()
        return bool(result)

    def get_all(self, db="VoiceManager.db"):
        cursor = self.connection.cursor()
        query = "select name from waves"
        cursor.execute(query)

        result = cursor.fetchall()
        names = [row[0] for row in result]
        self.connection.commit()
        cursor.close()
        
        return names

 
if   __name__ == "__main__" :
    model = WaveModel("test Model")
    choix = input("choose (0,1,2,3) : ")
    if choix == '0' :
        s = Sound(duration=5)
        model.set_sound(s)
        model.get_sound().record()
        model.create()
    elif choix == '1' :
        model.read()
        model.get_sound_instance().hear_voice(False)
    elif choix == '2' :
        model.set_filter_type("high_pass")
        model.set_low_cut(400.0)
        model.set_high_cut(2000.0)
        model.update()
    elif choix == '3' :
        model.delete()

    print("name : ", model.get_name())
    print("filter type : ", model.get_filter_type())
    print("low cut : ", model.get_low_cut())
    print("high cut : ", model.get_high_cut())
    print("duration : ", model.get_sound().get_duration())
    print("first 10 samples : ")
    i = 0
    if model.get_sound().get_audio() is not None :
        for val in model.get_sound().get_audio():
            i += 1
            if i == 10 :
                break
    