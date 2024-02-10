import os
from kivy.uix.screenmanager import Screen
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from threading import Thread
from functools import partial
import time
from kivy.lang import Builder

Builder.load_file('classes/screens/inicial_menu/ui.kv')

class CustomDropDown(DropDown):
    pass

class Selecionar_Sala(Screen):
    def __init__(self,**kwargs):
        super(Selecionar_Sala,self).__init__(**kwargs)
        self.sala = None
        self.pais = 'Brasil'

    def on_enter(self):
        dropdown = DropDown()
        paises = ['Brasil','Russia','USA','Japao','Alemenha','Ucrania']
        for pais in paises:
            btn = Button(text= pais, size_hint_y=None, height=44,background_color=[0.5,0.9,1,1],color=[1,1,1,1])
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
            
        self.mainbutton = Button(text='Brasil', size_hint=(None, None),background_color=[0.5,0.9,1,0.9],color=[1,1,1,1])
        self.mainbutton.height = 50
        self.mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        
        self.ids.list.add_widget(dropdown)
        self.ids.list.add_widget(self.mainbutton)
        dropdown.dismiss()
    
    def criar(self,*args):
        if 'ROOM.txt' in os.listdir():
            os.remove('ROOM.txt')
        Thread(target=partial(os.system,'python classes/conections/server.py')).start()
        while True:
            if 'ROOM.txt' in os.listdir():
                time.sleep(1)
                break
        with open('ROOM.txt','r') as file:
            self.sala = file.read()
        os.remove('ROOM.txt')
        self.pais = self.mainbutton.text
        self.parent.current = 'jogo'

    def entrar(self,*args):
        self.sala = self.ids.sala.text
        self.pais = self.mainbutton.text
        self.parent.current = 'jogo'
