#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
from __future__ import print_function
import shutil
import argparse
import sys
import os
from threading import Thread
from subprocess import Popen, PIPE


def serverCall(api, num_of_clients, ip, port):
    if api:
        os.system(("cd test/server/ && ./api.py -c %d --ip %s -p %d" %
                    (num_of_clients, ip, port)))
    else:
        os.system(("cd test/server/ && ./base.py -c %d --ip %s -p %d" %
                    (num_of_clients, ip, port)))


def clientCall(clientNo):
    comm = Popen(("cd test/client/cl%d && ./rspet_client.py 127.0.0.1" % clientNo), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = comm.communicate()
    if stderr:
        decode = stderr.decode('UTF-8')
    elif stdout:
        decode = stdout.decode('UTF-8')
    else:
        decode = 'Command has no output'
    print(decode)


def main():
    parser = argparse.ArgumentParser(description='Automate test deployment.')
    parser.add_argument("-c", "--clients", nargs=1, type=int, metavar='N',
                        help="Number of clients to spawn.", default=[5])
    parser.add_argument("--rest", action='store_true', help="Invoke the RESTful WebAPI.")
    parser.add_argument("--ip", nargs=1, type=str, metavar='IP',
                        help="IP to listen for incoming connections.",
                        default=["0.0.0.0"])
    parser.add_argument("-p", "--port", nargs=1, type=int, metavar='PORT',
                        help="Port number to listen for incoming connections.",
                        default=[9000])
    args = parser.parse_args()

    num_of_clients = int(args.clients[0])

    try:
        shutil.copytree("src/rspet/server", "test/server")
    except OSError:
        pass

    for i in range(0, num_of_clients):
        try:
            shutil.copytree("src/rspet/client", ("test/client/cl%d" %i))
        except OSError:
            pass

    f_jobs = []
    for i in range(0, num_of_clients):
        thr = Thread(target=clientCall, args=[i])
        f_jobs.append(thr)
    thr = Thread(target=serverCall, args=[args.rest, args.clients[0], args.ip[0],
                args.port[0]])
    f_jobs.append(thr)
    for k in f_jobs:
        k.start()
    for k in f_jobs:
        k.join()

    shutil.rmtree("test/")

if __name__ == '__main__':
    main()
