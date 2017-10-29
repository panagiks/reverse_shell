import re
import sys
from functools import wraps

# Prepare the regex to parse help
regex = re.compile("(.+)\n\n\s*Help: (.+)", re.M)


# We use this decorator to mark a function as a command.
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


def depends(*deps):
    def decorator(fn):
        if not hasattr(fn, '__is_command__'):
            raise RuntimeError("@depends decorator can only be used on commands")
        fn.__depends__ = [
            {
                'plugin': dep.split(':')[0],
                'command': dep.split(':')[1]
            }
            for dep in deps
        ]

        @wraps(fn)
        def decorated(*args, **kwargs):
            srv = args[0]
            errors = [
                dep for dep in fn.__depends__
                if dep['plugin'] not in srv.loaded_plugins() or dep['command'] not in srv.commands
            ]
            dp = fn.__depends__[0]
            errors = list(errors)
            if errors:
                ret = [None, 0, ""]
                ret[1] = 8  # UnmetDependencies
                ret[2] = "Some dependencies of command %s " % fn.__name__
                ret[2] += "were not found:"
                for error in errors:
                    ret[2] += "\n * command '{}' of plugin '{}'".format(
                        error['command'],
                        error['plugin']
                    )
                return ret
            else:
                return fn(*args, **kwargs)
        return decorated
    return decorator


def route(method, endpoint, name=None):
    def decorator(fn):
        fn.__is_route__ = True
        fn.http_method = method.upper()
        fn.endpoint = endpoint
        if name:
            fn.name = name

        @wraps(fn)
        def decorated(*args, **kwargs):
            return fn(*args, **kwargs, **args[0].match_info)
        return decorated
    return decorator


def router(module):
    def decorator(fn):
        def decorated(*args, **kwargs):
            commands = [
                cmd for cmd in map(
                    lambda el: getattr(sys.modules[module], el),
                    dir(sys.modules[module])
                )
                if hasattr(cmd, '__is_route__')
            ]
            for cmd in commands:
                if not cmd.endpoint or cmd.endpoint.startswith('/'):
                    raise RuntimeError("Plugin endpoints cannot be blank or start with '/'!")
                descriptor = {
                    'method': cmd.http_method,
                    'path': '/plugin/{}/'.format(args[1]) + cmd.endpoint,
                    'handler': cmd
                }
                if hasattr(cmd, 'name'):
                    descriptor['name'] = cmd.name
                args[0]['setup_route'](args[0], descriptor)
        return decorated
    return decorator


# We use this decorator to mark a dummy function as the plugin's installer
# Function name MUST be setup and its contents WILL be ignored
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
