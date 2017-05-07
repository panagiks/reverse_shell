"""
Plug-in module for RSPET server. Offer remote file inclusion functions.
"""
from __future__ import print_function
from socket import error as sock_error
from rspet.server.Plugins.mount import Plugin, command


class Files(Plugin):
    """
    Class expanding Plugin.
    """

    @command("connected")
    def pull_file(self, server, args):
        """Pull a regular text file from the host.

        Help: <remote_file> [local_file]"""
        ret = [None,0,""]
        host = server.get_selected()[0]
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["Pull_File"])
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            remote_file = args[0]
            try:
                local_file = args[1]
            except IndexError:
                local_file = remote_file
            try:
                host.send(host.command_dict['sendFile'])
                host.send("%03d" % len(remote_file))
                host.send(remote_file)
                if host.recv(3) == "fna":
                    ret[2] += "File does not exist or Access Denied"
                    ret[1] = 4 # Remote Access Denied Error Code
                else:
                    try:
                        with open(local_file, "w") as file_obj:
                            filesize = int(host.recv(13))
                            file_obj.write(host.recv(filesize))
                    except IOError:
                        ret[2] += "Cannot create local file"
                        ret[1] = 3 # Local Access Denied Error Code
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2 # Socket Error Code
        return ret

    @command("connected")
    def pull_binary(self, server, args):
        """Pull a binary file from the host.

        Help: <remote_bin> [local_bin]"""
        ret = [None,0,""]
        host = server.get_selected()[0]
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["Pull_Binary"])
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            remote_file = args[0]
            try:
                local_file = args[1]
            except IndexError:
                local_file = remote_file
            try:
                host.send(host.command_dict['sendBinary'])
                host.send("%03d" % len(remote_file))
                host.send(remote_file)
                if host.recv(3) == "fna":
                    ret[2] += "File does not exist or Access Denied"
                    ret[1] = 4 # Remote Access Denied Error Code
                else:
                    try:
                        with open(local_file, "wb") as file_obj:
                            filesize = int(host.recv(13))
                            file_obj.write(host.recv(filesize))
                    except IOError:
                        ret[2] += "Cannot create local file"
                        ret[1] = 3 # Local Access Denied Error Code
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2 # Socket Error Code
        return ret

    @command("connected", "multiple")
    def make_file(self, server, args):
        """Send a regular text file to the host(s).

        Help: <local_file> [remote_file]"""
        ret = [None,0,""]
        hosts = server.get_selected()
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["Make_File"])
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            local_file = args[0]
            try:
                remote_file = args[1]
            except IndexError:
                remote_file = local_file.split("/")[-1]
            for host in hosts:
                try:
                    host.send(host.command_dict['getFile'])
                    host.send("%03d" % len(remote_file))
                    host.send(remote_file)
                    if host.recv(3) == "fna":
                        ret[2] += "Access Denied"
                        ret[1] = 4 # Remote Access Denied Error Code
                    else:
                        with open(local_file) as file_obj:
                            contents = file_obj.read()
                            host.send("%013d" % len(contents))
                            host.send(contents)
                            host.recv(3) # For future use?
                except sock_error:
                    host.purge()
                    ret[0] = "basic"
                    ret[1] = 2 # Socket Error Code
                except IOError:
                    ret[1] = 3 # LocalAccessError Code
                    ret[2] += "File not found!"
        return ret

    @command("connected", "multiple")
    def make_binary(self, server, args):
        """Send a binary file to the host(s).

        Help: <local_bin> [remote_bin]"""
        ret = [None,0,""]
        hosts = server.get_selected()
        if len(args) == 0:
            ret[2] = ("Syntax : %s" % self.__cmd_help__["Make_Binary"])
            ret[1] = 1 # Invalid Syntax Error Code
        else:
            local_file = args[0]
            try:
                remote_file = args[1]
            except IndexError:
                remote_file = local_file.split("/")[-1]
            for host in hosts:
                try:
                    host.send(host.command_dict['getBinary'])
                    host.send("%03d" % len(remote_file))
                    host.send(remote_file)
                    if host.recv(3) == "fna":
                        ret[2] += "Access Denied"
                        ret[1] = 4 # Remote Access Denied Error Code
                    else:
                        with open(local_file, "rb") as file_obj:
                            contents = file_obj.read()
                            host.send("%013d" % len(contents))
                            host.send(contents)
                            host.recv(3) # For future use?
                except sock_error:
                    host.purge()
                    ret[0] = "basic"
                    ret[1] = 2 # Socket Error Code
                except IOError:
                    ret[1] = 3 # LocalAccessError Code
                    ret[2] += "File not found!"
        return ret
