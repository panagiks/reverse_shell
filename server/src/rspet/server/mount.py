import re
import sys

# We use a decorator to mark a function as a command.
# Prepare the regex to parse help
regex = re.compile("(.+)\n\n\s*Help: (.+)", re.M)


def command(*states):
    def decorator(fn):
        # Setup function states
        fn.__states__ = states
        # Declare function as a command
        fn.__is_command__ = True
        # Extract Help and Syntax from docstring
        if fn.__doc__:
            rmatch = regex.search(fn.__doc__)
            fn.__help__ = fn.__doc__

            if rmatch is not None:
                fn.__help__ = rmatch.groups()[0]
                fn.__syntax__ = rmatch.groups()[1]
        else:
            fn.__help__ = ""
            fn.__syntax__ = ""

        return fn
    return decorator


def installer(module):
    def decorator(fn):
        def decorated(*args, **kwargs):
            commands = [
                cmd for cmd in map(
                    lambda el: getattr(sys.modules[module], el),
                    dir(sys.modules[module])
                )
                if hasattr(cmd, '__is_command__')
            ]
            for cmd in commands:
                args[0].setup_command(cmd.__name__, cmd)
        return decorated
    return decorator
