#!/usr/bin/python3
#
# importissuer.py for Clique3
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

from kazoo.client import KazooClient
import hashlib
import psycopg2
import sys
sys.path.append('/the/path/of/util.py')
import util
import os

zkHost = util.conf().get('zkCluster3')
dbConnectStr = util.conf().get('pgConn3')

f = open('d.key', 'r')
txt = ''
while True:
    en = f.readline()
    if(en == ''):
        break
    txt += en
f.close()

arr = txt.split('@@')
pq = arr[0].strip()
d = arr[1].strip()
alias = sys.argv[1]
symbol = sys.argv[2]

globalId = sys.argv[3]


conn = psycopg2.connect(dbConnectStr)

cur = conn.cursor()
zk = KazooClient(hosts=zkHost)
zk.start()
zkc = zk.Counter("/issuerId3", default=0x700)
zkc += 1
entryId = zkc.value
zk.stop()
zk.close()

sha256 = hashlib.sha256()
sha256.update('{0}'.format(entryId).encode('utf-8'))
hashCode = sha256.hexdigest()
print("entryId = {0}, hashCode = {1}".format(entryId, hashCode))

try:
    cur.execute("""
    insert into issuer0(id, clique, "globalId", pq, d, alias,symbol ,"hashCode", setup) values(%s, '3', %s, %s, %s, %s,%s, %s ,now())
    """, [int(entryId), globalId, pq, '', alias, symbol, hashCode])
    conn.commit()
    # mv the player file and step1 file to the target place
    # read the playerepo variable from db
    cur.execute(""" select val from con0 where param = 'playerepo3' """)
    playerepo = cur.fetchone()[0].strip()
    conn.commit()
    cur.execute(""" select val from con0 where param = 'step1repo3' """)
    step1repo = cur.fetchone()[0].strip()
    conn.commit()
    path = util.path(symbol)
    playerepo = '{0}/{1}/'.format(playerepo, path)
    step1repo = '{0}/{1}/'.format(step1repo, path)
    print("playerepo = {0}, step1repo = {1}".format(playerepo, step1repo))
    os.popen("mv issuer{0}.py {1}".format(symbol, playerepo))
    os.popen("mv issuer{0}    {1}".format(symbol, playerepo))
    os.popen("mv step1{0}    {1}".format(symbol, step1repo))
except psycopg2.Error as err:
    print("ERROR {0}".format(err))
cur.close()
conn.close()
