#CHANGELOG

**NEW IN V0.0.5

**Features:

  -`RSPET_server.py` and `RSPET_client.py` added UDP spoofing

NEW IN V0.0.4

Features:
  
  -`RSPET_client.py` and `RSPET_client_min.py` code cleanup
  
  -`RSPET_server.py` and `RSPET_server_min.py` partially rewritten; Partial modularity achieved.
  
  -`RSPET_server.py` and `RSPET_server_min.py` bug-fix when calling `Make_File`/`Make_Binary` with bad input
  
Todo/Known Bugs:

  -Merge `ALL` and `Select` interfaces
  
  -Add UDP Reflection functionality

NEW IN V0.0.3

Features:

  -Built-in UDP Flood capabilities
  
  -Multiple/All host managment; can now transfer Files/Binaries to Multiple/All connected host and order a UDP Flood
  
  -Code cleanup; even more Chunks of code were moved into functions

Todo/Known Bugs:

  -The current model dictates the server should wait for the completion of an excecuted command (when excecuting command directly to the client's OS) so that any output can be sent to the server and be desplayed. This creates deadlocks when the executed command a) has no output or b) is a script/process ment to run endlessly.   
  
NEW IN V0.0.2

Features:

  -Text and Binary file transfer (both ways) over the masked trafic (no OS-specific commands, no extra Ports/limitations)

  -Code cleanup; Chunks of code were moved into functions

Todo/Known Bugs:

  -The current model dictates the server should wait for the completion of an excecuted command (when excecuting command directly to the client's OS) so that any output can be sent to the server and be desplayed. This creates deadlocks when the executed command a) has no output or b) is a script/process ment to run endlessly. 

Features:

-Reverse TCP/IP connection, circumventing victim-side firewall roules (in most cases) and NAT limitations.

-Trafic Masking. All traffic is sent XORed and not in clear text. For better masking swap port to 443.[1]

-Support for multiple connections. The Server part is built with support for multiple simulatneus connections, with Hosts list managment.

-Client script is tested and is compatible with PyInstaller (can be made into .exe).[2]

*[1]The idea for XORing as well as the skeleton for the client came from (http://www.primalsecurity.net) so if you like this pack of scripts you'll probably love what they do

*[2]Again check primalsecurity.net's perfect blogpost about producing an .exe
