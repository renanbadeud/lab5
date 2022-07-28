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
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

clients=[
{"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['ppd/pubkey'],"pub_key":"""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCncrg200X3/ISEBDso1DSkWBoa
HJOasq/Gd7/VmrDjmH5XOHcs/jN9Ncy7ViNSVtpej0Prqq879griM+GKiF6l3Dl6
DJfVOdDSvNcTwbW9A01umzeyKIg9cLKV9djC1QU+8RFDnyhr2ccOQChYy4j/oAKU
QdcE6tLBiaWadRvAkQIDAQAB""",
 "priv_key":"""MIICXQIBAAKBgQCncrg200X3/ISEBDso1DSkWBoaHJOasq/Gd7/VmrDjmH5XOHcs
/jN9Ncy7ViNSVtpej0Prqq879griM+GKiF6l3Dl6DJfVOdDSvNcTwbW9A01umzey
KIg9cLKV9djC1QU+8RFDnyhr2ccOQChYy4j/oAKUQdcE6tLBiaWadRvAkQIDAQAB
AoGBAIUdIqqa6/2HJcVZI7qCb9LSIvXtD74kHK421i61ybc0rAMkZUFEV6RLF5U5
ldzIJNKVK5Z2WtXc86v9OGgLnskMWgQQii6laX549ndibLc1eKwfmvLnNen1zYgt
91z32fGVfh7DyofCiT0N55sr3w1dU+8KND9tZloDwOi1w76tAkEA1hG2sEEGgd4r
zMpiexc18IcWOsf++RZ6YoZ9CH1c+jYAZZJJ9+RHr1NhR6qZ/KXPVX/K4jxiG1Fe
RL5iMC5hVwJBAMg/PSUCZg7qRldsvULOQuZBzfIqyZONcy3l0ke3u2CDKbuvsssE
V/2TKO7viDMaChM+qncotU67i2dnHyglNFcCQQCtL+WKUQFPvgvXggEMrqmP7+pX
IgixQrM+1KmBXdMEBv5pLmIzcHdia+WvEmHEWe0Use/U+p8wlLLckN5lNpC/AkBB
sJUjXe0S+YGHznEryDQkCvQ/fA/SarWdGeZohnpeh8iZ/GI/vTYMRklIUKWyddlW
RNlw65bGtDlf+3E6HzJTAkAmtS4YuJPQbgIF/5npWjTAlhwfRHpTRVuLjIGI9PsU
3Z7V8zfqjvudRo1TpKQpZLcpfGmfmJu20fTd48hm9wDU"""},
{"broker":"127.0.0.1","port":1883,"name":"blank","sub_topic":['ppd/pubkey'],"pub_key":"""MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDFLnnDS4pxThwFRj4A9DG29SB9
vkra5z0sCIcyEtaAZMveqIidGrp7eC6d5sFbcE2cRQNtGJOktNuiLnuWd5YkASdd
4ifar6HyaJf3AvUGxqVnLlu/t3+7YjaZzfXxYGCKLLCJDKjQE5CAipHbQFzuhSno
VJeQu32C83AxxhinHQIDAQAB""","priv_key":"""MIICXQIBAAKBgQDFLnnDS4pxThwFRj4A9DG29SB9vkra5z0sCIcyEtaAZMveqIid
Grp7eC6d5sFbcE2cRQNtGJOktNuiLnuWd5YkASdd4ifar6HyaJf3AvUGxqVnLlu/
t3+7YjaZzfXxYGCKLLCJDKjQE5CAipHbQFzuhSnoVJeQu32C83AxxhinHQIDAQAB
AoGBAKGFub7OAaFhP7jeWmpDnvnlgPEgUYdSBx0r+zt8jPPuHcbOPeKcA4ii4WT9
owS5UQoiynSyvjcc5BHNi/WtDnIMN+C9J/q/i7e5Whr+LuzIX8QF7Pq1w2Gh6api
VK0t716wmNV9aGraD/HuVe5bPF9S0jkNMUbHraKHUqWjbHCBAkEA9u0ufroL6sjO
RBQm22eLu4JtZoUOyw2cItmFGWD/LlUGwAu2YycyPv78SVEOr9lEX8UzZvF6JaSG
aM4K09AWYQJBAMxtWN/rEZB7gl+vGHzEZT/w5jFfHwuOMBpbsRrEVp0WQQNKI4pd
Ac92VzR6k448ehjfkbmPbZyaSKNsntjAkj0CQHSfdwtBgallKA59WhDcKeHo6xS1
mVQL3IeVJsjiyAMxA1wm7ACOnaulMLDMCNzDCAkXkXx4ZpFq0FSlo/WAXWECQAG5
lntlN2O5txLpnlJHMfeFJ9wYymFFlOBUD72DFJwEuQ23DW+4czB19ixqMF6N4hXd
pRQkwq8EmkJOw1Re450CQQDT6//VEJeNJPRtcEiy/ajpQdHrI+abhGgl64OaPxRR
NU4f454elvTxuUsGYJE7cBBHluBlT9weiJcJ6eLAePWu"""}
]

nclients=len(clients)


def assina(message,priv_key):
   digest = SHA256.new()
   digest.update(message.encode('utf-8'))

   # Load private key previouly generated

   # Sign the message
   signer = PKCS1_v1_5.new(priv_key)
   sig = signer.sign(digest)

   # sig is bytes object, so convert to hex string.
   # (could convert using b64encode or any number of ways)
   print("Signature: ")
   print(sig.hex())

def verifica(message,pub_key):
       # message = "I want this stream signed"
   
   digest = SHA256.new()
   digest.update(message.encode('utf-8'))

   sig = input('Enter signature: ')
   sig = bytes.fromhex(sig)  # convert string to bytes object

   # Load public key (not private key) and verify signature
   verifier = PKCS1_v1_5.new(pub_key)
   verified = verifier.verify(digest, sig)

   

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
            
            msg=clients[i]["client_id"]+ ":" + clients[i]["pub_key"]
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
                                 
         
         
#allow time for allthreads to stop before existing
time.sleep(10)               
                                 
         
         