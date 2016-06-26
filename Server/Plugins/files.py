from mount import Plugin

class Files(Plugin):
    __server_commands__ = {}
    __host_commands__ = {}

    def __init__(self):
        self.__host_commands__["Pull_File"] = self.pull_file
        self.__host_commands__["Pull_Binary"] = self.pull_binary
        self.__host_commands__["Make_File"] = self.make_file
        self.__host_commands__["Make_Binary"] = self.make_binary

    def pull_file(self, host, args):
        """Pulls a regular text file from the host(s).
        Use it on a single selected host, otherwise each host will overwrite
        last's contents"""

        if len(args) == 0:
            print("Usage: Pull_File <remote_file> [local_file]")

        remote_file = args[0]
        try:
            local_file = args[1]
        except IndexError:
            local_file = remote_file

        host.send("00003")
        host.send("%03d" % len(remote_file))
        host.send(remote_file)

        if host.recv(3) == "fna":
            print("Something went bad...")
            return 2

        try:
            with open(local_file, "w") as fp:
                filesize = int(host.recv(13))
                fp.write(host.recv(filesize))
        except IOError:
            print("Cannot create local file")

    def pull_binary(self, host, args):
        """Pulls a binary file from the host(s).
        Use it on a single selected host, otherwise each host will overwrite
        last's contents"""

        if len(args) == 0:
            print("Usage: Pull_Binary <remote_file> [local_file]")

        remote_file = args[0]
        try:
            local_file = args[1]
        except IndexError:
            local_file = remote_file

        host.send("00004")
        host.send("%03d" % len(remote_file))
        host.send(remote_file)

        if host.recv(3) == "fna":
            print("Something went bad...")
            return 2

        try:
            with open(local_file, "wb") as fp:
                filesize = int(host.recv(13))
                fp.write(host.recv(filesize))
        except IOError:
            print("Cannot create local file")

    def make_file(self, host, args):
        """Sends a regular text file to the host(s)"""
        if len(args) == 0:
            print("Usage: Make_File <local_file> [remote_file]")

        local_file = args[0]
        try:
            remote_file = args[1]
        except IndexError:
            remote_file = local_file

        host.send("00001")
        host.send("%03d" % len(remote_file))
        host.send(remote_file)

        if host.recv(3) == "fna":
            print("Something went bad...")
            return 2

        with open(local_file) as fp:
            contents = fp.read()
            host.send("%013d" % len(contents))
            host.send(contents)
            host.recv(3) # What to do with this?

    def make_binary(self, host, args):
        """Sends a binary file to the host(s)"""
        if len(args) == 0:
            print("Usage: Make_Binary <local_file> [remote_file]")

        local_file = args[0]
        try:
            remote_file = args[1]
        except IndexError:
            remote_file = local_file

        host.send("00002")
        host.send("%03d" % len(remote_file))
        host.send(remote_file)

        if host.recv(3) == "fna":
            print("Something went bad...")
            return 2

        with open(local_file, "rb") as fp:
            contents = fp.read()
            host.send("%013d" % len(contents))
            host.send(contents)
            host.recv(3) # What to do with this?
