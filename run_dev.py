#!/usr/bin/env python2
# -*- coding: <UTF-8> -*-
from __future__ import print_function
import shutil
import argparse
import sys
import os
from threading import Thread
from subprocess import Popen, PIPE


def serverCall(api):
    if api:
        os.system("cd test/Server/ && ./rspet_server_api.py")
    else:
        os.system("cd test/Server/ && ./rspet_server.py")


def clientCall(clientNo):
    comm = Popen(("cd test/Client/cl%d && ./rspet_client.py 127.0.0.1" % clientNo), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
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
                        help="Number of clients to spawn.")
    parser.add_argument("--rest", action='store_true', help="Invoke the RESTful WebAPI.")
    args = parser.parse_args()

    try:
        num_of_clients = int(args.clients[0])
    except IndexError:
        num_of_clients = 3
    except ValueError:
        print("Argument must be int! Exitting ...")
        sys.exit()

    try:
        shutil.copytree("Server", "test/Server")
    except OSError:
        pass

    for i in range(0, num_of_clients):
        try:
            shutil.copytree("Client", ("test/Client/cl%d" %i))
        except OSError:
            pass

    f_jobs = []
    for i in range(0, num_of_clients):
        thr = Thread(target=clientCall, args=[i])
        f_jobs.append(thr)
    thr = Thread(target=serverCall, args=[args.rest])
    f_jobs.append(thr)
    for k in f_jobs:
        k.start()
    for k in f_jobs:
        k.join()


if __name__ == '__main__':
    main()
