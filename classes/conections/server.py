import socket
import os
import random
from threading import Thread
from functools import partial

class Sala:
    def __init__(self):


        self.jogo = {}
        self.room_time = 0     
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        self.HOST = s.getsockname()[0]
        option = range(3000,4000)
        self.PORT = random.choice(option)
        while True:
            if self.portIsGood(self.HOST,self.PORT): break
            else: self.PORT += 1
        print('room at > ',self.HOST,':',self.PORT)
        with open('ROOM.txt','w') as file:
            file.write(f"{self.HOST}:{self.PORT}")

            
        while True:
            self.room_time += 1
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                s.bind((self.HOST,self.PORT))
                s.listen(5)
                conn,addr = s.accept()
                with conn:
                    data = None
                    while True:
                        dataRaw = conn.recv(1024)
                        data = repr(dataRaw)[2:-1]
                        if data != '':
                            Thread(target=partial(self.handle_message,data)).start()
                        if not dataRaw: break

    def send(self,host,port,message,*args):
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host,int(port)))
                    s.sendall(message.encode('utf-8'))
                break
            except: pass

    def handle_message(self,message):
        data = message.split('&')
        
        if data[0] == 'entrar':
            nickName = ''
            while True:
                options = range(100)
                nickName = str(random.choice(options))
                if nickName not in self.jogo:
                    break
            self.jogo[nickName] = {'pais':data[8],'x':data[6],'y':data[7],'fx':0,'fy':0,'host':data[2],'port':data[3],'animacao':data[4],'name':data[5]}
            self.send(data[2],data[3],'entrar&' + nickName)
            message = self.game_payload() + '&' + str(self.room_time)
            for cada in self.jogo:
                if cada == nickName: continue
                host = self.jogo[cada]['host']
                port = self.jogo[cada]['port']
                Thread(target=partial(self.send,host,port,message)).start()

        elif data[0] == 'atualizar':  
            self.jogo[data[1]]['x'] = data[2]
            self.jogo[data[1]]['y'] = data[3]
            self.jogo[data[1]]['animacao'] = data[4]
            self.jogo[data[1]]['fx'] = data[5]
            self.jogo[data[1]]['fy'] = data[6]
            message = self.game_payload() + '&' + str(self.room_time)
            for cada in self.jogo:
                if cada == data[1]: continue
                host = self.jogo[cada]['host']
                port = self.jogo[cada]['port']
                Thread(target=partial(self.send,host,port,message)).start()

        elif data[0] == 'message':
            for cada in self.jogo:
                host = self.jogo[cada]['host']
                port = int(self.jogo[cada]['port'])
                self.send(host,port,message)

    def game_payload(self):
        payload = ''
        for jogador in self.jogo:
            if payload != '': payload += '&'
            p = f"{jogador}${self.jogo[jogador]['x']}${self.jogo[jogador]['y']}${self.jogo[jogador]['animacao']}${self.jogo[jogador]['name']}${self.jogo[jogador]['fx']}${self.jogo[jogador]['fy']}${self.jogo[jogador]['pais']}"
            payload += p
        return payload
                    
    def portIsGood(self,host,port):
        try:      
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host,port))
                s.close()
            return True
        except: return False 

Sala()
