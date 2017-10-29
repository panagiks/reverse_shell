#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""RSPET Server's RESTful API."""
import argparse
import aiohttp_cors
import rspet.server.base
from aiohttp import web
from pluginbase import PluginBase
from rspet.server.decorators import route

__author__ = "Kolokotronis Panagiotis"
__copyright__ = "Copyright 2016, Kolokotronis Panagiotis"
__credits__ = ["Kolokotronis Panagiotis"]
__license__ = "MIT"
__version__ = "2.0"
__maintainer__ = "Kolokotronis Panagiotis"


def setup_route(app, descriptor):
    return app.router.add_route(**descriptor)


def make_plugin_routes(app, plugin_name):
    try:
        plugin = app['source'].load_plugin(plugin_name)
        routes = plugin.make_routes(app, plugin_name)
        for rt in routes:
            app['cors'].add(rt)
    except ImportError:
        pass
    except AttributeError as err:  # There probably was bo make_routes
        pass


def make_routes(app):
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    cors.add(
        app.router.add_route(
            method=plugin_list.http_method,
            path=plugin_list.endpoint,
            handler=plugin_list,
            name=plugin_list.name
        )
    )
    cors.add(
        app.router.add_route(
            method=plugin_create.http_method,
            path=plugin_create.endpoint,
            handler=plugin_create,
            name=plugin_create.name
        )
    )
    app['cors'] = cors
    for plugin in app['server'].loaded_plugins():
        make_plugin_routes(app, plugin)


@route('GET', '/plugin/', 'plugin_list')
async def plugin_list(request):
    server = request.app['server']
    if 'installed' in request.query:
        plugins = server.installed_plugins()
    elif 'loaded' in request.query:
        plugins = server.plugins["loaded"]
    else:
        plugins = server.available_plugins()
        plugins = {
            plugin: plugins[plugin]['doc']
            for plugin in plugins
        }
    plugins = [
        {
            "name": plugin,
            "doc": plugins[plugin]
        }
        for plugin in plugins
    ]
    return web.json_response({'plugins': plugins})


@route('POST', '/plugin/{plugin}/', 'plugin_create')
async def plugin_create(request, plugin):
    server = request.app['server']
    if 'install' in request.query:
        server.install_plugin(plugin)
    elif 'load' in request.query:
        server.load_plugin(plugin)
    else:
        return web.json_response(
            {'error': "You must specify an action in the request's query"},
            status=400
        )
    return web.Response(status=201)


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
    web.run_app(app)


if __name__ == '__main__':
    main()
