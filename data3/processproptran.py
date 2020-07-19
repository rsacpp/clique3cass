#!/usr/bin/python3
#
# processproptran.py for Clique3
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
import psycopg2
import hashlib
from kazoo.client import KazooClient
from subprocess import Popen, PIPE
sys.path.append('/the/path/of/util.py')
import util
dbConnectStr = util.conf().get('pgConn3')
zkHost = util.conf().get('zkCluster3')


def mapcode(c):
    if ord(c) >= 97 and ord(c) <= 102:
        return ord(c) - 87
    if ord(c) >= 65 and ord(c) <= 70:
        return ord(c) - 55
    if ord(c) >= 48 and ord(c) <= 57:
        return ord(c) - 48


def encodefromhex(s):
    re = ''
    for i in range(0, len(s), 4):
        v = 0
        tmp = s[i: i + 4]
        c0 = tmp[0]; c1 = tmp[1]; c2 = tmp[2]; c3 = tmp[3]
        v += mapcode(c0)
        v += mapcode(c1) << 4
        v += mapcode(c2) << 8
        v += mapcode(c3) << 12
        if v > 0:
            re = "{0}{1}".format(re, chr(v))
    return re


def getalias(pq):
    alias = ''
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""select alias from player0 where pq = %s and clique = '3'
        """, [pq.strip()])
        alias = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()
    return alias.strip()


def getpath(alias):
    path = ''
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute(""" select val from con0 where param = 'step1repo3' """)
        path = cur.fetchone()[0].strip()
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()
    return '{0}/{1}'.format(path, util.path(alias))


def getparam(clique):
    pq = ''
    d = ''
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""select pq,d from params0 where clique=%s
        """, [clique.strip()])
        res = cur.fetchone()
        pq = res[0]
        d = res[1]
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()
    return pq, d


def verify(pq, symbol, noteId, quantity, lastdig):
    # 1.ownership
    # 2.lastdig
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""select count(*) from ownership0 a, player0 b where a.owner = b.alias and b.pq = %s and a.symbol = %s and a."noteId"= %s and a.quantity= %s and a.clique = '3' and b.clique = '3'
        """, [pq, symbol, noteId, quantity])
        count = cur.fetchone()[0]
        conn.commit()
        if count == 1:
            cur.execute("""select count(*) from note_catalog0 where hook = %s and note = %s and clique = '3'
            """, [lastdig, "{0}||{1}||{2}".format(symbol, noteId, quantity)])
            count = cur.fetchone()[0]
            conn.commit()
            cur.execute("""
            select verdict from note_catalog0 where clique = '3' and note = %s order by id desc limit 1
            """, ["{0}||{1}||{2}".format(symbol, noteId, quantity)])
            verdict = cur.fetchone()[0]
            verdict = verdict.strip()
            conn.commit()
            if count == 0 and verdict.endswith(lastdig) and len(lastdig) == 16:
                return True
            else:
                return False
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()
    return False


def updateRedo(textin, status):
    print("proposal= {0}, staus = {1}".format(textin, status))
    try:
        conn = psycopg2.connect(dbConnectStr)

        cur = conn.cursor()
        cur.execute("""update transfer_redo0 set progress=%s, setup = now() where proposal =%s and clique = '3'
        """, [status, textin])
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()


def save2ownershipcatalog(pq, verdict, proposal, rawtext, symbol, noteId, quantity, target, lastsig):
    zk = KazooClient(hosts=zkHost)
    zk.start()
    zkc = zk.Counter("/noteId3", default=0x7000)
    zkc += 1
    rowId = zkc.value
    print("rowId={0}".format(rowId))
    zk.stop()
    zk.close()
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""update ownership0 set owner= %s , updated = now() where symbol = %s and "noteId"= %s and quantity= %s and clique = '3'
        """, [target.strip(), symbol.strip(), noteId.strip(), quantity.strip()])
        conn.commit()
        # save the entry to note_catalog table
        sha256 = hashlib.sha256()
        sha256.update("{0}{1}".format(noteId.strip(), target.strip()).encode('utf-8'))
        hashcode = sha256.hexdigest()
        cur.execute("""insert into note_catalog0(id, clique, pq , verdict, proposal, note, recipient, hook, stmt, setup, "hashCode")values(%s, '3', %s,%s,%s,%s,%s,%s,%s,now(),%s)
        """, [int(rowId), pq.strip(), verdict.strip(), proposal.strip(), "{0}||{1}||{2}".format(symbol.strip(), noteId.strip(), quantity.strip()), target.strip(), lastsig.strip(), rawtext.strip(), hashcode.strip()])
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close


textin = sys.argv[1]
arr = textin.split('@@')
pq = arr[0].strip()
proposal = arr[1].strip()

conn = psycopg2.connect(dbConnectStr)
cur = conn.cursor()
simplepq, simpled = getparam('3')
runCmd = './step1'
pro1 = Popen([runCmd, simplepq, simpled, proposal[-16:]], stdin=None, stdout=PIPE)
checksum0 = pro1.communicate()[0].decode().strip()
checksum0 = checksum0.rstrip('0')
alias = getalias(pq)
step1path = getpath(alias)

runCmd = '{0}/step1{1}'.format(step1path, alias)
pro1 = Popen([runCmd, proposal, checksum0], stdin=None, stdout=PIPE)
verdict = pro1.communicate()[0].decode().strip()
verdict = verdict.rstrip('0')

runCmd = './step2'
pro2 = Popen([runCmd, pq, verdict], stdin=None, stdout=PIPE)
note = pro2.communicate()[0].decode().strip()

note = note.strip()
if not note.startswith('e500e500'):
    updateRedo(textin, 4)
    sys.exit(0)

rawtext = encodefromhex(note)
print("rawtext = {0}".format(rawtext))

target = rawtext.split('->')[1].split('@@')[0]
lastsig = rawtext.split('->')[1].split('@@')[1][:-2]
symbol = rawtext.split('->')[0].split('||')[0][2:].split('::')[1]
noteId = rawtext.split('->')[0].split('||')[1]
quantity = rawtext.split('->')[0].split('||')[2]
# check whether the note is already in place

zk = KazooClient(hosts=zkHost)
zk.start()
lock0 = zk.Lock(symbol + noteId, 'data3')
with lock0:
    print("pq={0} symbol={1} noteId={2} quantity={3} lastsig={4}".format(pq, symbol, noteId, quantity, lastsig))
    if verify(pq.strip(), symbol.strip(), noteId.strip(), quantity.strip(), lastsig.strip()):
        # save both the ownerhsip and catalog to db
        save2ownershipcatalog(pq.strip(), verdict.strip(), proposal.strip(), rawtext.strip(), symbol.strip(), noteId.strip(), quantity.strip(), target.strip(), lastsig.strip())
        updateRedo(textin.strip(), 0)
    else:
        # update the transfer_redo with status code
        print("the note {0} symbol {1} lastsig {2} has been transfered already".format(noteId, symbol, lastsig))
        updateRedo(textin.strip(), 3)
zk.stop()
zk.close()
