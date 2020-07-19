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
import psycopg2
from subprocess import Popen, PIPE
import sys
sys.path.append('/the/path/of/util.py')
import util

dbConnectStr = util.conf().get('pgConn3')
disp = ''

raw = argv[1]
globalId = argv[2]

print("raw = {0}\n".format(raw))

s1 = "{0}{1}{2}".format("^^", raw, "$$")

for i in range(0, len(s1)):
    v = s1[i:i+1]
    code = ord(v)

    for j in range(0, 4):
        v0 = (code >> (4 * j)) & 0xf
        disp += "{0:x}".format(v0)

folder = '{0}/{1}'.format(util.conf().get('playerepo3'), util.path('SYMBOL'))
print('folder = {0}'.format(folder))
pro1 = Popen(['./issuerSYMBOL', disp], stdin=None, stdout=PIPE, cwd=folder)
output = pro1.communicate()[0].decode().strip()
output = output.rstrip('0')

print("output = {0}".format(output))

step0 = output
# insert it to issue_redo
try:
    conn = psycopg2.connect(dbConnectStr)
    cur = conn.cursor()
    cur.execute("""
    insert into issue_redo0("globalId", clique, proposal, setup, progress) values
    ( %s, '3', %s, now(), 1)
    """, [globalId, step0.strip()])

    conn.commit()
    cur.close()
    conn.close()
except psycopg2.Error as err:
    print("SQLError {0}".format(err))
