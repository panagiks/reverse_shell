from mount import Plugin

class Files(Plugin):
    __server_commands__ = {}
    __host_commands__ = {}

    def __init__(self):
        self.__host_commands__["Pull_File"] = [self.pull_file, "connected"]
        self.__host_commands__["Pull_Binary"] = [self.pull_binary, "connected"]
        self.__host_commands__["Make_File"] = [self.make_file, "connected",
                                               "multiple"]
        self.__host_commands__["Make_Binary"] = [self.make_binary, "connected",
                                                 "multiple"]

    def pull_file(self, host, args):
        """Pull a regular text file from the host."""

        if len(args) == 0:
            print("Usage: Pull_File <remote_file> [local_file]")
        else:
            remote_file = args[0]
            try:
                local_file = args[1]
            except IndexError:
                local_file = remote_file

            host.send(host.command_dict['sendFile'])
            host.send("%03d" % len(remote_file))
            host.send(remote_file)

            if host.recv(3) == "fna":
                print("Something went bad...")
            else:
                try:
                    with open(local_file, "w") as fp:
                        filesize = int(host.recv(13))
                        fp.write(host.recv(filesize))
                except IOError:
                    print("Cannot create local file")
        return None

    def pull_binary(self, host, args):
        """Pull a binary file from the host(s)."""

        if len(args) == 0:
            print("Usage: Pull_Binary <remote_file> [local_file]")
        else:
            remote_file = args[0]
            try:
                local_file = args[1]
            except IndexError:
                local_file = remote_file

            host.send(host.command_dict['sendBinary'])
            host.send("%03d" % len(remote_file))
            host.send(remote_file)

            if host.recv(3) == "fna":
                print("Something went bad...")s
            else:
                try:
                    with open(local_file, "wb") as fp:
                        filesize = int(host.recv(13))
                        fp.write(host.recv(filesize))
                except IOError:
                    print("Cannot create local file")
        return None

    def make_file(self, host, args):
        """Send a regular text file to the host(s)"""
        if len(args) == 0:
            print("Usage: Make_File <local_file> [remote_file]")
        else:
            local_file = args[0]
            try:
                remote_file = args[1]
            except IndexError:
                remote_file = local_file

            host.send(host.command_dict['getFile'])
            host.send("%03d" % len(remote_file))
            host.send(remote_file)

            if host.recv(3) == "fna":
                print("Something went bad...")
            else:
                with open(local_file) as fp:
                    contents = fp.read()
                    host.send("%013d" % len(contents))
                    host.send(contents)
                    host.recv(3) #For future use?
        return None

    def make_binary(self, host, args):
        """Send a binary file to the host(s)"""
        if len(args) == 0:
            print("Usage: Make_Binary <local_file> [remote_file]")
        else:
            local_file = args[0]
            try:
                remote_file = args[1]
            except IndexError:
                remote_file = local_file

            host.send(host.command_dict['getBinary'])
            host.send("%03d" % len(remote_file))
            host.send(remote_file)

            if host.recv(3) == "fna":
                print("Something went bad...")
            else:
                with open(local_file, "rb") as fp:
                    contents = fp.read()
                    host.send("%013d" % len(contents))
                    host.send(contents)
                    host.recv(3) # For future use?
        return None
