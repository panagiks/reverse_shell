# We use a decorator to mark a function as a command.
# Then, the PluginMount metaclass is called and it
# creates an actual object from each plugin's class
# and saves the methods needed.

# Suggestion: We could throw away the metaclass if we
# use simple functions (and not classes). Not sure if
# that would be useful


class PluginMount(type):
    def __init__(cls, name, base, attr):
        """Called when a Plugin derived class is imported

        Gathers all methods needed from __cmd_states__ to __server_cmds__"""

        tmp = cls()
        for fn in cls.__cmd_states__:
            cls.__server_cmds__[fn] = getattr(tmp, fn)


class Plugin(object):
    """Plugin class (to be extended by plugins)"""
    __metaclass__ = PluginMount

    __server_cmds__ = {}
    __cmd_states__ = {}
    __help__ = {}


def command(*states):
    def decorator(fn):
        Plugin.__cmd_states__[fn.__name__] = states

        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
