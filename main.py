#kivy modules
from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.core.window import Window

#screens
from classes.screens.inicial_menu.inicial_menu import Selecionar_Sala
from classes.screens.game.game import Jogo

#kivy screens manager
class Gerenciador_de_telas(ScreenManager):
    def __init__(self,**kwargs):
        super(Gerenciador_de_telas,self).__init__(**kwargs)
        self.add_widget(Selecionar_Sala(name='sala'))
        self.add_widget(Jogo(name='jogo'))

#inicialization of the application
class main(App):
    def build(self):
        self.title = 'BCC Halla'
        #Window.size = (800,600)
        Window.size = (600,600)
        return Gerenciador_de_telas()
    
main().run()
    
