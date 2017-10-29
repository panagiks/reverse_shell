'''

Written for DigitalOcean's Hacktoberfest!

Requires cx_Freeze and must be built on Windows :(
Unfortunately, neither cx_Freeze nor py2exe support cross platform compilation
thus, this particular solution was set into motion

'''

import sys
from cx_Freeze import setup, Executable

setup(
    name = "RSPET Test",            #Change these values to your liking
    version = "0.1",
    description = "A Test Executable",
    executables = [Executable("rspet_client.py", base = "Win32GUI")])