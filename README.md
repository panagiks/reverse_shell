# RSPET

![MIT Licence](https://img.shields.io/badge/Licence-MIT_Licence-red.svg?style=plastic)
[![Python 2.7](https://img.shields.io/badge/Python-2.7-yellow.svg?style=plastic)](https://www.python.org/)
![v0.2.6](https://img.shields.io/badge/Release-v0.2.6-orange.svg?style=plastic)
![Maintained](https://img.shields.io/badge/Maintained-Yes-green.svg?style=plastic)
[![Twitter](https://img.shields.io/badge/Twitter-@TheRSPET-blue.svg?style=plastic)](https://twitter.com/theRSPET)

> RSPET (Reverse Shell and Post Exploitation Tool) is a Python based reverse shell equipped with functionalities that assist in a post exploitation scenario.

DISCLAIMER: This software is provided for educational and PenTesting purposes and as a proof of concept. The developer(s) do not endorse, incite or in any other way support unauthorised computer access and networks disruption.

NOTE: As of v0.0.3 folder `min` has been added. Since the new version has many more features not essential to the main functionality (a reverse shell that is), min will not recieve any more features beyond v0.0.3 and will only get bug and performance related fixes.

Current Version: `v0.2.6`

Follow: [@TheRSPET](https://twitter.com/TheRSPET) on Twitter for updates.

Documentation : [rspet.readthedocs.io](http://rspet.readthedocs.io)

## Features

* Remote Command Execution
* Trafic masking (XORed instead of cleartext); for better results use port 443[1]
* Built-in File/Binary transfer (both ways) over the masked traffic
* Built-in UDP Flooding tool
* Built-in UDP Spoofing tool[2]
* Multiple/All Hosts management; order File/Binary transfer and UDP Flood from Multiple/All connected Hosts
* Modular Code Design to allow easy customization
* Client script is tested and is compatible with PyInstaller (can be made into .exe)[3]
* Full server side plug-in support.[4]
* RESTful API for the Server Module.

*[1]The idea for XORing as well as the skeleton for the client came from [primalsecurity.net](http://www.primalsecurity.net) so if you like this pack of scripts you'll probably love what they do

*[2]UDP Spoofing uses RAW_SOCKETS so in order to utilize it, the client has to run on an OS that supports RAW_SOCKETS (most Unix-Based) and with root privilages. Finally, most of the ISPs have implementations in place that will either drop or re-structure spoofed packets

*[3]Again check [primalsecurity.net's](http://www.primalsecurity.net) perfect blogpost about producing an .exe

*[4]Detailed documentation on creating plugins available in [Online Documentation](http://rspet.readthedocs.io/en/latest/dev/)!

## Deployment:

* `rspet_server.py` or `RSPET_server_min.py` is situated at the attacker's machine and running to accept connections
* `rspet_client.py` or `RSPET_client_min.py` is situated in the infected machine(s) and will initiate the connection and wait for input. 

## Execution:

* Server:
```sh
python rspet_server.py (max_connections) 
```
max_connections defaults to 5 if left blank

* RESTful API:
  * Install Flask with pip
  
    ```sh
    pip2 install Flask
    ```
  * Start the API
  
    ```sh
    python rspet_server_api.py
    ```

* Client: 
```sh
python rspet_client.py server_ip
```

Many changes can be made to fit individual needs.

As always if you have any suggestion, bug report or complain feel free to contact me.

## Distros
> A list of Distros that contain RSPET

* [BlackArch Linux](http://blackarch.org/tools.html) (as of version 2016.04.28)
* [ArchStrike](https://archstrike.org/packages/search/rspet)

## As Featured in

* [seclist.us](http://seclist.us/rspet-reverse-shell-and-post-exploitation-tool.html)
* [sillycon.org](http://www.sillycon.org/stories/article/github-panagiksrspet-rspet-reverse-shell-and-post-exploitation-tool-is-a-python-based-reverse-shell-equipped-with-functionalities-that-assist-in-a-post-exploitation-scenario)
* [digitalmunition.me](https://www.digitalmunition.me/2016/04/rspet-reverse-shell-post-exploitation-tool/)
* [n0where.net](https://n0where.net/reverse-shell-post-exploitation-tool/)
* [kitploit.com](http://www.kitploit.com/2016/05/rspet-python-reverse-shell-and-post.html)
* [Hakin9 IT Security Magazine](https://www.facebook.com/hakin9mag/posts/1376368245710855)

## Todo

- [x] ~~Fix logic bug where if a direct command to Host OS has no output Server displays command not recognized~~
- [ ] Fix logic bug where if a direct command's to Host OS execution is perpetual the Server deadlocks
- [x] ~~Add client version and type (min or full) as a property when client connects and at `List_Hosts`~~
- [ ] Add client update mechanism
- [ ] Add UDP Reflection functionality (already in the workings)
- [ ] Provide more settings via config file
- [ ] Re-introduce multythreading when handling multiple hosts.
- [ ] Make commands available with 'Tab' automatically generated based on loaded plugins.
- [ ] Fix logical bug when deleting a client. (Client still shows up on List_Hosts)
- [x] ~~Create comprehensive plug-in creation guide.~~

## Styleguide

This project is following [Google's Python Styleguide](https://google.github.io/styleguide/pyguide.html) with a minor variation on the use of whitespaces to align ":" tokens.

## Contribution Opportunities

This project is open for contributors. If you have implemented a new feature, or maybe an improvement to the current code feel free to open a pull request. If you want to sugest a new feature open an issue. Additionally Testers are needed to run a few standard scenarios (and a few of their own maybe) to decrease the chance a bug slips into a new version. Should there be any interest about testing a `beta` branch will be created (where code to be tested will be uploaded) along with a list of scenarios.

## Author - Project Owner/Manager

[panagiks](https://twitter.com/panagiks)

## Co-Author

[dzervas](https://dzervas.gr) -- Code (Server OO-redesign, Server Plug-in system implementation, bug reports, bug fixes)

## Contributors

* [b3mb4m](https://github.com/b3mb4m) -- Code (tab.py and bug fixes)
* [junzy](https://github.com/junzy) -- Docstings (udp_spoof & udp_spoof_send)

## License

MIT
