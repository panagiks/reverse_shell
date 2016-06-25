from mount import Plugin

class MyPlugin(Plugin):
    __host_commands__ = {}
    __server_commands__ = {}

    def __init__(self):
        self.__server_commands__ = {
            "hello": self.hello
        }
        print("I was loaded!")

    def hello(self, server, args):
        """Demo command that prints the arguments that you passed it"""
        print("You called hello with args: ", args)
