from mount import Plugin

class MyPlugin(Plugin):
    hostcommands = {}
    servercommands = {}

    def __init__(self):
        self.servercommands = {
            "hello": self.hello
        }
        print("I was loaded!")

    def hello(self, server, args):
        print("You called hello with args: ", args)
