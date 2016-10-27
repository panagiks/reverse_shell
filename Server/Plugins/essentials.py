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
        """List commands available in current state or provide syntax for a command."""
        ret = [None,0,""]
        if len(args) > 1:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["help"])
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            ret[2] = server.help(args)
        return ret

    def list_hosts(self, server, args):
        """List all connected hosts."""
        ret = [None,0,""]
        hosts = server.get_hosts()
        if hosts:
            ret[2] += "Hosts:"
            for i in hosts:
                tmp = hosts[i]
                ret[2] += ("\n[%s] %s:%s %s-%s %s %s" % (i, tmp.ip, tmp.port,
                                                        tmp.version, tmp.type,
                                                        tmp.systemtype,
                                                        tmp.hostname))
        else:
            ret[2] += "No hosts connected to the Server."
        return ret

    def list_sel_hosts(self, server, args):
        """List selected hosts."""
        ret = [None,0,""]
        hosts = server.get_selected()
        ret[2] += "Selected Hosts:"
        for tmp in hosts:
            #tmp = hosts[i]
            ret[2] += ("\n[%s] %s:%s %s-%s %s %s" % (tmp.id, tmp.ip, tmp.port,
                                                    tmp.version, tmp.type,
                                                    tmp.systemtype,
                                                    tmp.hostname))
        return ret

    def choose_host(self, server, args):
        """Select a single host."""
        ret = [None,0,""]
        if len(args) != 1 or not args[0].isdigit():
            ret[2] = ("Syntax : %s" % self.__cmd_help__["Choose_Host"])
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            ret[1], ret[2] = server.select([args[0]])
            ret[0] = "connected"
        return ret

    def select(self, server, args):
        """Select multiple hosts."""
        ret = [None,0,""]
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["Select"])
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            ret[1], ret[2] = server.select(args)
            ret[0] = "multiple"
        return ret

    def all(self, server, args):
        """Select all hosts."""
        ret = [None,0,""]
        ret[1], ret[2] = server.select(None)
        ret[0] = "all"
        return ret

    def exit(self, server, args):
        """Unselect all hosts."""
        ret = [None,0,""]
        ret[0] = "basic"
        return ret

    def quit(self, server, args):
        """Quit the CLI and terminate the server."""
        ret = [None,0,""]
        server.quit()
        return ret

    def close_connection(self, server, args):
        """Kick the selected host(s)."""
        ret = [None,0,""]
        hosts = server.get_selected()
        for host in hosts:
            host.trash()
        ret[0] = "basic"
        return ret

    def kill(self, server, args):
        """Stop host(s) from doing the current task."""
        ret = [None,0,""]
        hosts = server.get_selected()
        for host in hosts:
            try:
                host.send(host.command_dict['KILL'])
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2 # Socket Error Code
        return ret

    def execute(self, server, args):
        """Execute system command on host."""
        ret = [None,0,""]
        host = server.get_selected()[0]
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["Execute"])
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            command = " ".join(args)
            try:
                host.send(host.command_dict['command'])
                host.send("%013d" % len(command))
                host.send(command)
                respsize = int(host.recv(13))
                ret[2] += str(host.recv(respsize))
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2 # Socket Error Code
        return ret
