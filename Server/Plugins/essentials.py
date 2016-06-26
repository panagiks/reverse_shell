from mount import Plugin

class Essentials(Plugin):
    __server_commands__ = {}
    __host_commands__ = {}

    def __init__(self):
        self.__server_commands__["List_Commands"] = self.list_commands
        self.__server_commands__["List_Hosts"] = self.list_hosts
        self.__server_commands__["Choose_Host"] = self.choose_host
        self.__server_commands__["Select"] = self.select
        self.__server_commands__["ALL"] = self.all
        self.__server_commands__["Exit"] = self.exit
        self.__server_commands__["Close_Connection"] = self.close_connection

        self.__host_commands__["KILL"] = self.kill
        self.__host_commands__["Execute"] = self.execute

    def list_commands(self, server, args):
        """List all availble commands"""
        server.help()

    def list_hosts(self, server, args):
        """List all connected hosts"""
        for i in range(len(server.hosts)):
            tmp = server.hosts[i]
            print("[%d] %s:%s\t%s-%s" % (i, tmp.ip, tmp.port, tmp.version, tmp.type))

    def choose_host(self, server, args):
        """Select a single host"""
        if len(args) != 1:
            print("Usage: Choose_Host <id>")
            return
        server.select([args[0]])

    def select(self, server, args):
        """Select a multiple hosts"""
        if len(args) == 0:
            print("Usage: Select <id [id [id ...]]>")
            return

        server.select(args)

    def all(self, server, args):
        """Select a all hosts"""
        server.select(None)

    def exit(self, server, args):
        """Unselect all hosts"""
        server.select([])

    def close_connection(self, server, args):
        """Kick the selected host(s)"""
        for host in server.selected:
            host.send("00000")
            del selhost

        server.clean()

    def kill(self, host, args):
        """Stop host(s) from doing the current task"""
        host.send("00008")

    def execute(self, host, args):
        """Execute system command on host(s)"""
        if len(args) == 0:
            print("Usage: Execute <command>")
            return

        command = " ".join(args)

        host.send("00007")
        host.send("%013d" % len(command))
        host.send(command)

        respsize = int(host.recv(13))
        print(host.recv(respsize))
