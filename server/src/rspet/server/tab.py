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


def readline_completer(words):
    readline.set_completer(autocomplete(words).complete)
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set completion-ignore-case on')
