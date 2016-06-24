class PluginMount(type):
    """
    A plugin mount point derived from:
    http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    Acts as a metaclass which creates anything inheriting from Plugin
    """

    def __init__(cls, name, base, attr):
        """Called when a Plugin derived class is imported"""

        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls())
            print("%s was loaded" % name)

class Plugin(object):
    """A plugin which must provide a register_signals() method"""
    __metaclass__ = PluginMount
