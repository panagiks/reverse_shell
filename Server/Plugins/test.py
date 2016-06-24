from gen import Plugin

class MyPlugin(Plugin):
    def __init__(self):
        print("I was loaded!")

    def hello(self):
        print("world")
