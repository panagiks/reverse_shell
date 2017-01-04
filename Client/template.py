from rspet_client import Plugin

class MyPlugin(Plugin):
    """Example plugin. You can declare your commands in __server_commands__ or __host_commands__"""
    __server_commands__ = {}

    def __init__(self):
        """This function is called when the plugin is loaded"""
        self.__server_commands__["hello"] = self.hello
        print("Test plugin loaded!")

    def hello(self, server, args):
        """Demo command that prints the arguments that you passed it"""
        print("You called hello with args: ", args)
