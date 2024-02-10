import socket
import os
import random
from threading import Thread
from functools import partial

class Client:
    def __init__(self,room=None):
        self.room_time = 0
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        self.HOST = s.getsockname()[0]
        option = range(3000,4000)
        self.PORT = random.choice(option)
        while True:
            if self.portIsGood(self.HOST,self.PORT): break
            else: self.PORT += 1
        self.roomIP = room[0]
        self.roomPORT = room[1]
        self.response_update = ''
        self.response_message = ''
        Thread(target=self.runServer).start()

    def sendMessage(self,message,*args):
        Thread(target=partial(self.send,message)).start()

    def runServer(self,*args):
        while True:       
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
                            dt = data.split('&')
                            
                            if dt[0] == 'message':
                                self.response_message = str(data)
                            elif dt[0] == 'entrar':
                                self.response_update = str(dt[1])
                            elif int(dt[-1]) > self.room_time:
                                self.room_time = int(dt[-1])
                                updateData = data[:(len(str(self.room_time))+1)*-1]
                                self.response_update = str(updateData)
                                
                        if not dataRaw: break

    def send(self,message,*args):
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.roomIP,int(self.roomPORT)))
                    s.sendall(message.encode('utf-8'))
                break
            except: pass
                    
    def portIsGood(self,host,port):
        try:      
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host,port))
                s.close()
            return True
        except: return False
