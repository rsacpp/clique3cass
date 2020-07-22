#!/usr/bin/python3
#
# clienttemp2.py for Clique3
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

import sys
from kafka import KafkaProducer,KafkaConsumer
from subprocess import Popen, PIPE
from sys import argv

sys.path.append('./util.py')
import util

disp = ''
alias = 'USERID'
raw = argv[1]
lastdig = argv[2]
globalId = argv[3]
last_block = argv[4]
raw = "{0}::{1}@@{2}@@{3}".format(alias, raw, lastdig, last_block)

print("raw = {0}\n".format(raw))

s1 = "{0}{1}{2}".format("^^", raw, "$$")

#for i in range(0, len(s1)):
#    v = s1[i:i+1]
#    code = ord(v)
#    for j in range(0, 4):
#        v0 = (code >> (4 * j)) & 0xf
#        disp += "{0:x}".format(v0)
disp = str(binascii.b2a_hex(bytes(s1, 'utf-8')), 'utf-8')

folder = '{0}/{1}'.format(util.conf().get('playerepo3'), util.path('USERID'))
print('folder = {0}'.format(folder))
pro1 = Popen(['./payerUSERID', disp], stdin=None, stdout=PIPE, cwd=folder)
output = pro1.communicate()[0].decode().strip()
output = output.rstrip('0')

print("output = {0}".format(output))
kafkaproducer = KafkaProducer(bootstrap_servers='localhost:9092')
kafkaproducer.send('transfer3', key=bytes('{0}||{1}'.format(globalId, output), 'utf-8'), key=bytes('{0}||{1}'.format(globalId, output), 'utf-8'))
kafkaproducer.flush()

