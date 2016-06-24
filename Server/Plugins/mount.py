class PluginMount(type):
    """
    A plugin mount point derived from:
    http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    Acts as a metaclass which creates anything inheriting from Plugin
    """

    def __init__(cls, name, base, attr):
        """Called when a Plugin derived class is imported

        Gathers all hostcommands to hostcmds
        and all servercommands to servercmds"""

        if not hasattr(cls, "hostcmds") or not hasattr(cls, "servercmds"):
            cls.servercmds = {}
            cls.hostcmds = {}
        else:
            tmp = cls()
            for cmd in tmp.hostcommands:
                cls.hostcmds[cmd] = tmp.hostcommands[cmd]
            for cmd in tmp.servercommands:
                cls.servercmds[cmd] = tmp.servercommands[cmd]
            print("%s was loaded" % name)

class Plugin(object):
    """Plugin class (to be extended by plugins)"""
    __metaclass__ = PluginMount
