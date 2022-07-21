from collections import Counter
import ctypes
import string
import hashlib
from multiprocessing.sharedctypes import Value
from os import kill
import paho.mqtt.client as mqtt
import time
import json
import threading
import multiprocessing
import logging
import random

clients=[
{"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['ppd/pubkey']},
{"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['ppd/pubkey']}
]

nclients=len(clients)


def on_message(client, userdata, message):
    time.sleep(1)
    if(message.topic=='ppd/pubkey'):
        msg=str(message.payload.decode("utf-8")).split(':')
        if(client._client_id.decode('utf-8')!=msg[0]):
            print("recebido no topico ppd/pubkey do client",client._client_id,msg) 
            filename=msg[0]+'.txt'
            content=msg[-1]
            lines = ['-----BEGIN PUBLIC KEY-----',content,'-----END PUBLIC KEY-----']
            with    open(filename, "w") as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')
            
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        for i in range(nclients):
           if clients[i]["client"]==client:
              topic=clients[i]["sub_topic"]
              break
        for j in topic:      
            client.subscribe(j,qos=2)
    else:
        print("Bad connection Returned code=",rc)
        client.loop_stop()  

def on_disconnect(client, userdata, rc):
   pass
   #print("client disconnected ok")
def on_publish(client, userdata, mid):
   print("In on_pub callback mid= "  ,mid)
        

def Create_connections():
   for i in range(nclients):
         # cname=str(i)
    #   t=int(time.time()* 1000)
      client_id ="node"+ str(i) #create unique client_id
      client = mqtt.Client(client_id)             #create new instance
      clients[i]["client"]=client 
      clients[i]["client_id"]=client_id
      # clients[i]["cname"]=cname
      broker=clients[i]["broker"]
      port=clients[i]["port"]
      try:
         client.connect(broker,port)           #establish connection
      except:
         print("Connection Failed to broker ",broker)
         continue
      
      #client.on_log=on_log #this gives getailed logging
      client.on_connect = on_connect
      client.on_disconnect = on_disconnect
      #client.on_publish = on_publish
      client.on_message = on_message
      client.loop_start()
      while not client.connected_flag:
         time.sleep(0.05)
         
mqtt.Client.connected_flag=False #create flag in class
no_threads=threading.active_count()
print("current threads =",no_threads)
print("Creating  Connections ",nclients," clients")
Create_connections()
state ="init"
print("All clients connected ")
time.sleep(5)
#
no_threads=threading.active_count()
print("current threads =",no_threads)
print("Publishing ")
Run_Flag=True
estado=0
try:
    while Run_Flag:
         for i in range(nclients):
            client=clients[i]["client"]
            msg=clients[i]["client_id"]+ ":" + "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC9wA27p3MJGj2uNLT8mpET4FjRWS8pe2LTVx1owJmb0Q3WPKoDjVKG1EsluHXWLR72KvYsD1lr8S6XhFR5uLa8DY5JvaBBY2XQrOqAvAbaNTPYebkj2346g3SnOCI25NnnItNv7xJKibo59ObgzbEr9Chkn4HOp0FRi+P9ANDTawIDAQAB"
            if client.connected_flag:
               client.publish('ppd/pubkey',msg,qos=2)
               time.sleep(1)
               # print(str(i) +" "+ client._client_id.decode("utf-8") + " published on topic init " + "msg: " +msg)
               # print('--',clients[i]['status'])
            i+=1

except KeyboardInterrupt:
   print("interrupted  by keyboard")
   
for client in clients:
   client.disconnect()
   client.loop_stop()
#allow time for allthreads to stop before existing
time.sleep(10)               
                                 
         
         