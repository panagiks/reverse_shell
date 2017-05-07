from rspet.server.Plugins.mount import Plugin, command_basic

class MyPlugin(Plugin):
    """Example plugin. You can declare your commands in __server_commands__ or __host_commands__"""
    def __init__(self):
        """This function is called when the plugin is loaded"""
        print("Test plugin loaded!")

    @command_basic
    def hello(self, server, args):
        """Demo command that prints the arguments that you passed it"""
        print("You called hello with args: ", args)
