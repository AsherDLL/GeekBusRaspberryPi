
import requests
import functools
import os.path
import pyudev
import subprocess
import json
import re
import sys
import time
import urllib
from uuid import getnode as get_mac
from requests.exceptions import ConnectionError

CONS_IP =  '10.50.89.208:8000'
#global authentication
global Ciclo
global success
global Q
Q = []
success = False
authentication = 0
Ciclo = False
contador = 0
####################################################
def send_Q_to_server( Q, url_update):
    if len(Q) > 0:
        for element in Q:
            try:
    
                if len(Q) == 0:
                    return
                r = requests.post(url_update, data = element)
                q_obj = json.loads(r.text)
                confirmation = q_obj["success"]
                if confirmation == True:
                    print len(Q)
                    print element
                    Q.remove(element)
            except ConnectionError as e:
                print ("Error de conexion")
                
    
    ###################################################
def rusb():

    time.sleep(10)
    global authentication 
    if authentication != 0:
        post()
        return
    try:
        f=open("/media/pi/DONGLE/prueba.txt",'r+')

        password = f.readline()
        password = password[:-1]
        mac = get_mac()

        f.close()

        url_login = 'http://'+CONS_IP +'/api/servicio/login'
        credenciales = {'conductorKey':password, 'camionKey':mac}
        r_credenciales = requests.post(url_login, data = credenciales)
        obj = json.loads(r_credenciales.text)
        authentication = obj["auth"]
        success = obj["success"]
        
        print "Credenciales"
        print r_credenciales

        if success == True:
            post()
        else:
            print (obj["message"])
    except (OSError, IOError) as e:
        print("Error al leer credenciales") 
    
    ###################################################

def post():
    try:
        f=open("Texto.txt",'r+')
        pasajeros = f.readline()
        pasajeros = pasajeros[:-1]
        latitud = f.readline()
        latitud = latitud[:-1]
        longitud = f.readline()
        longitud = longitud[:-1]
        RPM = f.readline()
        RPM = RPM[:-1]
        Vel = f.readline()
        Vel = Vel[:-1]
        T = f.readline()
        T = T[:-1]
        f.close()
        
    except (OSError, IOError) as e:
        print("Error al leer los valores del sensor")

    try:
        url_update = 'http://'+CONS_IP +'/api/servicio/update'
        global authentication
        payload = {'auth':authentication,'rpm':int(RPM),'pasajeros':int(pasajeros),'velocidad':int(Vel),'lat':float(latitud),'long':float(longitud),'temp':int(T)}
        print payload
        r = requests.post(url_update, data = payload)

        #Response
        print "Post de datos al server"
        print r.text
        r.status_code

        q_obj = json.loads(r.text)
        confirmation = q_obj["success"]

    except ConnectionError as e:
        print("Error en la conexion, post fallido")
        confirmation = False

    

    
    if confirmation == False:
        Q.append(payload)
    else:
        send_Q_to_server(Q, url_update)


    ######################SHUTDOWN#################

    url_shutdown = 'http://'+CONS_IP +'/api/servicio/shutdown'
    shutdown = {'auth':authentication}
    
    try:
        
        
        if int(RPM) == 0:
            if shutdown_obj["success"] == True:
                r_shutdown = requests.post(url_shutdown, data = shutdown)
                shutdown_obj = json.loads(r_shutdown.text)
                print shutdown_obj["message"]
                sys.exit(0)
    except ConnectionError as e:
        print("Error en la conexion, post fallido")
        RPM = 0
    

    ###################################################
def main():
    global contador
    if contador == 0:
        log = {'temp': 10212, 'velocidad': 147, 'long': 99.334511, 'auth': 1, 'lat': 86.565481, 'rpm': 0, 'pasajeros': 24}
        logout = requests.post('http://'+CONS_IP +'/api/servicio/shutdown', data = log )
        logout_obj = json.loads(logout.text)
        contador = 2346
    print contador
    print logout.text

    
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))
    path = functools.partial(os.path.join, BASE_PATH)
    call = lambda x, *args: subprocess.call([path(x)] + list(args))

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')  
    monitor.start()
    Bandera=True
    conectado=True

    for device in iter(monitor.poll, None): 
        if Bandera:
            if conectado:
                print ('Conectaste la usb')
                Bandera=False
                conectado=False
                Ciclo = True				                
                
            else:
                print ('Desconectaste la usb')
                Bandera=False
                conectado=True
                

        while conectado == False:
            rusb()
            time.sleep(7)
            
        else:
            Bandera=True

    if Ciclo == True:
        print('Entro')
        
    ###################################################
		
if __name__ == '__main__':
    main()
