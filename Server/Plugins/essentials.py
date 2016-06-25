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

    def list_commands(self, server, args):
        server.help()

    def list_hosts(self, server, args):
        for i in range(len(server.hosts)):
            tmp = server.hosts[i]
            print("[%d] %s:%s\t%s-%s" % (i, tmp.ip, tmp.port, tmp.version, tmp.type))

    def choose_host(self, server, args):
        server.select([args[0]])

    def select(self, server, args):
        server.select(args)

    def all(self, server, args):
        server.select(None)

    def exit(self, server, args):
        server.select([])

    def close_connection(self, server, args):
        for host in server.selection:
            del selhost

        server.clean()
