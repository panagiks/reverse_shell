"""
Plug-in module for RSPET server. Offer functions essential to server.
"""
import json
import requests
from aiohttp import web
from socket import error as sock_error
from rspet.server.decorators import command, installer, depends, route, router


@command("basic", "connected", "multiple")
def help(server, args):
    """List commands available in current state or provide syntax for a command.

    Help: [command]"""
    ret = [None, 0, ""]
    if len(args) > 1:
        ret[2] = ("Syntax : %s" % server.commands["help"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        ret[2] = server.help(args)
    return ret


@command("basic")
def list_hosts(server, args):
    """List all connected hosts."""
    ret = [None, 0, ""]
    hosts = server.get_hosts()
    if hosts:
        ret[2] += "Hosts:"
        for i in hosts:
            inf = hosts[i].info
            con = hosts[i].connection
            ret[2] += ("\n[%s] %s:%s %s-%s %s %s" % (
                i, con["ip"], con["port"],
                inf["version"], inf["type"],
                inf["systemtype"],
                inf["hostname"]))
    else:
        ret[2] += "No hosts connected to the Server."
    return ret


@command("connected", "multiple")
def list_sel_hosts(server, args):
    """List selected hosts."""
    ret = [None, 0, ""]
    hosts = server.get_selected()
    ret[2] += "Selected Hosts:"
    for host in hosts:
        # tmp = hosts[i]
        inf = host.info
        con = host.connection
        ret[2] += ("\n[%s] %s:%s %s-%s %s %s" % (
            host.id, con["ip"], con["port"],
            inf["version"], inf["type"],
            inf["systemtype"],
            inf["hostname"]))
    return ret


@command("basic")
def choose_host(server, args):
    """Select a single host.

    Help: <host ID>"""
    ret = [None, 0, ""]
    if len(args) != 1 or not args[0].isdigit():
        ret[2] = ("Syntax : %s" % server.commands["choose_host"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        ret[1], ret[2] = server.select([args[0]])
        ret[0] = "connected"
    return ret


@command("basic")
def select(server, args):
    """Select multiple hosts.

    Help: <host ID> [host ID] [host ID] ..."""
    ret = [None, 0, ""]
    if len(args) == 0:
        ret[2] = ("Syntax : %s" % server.commands["select"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        ret[1], ret[2] = server.select(args)
        ret[0] = "multiple"
    return ret


@command("basic")
def all(server, args):
    """Select all hosts."""
    ret = [None, 0, ""]
    ret[1], ret[2] = server.select(None)
    ret[0] = "all"
    return ret


@command("connected", "multiple")
def exit(server, args):
    """Unselect all hosts."""
    ret = [None, 0, ""]
    ret[0] = "basic"
    return ret


@command("basic")
def quit(server, args):
    """Quit the CLI and terminate the server."""
    ret = [None, 0, ""]
    server.quit()
    return ret


@command("connected", "multiple")
def close_connection(server, args):
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
def kill(server, args):
    """Stop host(s) from doing the current task."""
    ret = [None, 0, ""]
    hosts = server.get_selected()
    for host in hosts:
        try:
            host.send(host.command_dict['KILL'])
        except sock_error:
            host.purge()
            ret[0] = "basic"
            ret[1] = 2  # Socket Error Code
    return ret


@command("connected")
def execute(server, args):
    """Execute system command on host.

    Help: <command>"""
    ret = [None, 0, ""]
    host = server.get_selected()[0]
    if len(args) == 0:
        ret[2] = ("Syntax : %s" % server.commands["execute"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        command = " ".join(args)
        try:
            host.send(host.command_dict['command'])
            host.send(command)
            resp = ''
            try:
                resp = str(host.recv())
            except KeyboardInterrupt:
                kill(server, [])
            finally:
                resp = str(host.recv())
                ret[2] += resp
        except sock_error:
            host.purge()
            ret[0] = "basic"
            ret[1] = 2  # Socket Error Code
    return ret


############################################################################
###                        Server Plugin Section                         ###
############################################################################
@command("basic")
def install_plugin(server, args):
    """Download an official plugin (Install).

    Help: <plugin> [plugin] [plugin] ..."""
    ret = [None, 0, ""]
    for plugin in args:
        server.install_plugin(plugin)
    return ret


@command("basic")
def load_plugin(server, args):
    """Load an already installed plugin.

    Help: <plugin> [plugin] [plugin] ..."""
    ret = [None, 0, ""]
    for plugin in args:
        server.load_plugin(plugin)
    return ret


@command("basic")
def available_plugins(server, args):
    """List plugins available online."""
    ret = [None, 0, ""]
    avail_plug = server.available_plugins()
    ret[2] += "Available Plugins:"
    for plug in avail_plug:
        plug_dct = avail_plug[plug]
        ret[2] += ("\n\t%s: %s" % (plug, plug_dct["doc"]))
    return ret


@command("basic")
def installed_plugins(server, args):
    """List installed plugins."""
    ret = [None, 0, ""]
    inst_plug = server.installed_plugins()
    ret[2] += "Installed Plugins:"
    for plug in inst_plug:
        ret[2] += ("\n\t%s: %s" % (plug, inst_plug[plug]))
    return ret


@command("basic")
def loaded_plugins(server, args):
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
def client_install_plugin(server, args):
    """Install plugin to the selected client(s).

    Help: <plugin>"""
    ret = [None, 0, ""]
    if len(args) < 1:
        ret[2] = ("Syntax : %s" % server.commands["client_install_plugin"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        cmd = args[0]  # Get plugin name
        hosts = server.get_selected()
        # Read contents of plugin.
        with open("/etc/rspet/plugins/Client/" + cmd + ".client") as pl_file:
            code = pl_file.read()
        for host in hosts:
            try:
                host.send(host.command_dict["loadPlugin"])  # Send order
                host.send(cmd)  # Send plugin name
                host.send(code)  # Send plugin contents
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2  # Socket Error Code
    return ret


@command("connected", "multiple")
def plugin_command(server, args):
    """Execute a plugin's command to selected host(s).

    Help: <command> [args]"""
    ret = [None, 0, ""]
    if len(args) < 1:
        ret[2] = ("Syntax : %s" % server.commands["plugin_command"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    elif args[0] not in server.commands:
        ret[2] = ("Run 'Load_Plugin' first to load local handler.")
    else:
        cmd = args[0]  # Read command from args
        args.pop(0)  # Remove it from args
        hosts = server.get_selected()
        for host in hosts:
            if cmd not in host.info["commands"]:
                ret[2] += ("Command not available on client %d" % host.id)
                ret[0] = "basic"
                continue
            try:
                host.send(host.command_dict["runPluginCommand"])  # Send order
                host.send(cmd)  # Send command

                # TODO: Decide if args are handled centrally or by local handler.

                # host.send("%02d" % len(args)) # Send number of arguments
                # for arg in args:
                #     host.send("%02d" % len(arg)) # Send length of argument
                #     host.send(arg) # Send argument

                # Call local handler and pass remaining args
                res = server.commands[cmd](server, host, args)
                ret[2] += res[2]
                if res[0] is not None:
                    ret[0] = res[0]
                if res[1] != 0:
                    ret[1] = res[1]
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2  # Socket Error Code
    return ret


@command("basic", "connected", "multiple")
def available_client_plugins(server, args):
    """Get a list of the available client plugins from the selected repos."""
    ret = [None, 0, ""]
    server.plugins["available_client"] = {}
    for base_url in server.plugins["base_url"]:
        try:
            json_dct = requests.get(base_url + '/client_plugins.json').json()
        except json.decoder.JSONDecodeError:  # Plugin repo 404ed (probably)
            server._log("ERROR", "Error connecting to plugin repo %s" % base_url)
            ret[1] = 8  # PluginRepoUnreachable Error code
            continue
        for plugin in json_dct:
            if plugin not in server.plugins["available_client"]:
                server.plugins["available_client"][plugin] = json_dct[plugin]
        ret[2] += "Available Client Plugins"
        for plugin in server.plugins["available_client"]:
            plug_dct = server.plugins["available_client"][plugin]
            ret[2] += ("\n\t%s: %s" % (plugin, plug_dct["doc"]))
    return ret


@command("basic", "connected", "multiple")
def get_client_plugins(server, args):
    """Download Client Plugins from the selected repos.

    Help: <plugin> [plugin] [plugin] ..."""
    ret = [None, 0, ""]
    if len(args) < 1:
        ret[2] = ("Syntax : %s" % server.commands["get_client_plugins"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        # Force client plugin list refresh.
        server.available_client_plugins(server, args)
        avail_plug = server.plugins["available_client"]
        for plugin in args:
            try:
                plugin_url = server.plugins["available_client"][plugin]
            except KeyError:
                ret[2] += ("%s: plugin does not exist" % plugin)
            else:
                # Download the plugin and write it to a file.
                try:
                    plugin_cont = requests.get(plugin_url + ".py").text
                    plugin_cont_cl = requests.get(plugin_url + ".client").text
                # FIXME: Find the right way to test for failure to get plugin
                except json.decoder.JSONDecodeError:  # Plugin repo 404ed (most probably).
                    ret[2] += ("%s: plugin not available on server." % plugin)
                    server._log("ERROR", "%s: plugin not available on server." % plugin)
                else:
                    # Create the file for local handler.
                    with open(("/etc/rspet/plugins/%s.py" % plugin), 'w') as plugin_file:
                        plugin_file.write(plugin_cont)
                    # Create the file for client plugin
                    with open(("/etc/rspet/plugins/Clinet/%s.client" % plugin), 'w') as plugin_file:
                        plugin_file.write(plugin_cont_cl)
                    ret[2] += ("%s: Clinet plugin installed." % plugin)
                    server._log("DEBUG", "%s: Clinet plugin installed" % plugin)
    return ret


@command("basic", "connected", "multiple")
def create_client_profile(server, args):
    """Creates a client profile.

    Help: <profile_name> <plugin> [plugin]"""
    ret = [None, 0, ""]
    if not hasattr(server, "client_profile"):
        server.client_profile = {}
    server.client_profile.update({args[0]: args[1:]})
    return ret


@command("basic", "connected", "multiple")
def list_client_profiles(server, args):
    """Lists client profiles."""
    ret = [None, 0, ""]
    if hasattr(server, "client_profile"):
        for profile in server.client_profile:
            ret[2] += '\n%s:' % profile
            for plugin in server.client_profile[profile]:
                ret[2] += '\n\t%s' % plugin
    else:
        ret[2] = "No client profiles registered"
    return ret


@command("connected", "multiple")
def apply_client_profile(server, args):
    """Apply client profile to selected client(s).

    Help: <profile_name>"""
    ret = [None, 0, ""]
    if len(args) < 1:
        ret[2] = ("Syntax : %s" % server.commands["apply_client_profile"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        try:
            for plugin in server.client_profile[args[0]]:
                client_install_plugin(server, [plugin])
        except KeyError:
            ret[2] = "Client profile not found"
            ret[1] = 1  # FIXME: Add correct error number
    return ret


@depends('files:make_file')
@command("connected", "multiple")
def update_client(server, args):
    """Update selected client(s).

    Help: <new_client_file>"""
    ret = [None, 0, ""]
    if len(args) < 1:
        ret[2] = ("Syntax : %s" % server.commands["update_client"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        hosts = server.get_selected()
        for host in hosts:
            server.commands['make_file'](server, args)
            host.send(host.command_dict['update'])
            resp = host.recv()
            host.info['version'] = resp.split('-')[0]
    return ret


# REST API VEIWS

def extract_client(request, hid, host):
    return {
        'id': hid,
        'ip': host.connection['ip'],
        'port': host.connection['port'],
        'version': host.info['version'],
        'type': host.info['type'],
        'system': host.info['systemtype'],
        'hostname': host.info['hostname'],
        'uri': str(request.app.router['client_detail'].url_for(hid=hid))
    }


@route('GET', 'client/', 'client_list')
async def api_client_list(request):
    hosts = request.app['server'].get_hosts()
    if not hosts:
        return web.json_response({'error': 'No hosts found'}, status=404)
    else:
        clients = [
            extract_client(request, int(host), hosts[host])
            for host in hosts
        ]
        return web.json_response({'clients': clients})


@route('GET', 'client/{hid}/', 'client_detail')
async def api_client_detail(request, hid):
    try:
        clients = [
            extract_client(
                request,
                str(hid),
                request.app['server'].clients['hosts'][str(hid)]
            )
        ]
    except KeyError:
        return web.json_response(
            {'error': 'Host %s not found' % hid},
            status=404
        )
    return web.json_response({'clients': clients})


@route('POST', 'client/{hid}/close/', 'close_connection')
async def api_close_connection(request, hid):
    server = request.app['server']
    res = server.select([hid])
    if res[0] != 0:
        server.select([])
        return web.json_response(
            {'error': 'Host %s not found' % hid},
            status=404
        )
    server.commands['close_connection'](server, [])
    server.select([])
    return web.Response(status=204)


@route('POST', 'client/{hid}/shell/', 'execute_shell')
async def api_execute_shell(request, hid):
    try:
        body = await request.json()
        cmd = body['command']
        try:
            args = body['args']
        except KeyError:
            args = []
        args = [cmd, *args]
        command = ' '.join(args)
    except:
        pass  # Return an error ...
    try:
        host = request.app['server'].clients['hosts'][str(hid)]
    except KeyError:
        return web.json_response(
            {'error': 'Host %s not found' % hid},
            status=404
        )
    try:
        host.send(host.command_dict['command'])
        host.send(command)
        resp = ''
        resp = str(host.recv())
        resp = str(host.recv())
    except sock_error:
        host.purge()
    return web.json_response({"stdout": resp})


@route('POST', 'client/{hid}/kill/', 'kill_execution')
async def api_kill_execution(request, hid):
    server = request.app['server']
    res = server.select([hid])
    if res[0] != 0:
        server.select([])
        return web.json_response(
            {'error': 'Host %s not found' % hid},
            status=404
        )
    server.commands['kill'](server, [])
    server.select([])
    return web.Response(status=204)


def extract_help(request, cmd, command):
    return {
        'help': command.__help__,
        'states': command.__states__,
        'syntax': (
            command.__syntax__
            if hasattr(command, '__syntax__') else
            None
        ),
        'uri': str(request.app.router['help_detail'].url_for(cmd=cmd))
    }


@route('GET', 'help/', 'help_list')
async def api_help_list(request):
    commands = request.app['server'].commands
    help_dict = [
        extract_help(request, cmd, commands[cmd])
        for cmd in commands
    ]
    return web.json_response({'help': help_dict})


@route('GET', 'help/{cmd}/', 'help_detail')
async def api_help_detail(request, cmd):
    try:
        help_dict = [
            extract_help(request, cmd, request.app['server'].commands[cmd])
        ]
    except KeyError:
        return web.json_response(
            {'error': 'Command %s not found' % cmd},
            status=404
        )
    return web.json_response({'help': help_dict})


@installer(__name__)
def setup(app, commands):
    pass


@router(__name__)
def make_routes(app, name):
    pass
