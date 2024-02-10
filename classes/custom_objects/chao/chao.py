from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.lang import Builder

Builder.load_file('classes/custom_objects/chao/ui.kv')

class Chao(Widget):    
    texture = Image(source='assets/textures/scene/terra.jpg').texture
    texture.wrap = 'repeat'
    texture.uvsize = (8,1)
    def __init__(self,**kwargs):
        super(Chao,self).__init__(**kwargs)
        self.texture.uvsize = (int(self.width/self.height),1)
