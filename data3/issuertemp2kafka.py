#!/usr/bin/python3
#
# issuertemp2.py for Clique3
# Copyright (C) 2018, Gu Jun
#
# This file is part of Clique3.
# Clique3 is  free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

# Clique3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Clique3. If not, see <http://www.gnu.org/licenses/>.

from sys import argv
from kafka import KafkaProducer
from subprocess import Popen, PIPE
import binascii
import sys
sys.path.append('./util.py')
import util


disp = ''

raw = argv[1]
globalId = argv[2]

print("raw = {0}\n".format(raw))

s1 = "{0}{1}{2}".format("^^", raw, "$$")
disp = str(binascii.b2a_hex(bytes(s1, 'utf-8')), 'utf-8')

playerrepo = '/tmp/var/player'

folder = '{0}/{1}'.format(playerrepo, util.path('SYMBOL'))
print('folder = {0}'.format(folder))
pro1 = Popen(['./issuerSYMBOL', disp], stdin=None, stdout=PIPE, cwd=folder)
output = pro1.communicate()[0].decode().strip()
output = output.rstrip('0')

print("output = {0}".format(output))

step0 = output
kafkaproducer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
kafkaproducer.send('issue3', key=bytes('{0}||{1}'.format(globalId, step0.strip()), 'utf-8'), value=bytes('{0}||{1}'.format(globalId, step0.strip()), 'utf-8'))
kafkaproducer.flush()
