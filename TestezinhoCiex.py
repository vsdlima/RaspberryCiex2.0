import asyncio
import socket
import os
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from threading import Thread
import time
from datetime import datetime, timedelta
import serial
import struct

DEBUG_XML = False
DEBUG_REDE = True
DEBUG_TIME = True

ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate =9600,           
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1)


ff = struct.pack('B', 0xff)

file_config = 'ConfigM.xml'

full_file = os.path.abspath(os.path.join('data'))


arq_config = os.path.abspath(os.path.join('data', file_config))

if DEBUG_XML:
    xmlConfig = minidom.parse(arq_config)
    listaOperadoresXml = xmlConfig.getElementsByTagName('operador')
    listaOperadores = []
    for operador  in listaOperadoresXml:
        listaOperadores.append(operador.firstChild.nodeValue)

    print(listaOperadores)

    tela = 0

    tela = tela + 1 if False else tela - 1
    print(tela)


if DEBUG_REDE:
    PORTA_BASE_PADRAO = 32000
    MAQUINA = 2
    PORT = PORTA_BASE_PADRAO + MAQUINA
    class Server(Thread):
        def __init__(self):
            Thread.__init__(self)
            #self.daemon = True
            self.start()
        def run(self):
            while True:
                print('A')
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1 )
                    HOST = socket.gethostname()
                    sock.bind((HOST, PORT))
                    sock.listen()

                    client, addr = sock.accept()

                    with client:
                        print('Connectado a', addr)
                        btipo = client.recv(1)
                        tipo = btipo.decode("utf-8")
                        if btipo is 'c' or 'p':  # c = config (ou seja, receber info de maquina), p = prod/paradas (ou seja, enviar xmls)
                            client.send(btipo)     # echo
                            if tipo is 'c':
                                stream = client.recv(1024000)
                                root = ET.fromstring(stream)
                                with open(arq_config,'w') as arq:
                                    arq.write(ET.tostring(root).decode())
                            else:
                                xmlStream = ET.parse(arq_paradas)
                                xmlstr = ET.tostring(xmlStream.getroot()).decode()
                                client.send(bytes(xmlstr, "utf-8"))

                                xmlStream = ET.parse(arq_prod)
                                xmlstr = ET.tostring(xmlStream.getroot()).decode()
                                client.send(bytes(xmlstr, "utf-8"))
                        else:
                            print('Erro!')
                

          

if DEBUG_REDE:
     Server()

     #while True:
     #    pass


if DEBUG_TIME:
    class TimeRTC(Thread):
        def __init__(self):
            Thread.__init__(self)
            #self.daemon = True
            self.start()
        def run(self):
            while True:
                startTempo = datetime.now()
                while datetime.now() - startTempo < timedelta(seconds=.1):
                    pass
                
                now = datetime.now()
                second = '{:02d}'.format(now.second)
                second = str(second)
                minute = '{:02d}'.format(now.minute)
                minute = str(minute)
                hour = '{:02d}'.format(now.hour)
                hour = str(hour)
                
                tempo = hour + ':' + minute + ':' + second
                tempo = bytes('"'+str(tempo)+'"', encoding='iso-8859-1')
                
                ser.write(b't1.txt=')
                ser.write(tempo)
                ser.write(ff+ff+ff)
                
                x = ser.readlines()
                print(x)
                if x:
                    print('A')
                    for y in x:
                        _, sinal, _ = str(y).split("'")
                        print(sinal)
                        sinal = sinal.replace('\\xff\\xff\\xff', '')
                        print(sinal)
                        e, info1, info2, info3 = sinal.split('\\x')
                        print(info2)


if DEBUG_TIME:
    TimeRTC()

    