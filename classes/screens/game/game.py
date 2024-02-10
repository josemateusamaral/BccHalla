#kivy modules
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

#python modules
import os
from functools import partial

#custom objects
from classes.conections.client import Client
from classes.custom_objects.jogador.jogador import Jogador
from classes.custom_objects.chao.chao import Chao

#consts
GRAVIDADE = -0.1
ATRITO = -0.03

Builder.load_file('classes/screens/game/ui.kv')


class Jogo(Screen):

    def __init__(self,**kwargs):
        super(Jogo,self).__init__(**kwargs)
        
        #variaveis do ambiente
        self.gameData = True
        self.client = ''
        self.updated = False
        self.nameNick = ''
        self.sala = ''
        self.pais = ''
        self.nickname = ''
        self.teclas_pressionadas = []
        self.animacaoAtual = 'assets/textures/inimigo/parado.png'
        self.jogo = {}
        self.jogador = {'tipo':'player','x':400,'y':300,'fx':0,'fy':0,'obj':None,'update':True}
        self.sollides = []
        self.messages = ''


        #configurar teclado
        self._keyboard = Window.request_keyboard(self.teclas_TASK,self)
        self._keyboard.bind(on_key_down=self.add_tecla)
        self._keyboard.bind(on_key_up=self.remove_tecla)

        


        
            
    #methodos de inicializacao e tasks
    def on_pre_enter(self):
        Clock.schedule_once(self.config,0.01)
        self.sala = self.parent.get_screen('sala').sala
        self.pais = self.parent.get_screen('sala').pais
        self.ids.sala.text = self.sala
        self.nameNick = self.parent.get_screen('sala').ids.name.text
        self.ids.nome.text = self.nameNick
        dt = self.sala.split(':')
        self.client = Client( room = [dt[0],dt[1]] )
        self.entrar()

    def on_enter(self,*args):
        speed = 0.1
        Clock.schedule_interval(self.update_TASK,0.01)
        Clock.schedule_interval(self.teclas_TASK,0.01)
        Clock.schedule_interval(self.checkClient_TASK,0.01)
        





    #configurar tela do jogo
    def config(self,*args):

        #jogador
        playerObj = Jogador()
        playerObj.pos = [self.jogador['x'],self.jogador['y']]
        self.jogador['obj'] = playerObj
        self.ids.gameBox.add_widget(playerObj)

        #lista de objetos do cenario
        sollides_list = [
            {'sx':500,'sy':50,'px':100,'py':100},
            {'sx':200,'sy':50,'px':200,'py':300},
            {'sx':100,'sy':50,'px':600,'py':400}
        ]

        #renderizar os objetos
        for s in sollides_list:
            sollide = Chao()
            sollide.size_hint = [None,None]
            sollide.height = s['sy']
            sollide.width = s['sx']
            sollide.pos = [s['px'],s['py']]
            self.sollides.append(sollide)
            self.ids.gameBox.add_widget(sollide)

    def config_tabela(self):
        self.ids.players.clear_widgets()
        box = BoxLayout(size_hint_y=None,height=50)
        box.add_widget(Label(text=self.nameNick,color=[0.4,1,0.4,1]))
        box.add_widget(Label(text=self.pais,color=[1,1,1,1]))
        self.ids.players.add_widget(box)
        for player in self.jogo:
            box = BoxLayout(size_hint_y=None,height=50)
            box.add_widget(Label(text=self.jogo[player]['name'],color=[1,1,1,1]))
            box.add_widget(Label(text=self.jogo[player]['pais'],color=[1,1,1,1]))
            self.ids.players.add_widget(box)
        self.ids.players.add_widget(Widget())






    #atualizar a sala com os dados do servidor
    def updateGame(self,data,*args):
        gameList = data.split('&')
        for cada in gameList:
            dados = cada.split('$')
            if str(dados[0]) == str(self.nickname): continue
            name = dados[0]
            x = float(dados[1])
            y = float(dados[2])
            animacao = dados[3]
            nameNick = dados[4]
            fx = float(dados[5])
            fy = float(dados[6])
            pais = str(dados[7])
            if name not in self.jogo:
                playerObj = Jogador()
                playerObj.pos = [x,y]
                playerObj.source = animacao
                self.ids.gameBox.add_widget(playerObj)
                nome = Label(size_hint=[None,None],height=50,width=50,text=nameNick,color=[1,0,0,1],bold=True)
                self.ids.names.add_widget(nome)
                self.jogo[name] = {'obj':playerObj,'x':x,'y':y,'fx':fx,'fy':fy,'animacao':animacao,'name':nameNick,'nameNick':nome,'update':True,'pais':pais}
                if self.ids.gameData.opacity == 1:
                    self.config_tabela()
                self.atualizarServidor_TASK()
            else:
                self.jogo[name]['fx'] = fx
                self.jogo[name]['fy'] = fy
                self.jogo[name]['x'] = x
                self.jogo[name]['y'] = y
                self.jogo[name]['animacao'] = animacao
                self.jogo[name]['obj'].source = animacao
                
        for jogador in self.jogo:
            self.jogo[jogador]['obj'].pos[0] = self.jogo[jogador]['x']
            self.jogo[jogador]['obj'].pos[1] = self.jogo[jogador]['y']
            self.jogo[jogador]['nameNick'].pos = [self.jogo[jogador]['x']-5,self.jogo[jogador]['y']+24]
            
    def updateChat(self,message,*args):
        data = message.split('&')
        player = data[1]
        message = data[2]
        newMessage = f"{player}: {message}\n"
        self.messages += newMessage
        self.ids.chat.text = self.messages
                
            




    #operacoes com o servidor
    def entrar(self,again=False,*args):
        if not again:
            self.client.sendMessage(message=f"entrar&{self.nickname}&{self.client.HOST}&{self.client.PORT}&{self.animacaoAtual}&{self.nameNick}&{self.jogador['x']}&{self.jogador['y']}&{self.pais}")
        if self.client.response_update != '':
            self.nickname = self.client.response_update
            self.client.response_update = ''
            self.ids.sala.text = f'sala_> {self.sala}'
            return
        Clock.schedule_once(partial(self.entrar,True))
        
    def atualizarServidor_TASK(self,*args):
        self.client.sendMessage(message=f"atualizar&{self.nickname}&{self.jogador['x']}&{self.jogador['y']}&{self.animacaoAtual}&{self.jogador['fx']}&{self.jogador['fy']}")

    def enviarMensagem(self,*args):
        message = self.ids.message.text.replace('\n','')
        self.client.sendMessage(message=f"message&{self.nameNick}&{message}")
        self.ids.messageBox.opacity = 0
        self.ids.message.text = ''

    def checkClient_TASK(self,*args):
        if self.client.response_update != '':
            self.updateGame(self.client.response_update)
            self.client.response_update = ''
        if self.client.response_message != '':
            self.updateChat(self.client.response_message)
            self.client.response_message = ''




    
    #atualizaar a animacao do personagem
    def updateTexture(self,obj,textureType,*args):
        if obj['fx'] > 0 and obj['fy'] > 0:
            obj['obj'].source = f'assets/textures/{textureType}/direitaCima.png'
            return 'assets/textures/inimigo/direitaCima.png'
        elif obj['fx'] < 0 and obj['fy'] > 0:
            obj['obj'].source = f'assets/textures/{textureType}/esquerdaCima.png'
            return 'assets/textures/inimigo/esquerdaCima.png'
        elif obj['fx'] < 0 and obj['fy'] < -1:
            obj['obj'].source = f'assets/textures/{textureType}/esquerdaBaixo.png'
            return 'assets/textures/inimigo/esquerdaBaixo.png'
        elif obj['fx'] > 0 and obj['fy'] < -1:
            obj['obj'].source = f'assets/textures/{textureType}/direitaBaixo.png'
            return 'assets/textures/inimigo/direitaBaixo.png'
        elif obj['fx'] > 0:
            obj['obj'].source = f'assets/textures/{textureType}/direita.png'
            return 'assets/textures/inimigo/direita.png'
        elif obj['fx'] < 0:
            obj['obj'].source = f'assets/textures/{textureType}/esquerda.png'
            return 'assets/textures/inimigo/esquerda.png'
        elif obj['fy'] > 0:
            obj['obj'].source = f'assets/textures/{textureType}/pulando.png'
            return 'assets/textures/inimigo/pulando.png'
        else:
            obj['obj'].source = f'assets/textures/{textureType}/parado.png'
            return 'assets/textures/inimigo/parado.png'







    #funcoes relacionadas ao teclado
    def add_tecla(self,keyboard=None,keycode=None,text=None,modifiers=None):
        if self.ids.message.focused: return
        if keycode[1] not in self.teclas_pressionadas:
            self.teclas_pressionadas.append(keycode[1])
            
    def remove_tecla(self,keyboard=None,keycode=None,text=None,modifiers=None):
        if keycode[1] in self.teclas_pressionadas:
            self.teclas_pressionadas.remove(keycode[1])

        if keycode[1] == 'p' and not self.ids.message.focused:
            if self.ids.gameData.opacity == 1:
                self.ids.gameData.opacity = 0
                self.ids.chat.opacity = 1
            else:
                self.ids.gameData.opacity = 1
                self.ids.chat.opacity = 0
                self.config_tabela()

        elif keycode[1] == 'enter':
            if self.ids.messageBox.opacity == 1:
                self.ids.messageBox.opacity = 0
                self.ids.message.focus = False
                if self.ids.message.text != '\n': self.enviarMensagem()
            else:
                self.ids.message.text = ''
                self.ids.messageBox.opacity = 1
                self.ids.message.focus = True
                    
    def teclas_TASK(self,*args):
        for tecla in self.teclas_pressionadas:
            #if self.jogador['fy'] == 0:
            if tecla in ['w','up'] and self.jogador['fy'] == 0:
                self.jogador['fy'] += 8
                self.jogador['update'] = True
                self.atualizarServidor_TASK()
            if tecla in ['a','left']:
                self.jogador['fx'] -= 0.5
                self.jogador['update'] = True
                self.atualizarServidor_TASK()
            if tecla in ['d','right']:
                self.jogador['fx'] += 0.5
                self.jogador['update'] = True
                self.atualizarServidor_TASK()








    
    #task que atualiza a fisica e a posicao do jogador
    def update_TASK(self,*args):
        for jogador in self.jogo:
            self.jogo[jogador]['update'] = True
            self.update_Physics(self.jogo[jogador])
            self.updateTexture(obj=self.jogo[jogador],textureType='inimigo')
            self.jogo[jogador]['nameNick'].pos = [self.jogo[jogador]['x']-5,self.jogo[jogador]['y']+24]
        self.jogador['update'] = True
        self.update_Physics(self.jogador)
        self.animacaoAtual = self.updateTexture(obj=self.jogador,textureType='jogador')
        self.ids.nome.pos = [self.jogador['x']-5,self.jogador['y']+24]

    
    def update_Physics(self,obj,*args):

        #limite de velocidade
        if obj['fy'] > 20:
            obj['fy'] = 20
        if obj['fy'] < -20:
            obj['fy'] = -20
        if obj['fx'] > 2:
            obj['fx'] = 2
        if obj['fx'] < -2:
            obj['fx'] = -2

        #nao sair fora da tela
        if obj['x'] > Window.size[0] - 40:
            obj['fx'] = 0
            obj['x'] = Window.size[0] - 40
        if obj['x'] < 0:
            obj['x'] = 0
            obj['fx'] = 0
        if obj['y'] > Window.size[1] - 40:
            obj['y'] = Window.size[1] - 40
            obj['fy'] = 0
        if obj['y'] < 0:
            obj['y'] = 0
            obj['fy'] = 0
            obj['update'] = False
            
        if not obj['update']: return
        checkY = True

        #move Y
        obj['fy'] += GRAVIDADE
        obj['y'] += obj['fy']
        collisionObject = self.getCollision(obj)
        obj['obj'].pos = [obj['x'],obj['y']] 
        if collisionObject['collision'] and checkY:
            if obj['fy'] > 0:
                obj['y'] = collisionObject['pos'][1] - 40
                obj['fy'] = -0.01
            elif obj['fy'] < 0:
                obj['y'] = collisionObject['pos'][1] + collisionObject['size'][1]
                obj['fy'] = 0
                obj['update'] = False   
            obj['obj'].pos = [obj['x'],obj['y']] 

        #move X
        if not obj['update'] and obj['fy'] != 0: return
        obj['x'] += obj['fx']
        if obj['fx'] > 0:
            obj['fx'] += ATRITO
            if obj['fx'] < 0:
                obj['fx'] = 0
        if obj['fx'] < 0:
            obj['fx'] -= ATRITO
            if obj['fx'] > 0:
                obj['fx'] = 0
        obj['obj'].pos = [obj['x'],obj['y']] 
        collisionObject = self.getCollision(obj)
        if collisionObject['collision']:
            if obj['fx'] > 0:
                obj['x'] = collisionObject['pos'][0] - 40
                obj['fx'] = 0
                obj['update'] = True
            elif obj['fx'] < 0:
                obj['x'] = collisionObject['pos'][0] + collisionObject['size'][0]
                obj['fx'] = 0
                obj['update'] = True
            obj['obj'].pos = [obj['x'],obj['y']] 
            checkY = False

        

        




    #funcao que verifica a colisao com os objetos do cenário
    def getCollision(self,obj,*args):
        x = obj['x']
        y = obj['y']
        sx = obj['obj'].width
        sy = obj['obj'].height
        for cada in self.sollides:
            solide_x = cada.pos[0]
            solide_y = cada.pos[1]
            solide_sx = cada.width
            solide_sy = cada.height
            if x + sx > solide_x and \
               x < solide_x + solide_sx and \
               y + sy > solide_y and \
               y < solide_y + solide_sy:
                return {'collision':True,'pos':[solide_x,solide_y],'size':[solide_sx,solide_sy]}
        return {'collision':False}



