"""
Plug-in module for RSPET server. Offer remote file inclusion functions.
"""
from aiohttp import web
from socket import error as sock_error
from rspet.server.decorators import command, installer, route, router


@command("connected")
def pull_file(server, args):
    """Pull a regular text file from the host.

    Help: <remote_file> [local_file]"""
    ret = [None, 0, ""]
    host = server.get_selected()[0]
    if len(args) == 0:
        ret[2] = ("Syntax : %s" % server.commands["pull_file"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        remote_file = args[0]
        try:
            local_file = args[1]
        except IndexError:
            local_file = remote_file
        try:
            host.send(host.command_dict['sendFile'])
            host.send(remote_file)
            if host.recv() == "fna":
                ret[2] += "File does not exist or Access Denied"
                ret[1] = 4  # Remote Access Denied Error Code
            else:
                try:
                    with open(local_file, "w") as file_obj:
                        file_obj.write(host.recv())
                except IOError:
                    ret[2] += "Cannot create local file"
                    ret[1] = 3  # Local Access Denied Error Code
        except sock_error:
            host.purge()
            ret[0] = "basic"
            ret[1] = 2  # Socket Error Code
    return ret


@command("connected")
def pull_binary(server, args):
    """Pull a binary file from the host.

    Help: <remote_bin> [local_bin]"""
    ret = [None, 0, ""]
    host = server.get_selected()[0]
    if len(args) == 0:
        ret[2] = ("Syntax : %s" % server.commands["pull_binary"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        remote_file = args[0]
        try:
            local_file = args[1]
        except IndexError:
            local_file = remote_file
        try:
            host.send(host.command_dict['sendBinary'])
            host.send(remote_file)
            if host.recv() == "fna":
                ret[2] += "File does not exist or Access Denied"
                ret[1] = 4  # Remote Access Denied Error Code
            else:
                try:
                    with open(local_file, "wb") as file_obj:
                        file_obj.write(host.recv())
                except IOError:
                    ret[2] += "Cannot create local file"
                    ret[1] = 3  # Local Access Denied Error Code
        except sock_error:
            host.purge()
            ret[0] = "basic"
            ret[1] = 2  # Socket Error Code
    return ret


@command("connected", "multiple")
def make_file(server, args):
    """Send a regular text file to the host(s).

    Help: <local_file> [remote_file]"""
    ret = [None, 0, ""]
    hosts = server.get_selected()
    if len(args) == 0:
        ret[2] = ("Syntax : %s" % server.commands["make_file"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        local_file = args[0]
        try:
            remote_file = args[1]
        except IndexError:
            remote_file = local_file.split("/")[-1]
        for host in hosts:
            try:
                host.send(host.command_dict['getFile'])
                host.send(remote_file)
                if host.recv() == "fna":
                    ret[2] += "Access Denied"
                    ret[1] = 4  # Remote Access Denied Error Code
                else:
                    with open(local_file) as file_obj:
                        contents = file_obj.read()
                        host.send(contents)
                        host.recv()  # For future use?
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2  # Socket Error Code
            except IOError:
                ret[1] = 3  # LocalAccessError Code
                ret[2] += "File not found!"
    return ret


@command("connected", "multiple")
def make_binary(server, args):
    """Send a binary file to the host(s).

    Help: <local_bin> [remote_bin]"""
    ret = [None, 0, ""]
    hosts = server.get_selected()
    if len(args) == 0:
        ret[2] = ("Syntax : %s" % server.commands["make_binary"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        local_file = args[0]
        try:
            remote_file = args[1]
        except IndexError:
            remote_file = local_file.split("/")[-1]
        for host in hosts:
            try:
                host.send(host.command_dict['getBinary'])
                host.send(remote_file)
                if host.recv() == "fna":
                    ret[2] += "Access Denied"
                    ret[1] = 4  # Remote Access Denied Error Code
                else:
                    with open(local_file, "rb") as file_obj:
                        contents = file_obj.read()
                        host.send(contents)
                        host.recv()  # For future use?
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2  # Socket Error Code
            except IOError:
                ret[1] = 3  # LocalAccessError Code
                ret[2] += "File not found!"
    return ret


# REST API VEIWS

async def file_helper(request, func):
    try:
        body = await request.json()
        args = [body['source']]
        try:
            args.append(body['destination'])
        except KeyError:
            pass
        clients = body['clients']
    except:
        pass  # Return an error ...
    server = request.app['server']
    res = server.select(clients)
    if res[0] != 0:
        server.select([])
        return web.json_response(
            {'error': 'Host %s not found' % hid},
            status=404
        )
    func(server, args)
    return web.Response(status=201)


@route('POST', 'pull_file/', 'pull_file')
async def api_pull_file(request):
    return (await file_helper(request, pull_file))


@route('POST', 'pull_binary/', 'pull_binary')
async def api_pull_binary(request):
    return (await file_helper(request, pull_binary))


@route('POST', 'make_file/', 'make_file')
async def api_make_file(request):
    return (await file_helper(request, make_file))


@route('POST', 'make_binary/', 'make_binary')
async def api_make_binary(request):
    return (await file_helper(request, make_binary))


@installer(__name__)
def setup(app, commands):
    pass


@router(__name__)
def make_routes(app, name):
    pass
