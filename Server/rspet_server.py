#!/usr/bin/env python2
class Console:
    """Class to interfere with the server"""
    def max_conns
    def server
    def prompt

    def __init__(self, max_conns=5):
        """Starts server"""
        self.max_conns = max_conns
        self.prompt = "~$ "
        self.server = Server()

    def loop(self):
        """Main CLI loop"""
        self._logo()

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
    def ip = "0.0.0.0"
    def port = "9000"
    def hosts = [] # List of hosts
    def selection = [] # List of selected hosts
    def plugins = [] # List of active plugins

    def __init__(self, ip=None, port=None):
        """Starts to listen on socket"""

    def __del__(self):
        """Safely closes all sockets"""

    def loop(self):
        """Main server loop. Better call it on its own thread"""

    def select(self, ids=None):
        """Selects given host(s) based on ids

        Keyword argument:
        ids     -- Array of ids of hosts. Empty array unselects all. None
        selects all
        """

    def exec(self, cmd, args):
        """Execute function on all client objects.

        Keyword argument:
        cmd     -- Function to call for each selected host.
        Function signature myfunc(Host, args[0], args[1], ...)
        It should accept len(args) - 1 arguments
        args    -- Arguments to pass to the command function"""

    def getHost(self, ids=None):
        """Get object(s) of given host(s) based on ids

        Keyword argument:
        ids     -- Array of ids of hosts. None means all.
        """

    def getSelection(self):
        """Get object(s) of currently selected host(s)"""

class Host:
    """Class for host. Each Host object represent one client"""
    def ip
    def port
    def version
    def type = "full"
    def sock

    def __init__(self, ip, port):
        """Accepts the connection and initializes variables"""

    def __del__(self):
        """Graceful deletion of host"""

    def loop(self):
        """Main loop to manage the host"""

    def send(self, msg):
        """Send message to host"""

    def recv(self, size):
        """Receive from host"""

    def ping(self):
        """Ping host"""

    def _enc(self, data):
        """Encrypt message (before send)"""

    def _dec(self, data):
        """Decrypt message (after receive)"""

if __name__ == "__main__":
    cli = Console()
    try:
        cli.loop(int(argv[1]))
    except IndexError:
        cli.loop()
