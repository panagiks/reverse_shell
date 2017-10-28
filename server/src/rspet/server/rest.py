#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""RSPET Server's RESTful API."""
import argparse
import rspet.server.base
from aiohttp import web
from pluginbase import PluginBase

__author__ = "Kolokotronis Panagiotis"
__copyright__ = "Copyright 2016, Kolokotronis Panagiotis"
__credits__ = ["Kolokotronis Panagiotis"]
__license__ = "MIT"
__version__ = "1.1"
__maintainer__ = "Kolokotronis Panagiotis"


def setup_route(app, descriptor):
    app.router.add_route(**descriptor)


def make_plugin_routes(app, plugin_name):
    try:
        plugin = app['source'].load_plugin(plugin_name)
        plugin.make_routes(app, plugin_name)
    except ImportError:
        pass
    except AttributeError as err:  # There probably was bo make_routes
        pass


def make_routes(app):
    for plugin in app['server'].loaded_plugins():
        make_plugin_routes(app, plugin)


def main():
    parser = argparse.ArgumentParser(description='RSPET Server module.')
    parser.add_argument("-c", "--clients", nargs=1, type=int, metavar='N',
                        help="Number of clients to accept.", default=[5])
    parser.add_argument("--ip", nargs=1, type=str, metavar='IP',
                        help="IP to listen for incoming connections.",
                        default=["0.0.0.0"])
    parser.add_argument("-p", "--port", nargs=1, type=int, metavar='PORT',
                        help="Port number to listen for incoming connections.",
                        default=[9000])
    args = parser.parse_args()
    app = web.Application()
    app['setup_route'] = setup_route
    app['RSPET_API'] = rspet.server.base.API(
        args.clients[0], args.ip[0], args.port[0]
    )
    app['server'] = app['RSPET_API'].get_server()
    plugin_base = PluginBase(
        package='rspet.server.rest.plugins',
        searchpath=['/etc/rspet/plugins']
    )
    app['source'] = plugin_base.make_plugin_source(
        searchpath=['/etc/rspet/plugins'],
        identifier='rspet.rest'
    )
    make_routes(app)
    print(app.router.routes()._routes)
    web.run_app(app)


if __name__ == '__main__':
    main()
