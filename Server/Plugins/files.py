from mount import Plugin

class Files(Plugin):
    __server_commands__ = {}
    __host_commands__ = {}

    def __init__(self):
        self.__host_commands__["Pull_File"] = self.pull_file
        self.__host_commands__["Pull_Binary"] = self.pull_binary
        self.__host_commands__["Make_File"] = self.make_file
        self.__host_commands__["Make_Binary"] = self.make_binary

    def pull_file(self, client, args):
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

        client.send("00003")
        client.send("%03d" % len(remote_file))
        client.send(remote_file)

        if client.recv(3) == "fna":
            print("Something went bad...")
            return 2

        try:
            with open(local_file, "w") as fp:
                filesize = int(client.recv(13))
                fp.write(client.recv(filesize))
        except IOError:
            print("Cannot create local file")

    def pull_binary(self, client, args):
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

        client.send("00004")
        client.send("%03d" % len(remote_file))
        client.send(remote_file)

        if client.recv(3) == "fna":
            print("Something went bad...")
            return 2

        try:
            with open(local_file, "wb") as fp:
                filesize = int(client.recv(13))
                fp.write(client.recv(filesize))
        except IOError:
            print("Cannot create local file")

    def make_file(self, client, args):
        """Sends a regular text file to the host(s)"""
        if len(args) == 0:
            print("Usage: Make_File <local_file> [remote_file]")

        local_file = args[0]
        try:
            remote_file = args[1]
        except IndexError:
            remote_file = local_file

        client.send("00001")
        client.send("%03d" % len(remote_file))
        client.send(remote_file)

        if client.recv(3) == "fna":
            print("Something went bad...")
            return 2

        with open(local_file) as fp:
            contents = fp.read()
            client.send("%013d" % len(contents))
            client.send(contents)
            client.recv(3) # What to do with this?

    def make_binary(self, client, args):
        """Sends a binary file to the host(s)"""
        if len(args) == 0:
            print("Usage: Make_Binary <local_file> [remote_file]")

        local_file = args[0]
        try:
            remote_file = args[1]
        except IndexError:
            remote_file = local_file

        client.send("00002")
        client.send("%03d" % len(remote_file))
        client.send(remote_file)

        if client.recv(3) == "fna":
            print("Something went bad...")
            return 2

        with open(local_file, "rb") as fp:
            contents = fp.read()
            client.send("%013d" % len(contents))
            client.send(contents)
            client.recv(3) # What to do with this?
