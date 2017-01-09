import re

# We use a decorator to mark a function as a command.
# Then, the PluginMount metaclass is called and it
# creates an actual object from each plugin's class
# and saves the methods needed.


class PluginMount(type):
    def __init__(cls, name, base, attr):
        """Called when a Plugin derived class is imported

        Gathers all methods needed from __cmd_states__ to __server_cmds__"""

        tmp = cls()
        for fn in cls.__cmd_states__:
            # Load the function (if its from the current plugin) and see if
            # it's marked. All plugins' commands are saved as function names
            # without saving from which plugin they come, so we have to mark
            # them and try to load them
            try:
                f = getattr(tmp, fn)
                if f.__is_command__:
                    cls.__server_cmds__[fn] = f
            except AttributeError:
                pass


# Suggestion: We could throw away the metaclass if we
# use simple functions (and not classes). Not sure if
# that would be useful
class Plugin(object):
    """Plugin class (to be extended by plugins)"""
    __metaclass__ = PluginMount

    __server_cmds__ = {}
    __cmd_states__ = {}


# Prepare the regex to parse help
regex = re.compile("(.+)\n\n\s*Help: (.+)", re.M)

def command(*states):
    def decorator(fn):
        Plugin.__cmd_states__[fn.__name__] = states

        rmatch = regex.search(fn.__doc__)
        fn.__is_command__ = True # Mark function for loading
        fn.__help__ = fn.__doc__

        if rmatch is not None:
            fn.__help__ = rmatch.groups()[0]
            fn.__syntax__ = rmatch.groups()[1]

        return fn
    return decorator
