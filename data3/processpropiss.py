#!/usr/bin/python3
#
# processpropiss.py for Clique3
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


def getsymbol(pq):
    symbol = ''
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""select symbol from issuer0 where pq = %s and clique = '3'
        """, [pq.strip()])
        symbol = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()
    return symbol.strip()


def getpath(symbol):
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
    return '{0}/{1}'.format(path, util.path(symbol))


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


def checkcount(symbol, noteId):
    count = -1
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""select count(*) from ownership0 where
        clique = '3' and symbol=%s and "noteId"=%s
        """, [symbol, noteId])
        count = cur.fetchone()[0]
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()
    return count


def updateRedo(textin, status):
    print("proposal = {0}".format(textin))
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""update issue_redo0 set progress=%s, setup = now() where proposal =%s and clique = '3'
        """, [status, textin])
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()


def save2ownershipcatalog(pq, verdict, proposal, rawtext, symbol, noteId, quantity, target):
    zk = KazooClient(hosts=zkHost)
    zk.start()
    zkc = zk.Counter("/ownershipId3", default=0x700)
    zkc += 1
    ownershipId = zkc.value
    print("ownershipId={0}".format(ownershipId))
    zkc = zk.Counter("/noteId3", default=0x700)
    zkc += 1
    rowId = zkc.value
    print("rowId={0}".format(rowId))

    zk.stop()
    zk.close()
    sha256 = hashlib.sha256()
    sha256.update("{0}{1}".format(noteId.strip(), target.strip()).encode('utf-8'))
    hashcode = sha256.hexdigest()
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        cur.execute("""insert into ownership0(id, clique, symbol,"noteId", quantity,owner,updated,"hashCode")values(%s, '3',%s,%s,%s,%s,now(),%s)
        """, [int(ownershipId), symbol.strip(), noteId.strip(), quantity.strip(), target.strip(), hashcode.strip()])
        conn.commit()
        cur.execute("""insert into note_catalog0(id, clique, pq , verdict, proposal, note, recipient, hook, stmt, setup, "hashCode")values(%s,'3',%s,%s,%s,%s, %s, %s,%s,now(),%s)
        """, [int(rowId), pq.strip(), verdict.strip(), proposal.strip(), "{0}||{1}||{2}".format(symbol.strip(), noteId.strip(), quantity.strip()), target.strip(), '', rawtext.strip(), hashcode.strip()])
        conn.commit()
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        cur.close()
        conn.close()


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
symbol = getsymbol(pq)
step1path = getpath(symbol)
runCmd = '{0}/step1{1}'.format(step1path, symbol)

pro3 = Popen([runCmd, proposal, checksum0], stdin=None, stdout=PIPE)
verdict = pro3.communicate()[0].decode().strip()
verdict = verdict.rstrip('0')

runCmd = './step2'
pro2 = Popen([runCmd, pq, verdict], stdin=None, stdout=PIPE)
note = pro2.communicate()[0].decode().strip()
print("verdict={0} note={1}".format(verdict, note))

# if it the wrong verdict, upate the redo to status 4 then exit
if not note.startswith('e500e500'):
    updateRedo(textin, 4)
    sys.exit(0)
rawtext = encodefromhex(note)

target = rawtext.split('->')[1][:-2]
symbol = rawtext.split('->')[0].split('||')[0][2:]
noteId = rawtext.split('->')[0].split('||')[1]
quantity = rawtext.split('->')[0].split('||')[2]
# check whether the note is already in place

zk = KazooClient(hosts=zkHost)
zk.start()
lock0 = zk.Lock(symbol + noteId, 'data3')
with lock0:
    count = checkcount(symbol, noteId)
    if count != 0:
        # update the issue_redo with status code
        print("the note {0} symbol {1} is already in place".format(noteId, symbol))
        updateRedo(textin, 3)
        # insert one notification
    else:
        # save both the ownerhsip and catalog to db
        save2ownershipcatalog(pq.strip(), verdict.strip(), proposal.strip(), rawtext.strip(), symbol.strip(), noteId.strip(), quantity.strip(), target.strip())
        # update the issue_redo set progress to 0
        print("update Redo to 0")
        updateRedo(textin, 0)
zk.stop()
zk.close()
