#!/usr/bin/env python2
# -*- coding: <UTF-8> -*-
from subprocess import Popen, PIPE
import pip

command = "openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 -subj \"/C=RT/ST=RT/L=RT/O=RT/CN=.\" -keyout Server/server.key -out Server/server.crt"
comm = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
stdout, stderr = comm.communicate()
pip.main(['install','Flask', 'flask-cors', '-q'])
