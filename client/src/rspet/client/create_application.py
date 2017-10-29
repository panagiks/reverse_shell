

"""

This particular file is not necessary, it just makes it easier to build the windows application from
an IDE or within another instance of RSPET.  This could be implemented in the server application to build
client executables.


"""

import subprocess

subprocess.call(["python", "setup.py", "build"])