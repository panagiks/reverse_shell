from mount import Plugin

class Essentials(Plugin):
    __server_commands__ = {}
    __host_commands__ = {}

    def __init__(self):
        self.__server_commands__["List_Commands"] = [self.list_commands, "basic",
                                                     "connected", "multiple"]
        self.__server_commands__["List_Hosts"] = [self.list_hosts, "basic"]
        self.__server_commands__["List_Sel_Hosts"] = [self.list_sel_hosts,
                                                      "connected", "multiple"]
        self.__server_commands__["Choose_Host"] = [self.choose_host, "basic"]
        self.__server_commands__["Select"] = [self.select, "basic"]
        self.__server_commands__["ALL"] = [self.all, "basic"]
        self.__server_commands__["Exit"] = [self.exit, "connected", "multiple"]
        self.__server_commands__["Quit"] = [self.quit, "basic"]
        self.__server_commands__["Close_Connection"] = [self.close_connection,
                                                        "connected", "multiple"]
        self.__host_commands__["KILL"] = [self.kill, "connected", "multiple"]
        self.__host_commands__["Execute"] = [self.execute, "connected"]

    def list_commands(self, server, args):
        """List all availble commands."""
        server.help()
        return None

    def list_hosts(self, server, args):
        """List all connected hosts."""
        for i in range(len(server.hosts)):
            tmp = server.hosts[i]
            print("[%d] %s:%s\t%s-%s" % (i, tmp.ip, tmp.port, tmp.version, tmp.type))
        return None

    def list_sel_hosts(self, server, args):
        """List selected hosts."""
        for i in range(len(server.selected)):
            tmp = server.selected[i]
            print("[%d] %s:%s\t%s-%s" % (i, tmp.ip, tmp.port, tmp.version, tmp.type))
        return None

    def choose_host(self, server, args):
        """Select a single host."""
        if len(args) != 1:
            print("Usage: Choose_Host <id>")
            return None
        server.select([args[0]])
        return "connected"

    def select(self, server, args):
        """Select a multiple hosts."""
        if len(args) == 0:
            print("Usage: Select <id [id [id ...]]>")
            return None
        server.select(args)
        return "selected"

    def all(self, server, args):
        """Select all hosts."""
        server.select(None)
        return "all"

    def exit(self, server, args):
        """Unselect all hosts."""
        server.select([])
        return "basic"

    def quit(self, server, args):
        """Quit the CLI."""
        server.quit()

    def close_connection(self, server, args):
        """Kick the selected host(s)."""
        for host in server.selected:
            host.send(host.command_dict['killMe'])
            del host

        server.clean()
        return "basic"

    def kill(self, host, args):
        """Stop host(s) from doing the current task."""
        host.send(host.command_dict['KILL'])
        return None

    def execute(self, host, args):
        """Execute system command on host(s)."""
        if len(args) == 0:
            print("Usage: Execute <command>")
            #return None
        else:
            command = " ".join(args)

            host.send(host.command_dict['command'])
            host.send("%013d" % len(command))
            host.send(command)

            respsize = int(host.recv(13))
            print(host.recv(respsize))
        return None
