#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
from subprocess import Popen, PIPE
import pip

#Format and execute command to generate RSPET server's RSA key.
command = "openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 -subj \"/C=RT/ST=RT/L=RT/O=RT/CN=.\" -keyout Server/server.key -out Server/server.crt"
comm = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
stdout, stderr = comm.communicate()
#Install dependencies for RESTful WebAPI.
pip.main(['install','Flask', 'flask-cors', '-q'])
