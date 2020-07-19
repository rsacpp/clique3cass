#!/usr/bin/python3
# 
# feeds3.py for Clique3
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

import os
import time
import sys
import signal
import psycopg2
import uuid
from datetime import datetime
from kazoo.client import KazooClient
from kazoo.recipe.queue import LockingQueue
sys.path.append('/the/path/of/util.py')
import util

def handle_exit(signum):
    sys.exit(0)

def freopen(f, mode, stream):
    oldf = open(f, mode)
    oldfd = oldf.fileno()
    newfd = stream.fileno()
    os.close(newfd)
    os.dup2(oldfd, newfd)

def feeds():
    try:
        conn = psycopg2.connect(util.conf().get('pgConn3'))
        cur = conn.cursor()

        #zkHost = "ZKHOST1234"
        zk = KazooClient(hosts=util.conf().get('zkCluster3'))
        zk.start()
        # 4 queues '3'
        aliasq = LockingQueue(zk, util.conf().get('alias3'))
        symbolq = LockingQueue(zk, util.conf().get('symbol3'))
        issueq = LockingQueue(zk, util.conf().get('issue3'))
        transferq = LockingQueue(zk, util.conf().get('transfer3'))

        # 2 more queues
        propIssueq = LockingQueue(zk, util.conf().get('proposeIssue'))
        propTranq = LockingQueue(zk, util.conf().get('proposeTran'))

        cur.execute("""select min(id) from alias_redo0 where progress = 1 and clique = '3' """)
        res = cur.fetchone()
        conn.commit()
        if res[0]:
            minAlias = res[0] - 1
        else:
            minAlias = -1

        cur.execute("""select min(id) from symbol_redo0 where progress = 1 and clique = '3'""")
        res = cur.fetchone()
        conn.commit()
        if res[0]:
            minSymbol = res[0] - 1
        else:
            minSymbol = -1

        cur.execute("""select min(id) from  issue_redo0 where progress = 1 and clique='3'""")
        res = cur.fetchone()
        conn.commit()
        if res[0]:
            minIssue = res[0] - 1
        else:
            minIssue = -1

        cur.execute("""select min(id) from  transfer_redo0 where progress = 1 and clique='3'""")
        res = cur.fetchone()
        conn.commit()
        if res[0]:
            minTransfer = res[0] - 1
        else:
            minTransfer = -1
        print('minAlias={0}, minSymbol={1}, minIssue={2}, minTransfer={3}'.format(minAlias,minSymbol,minIssue,minTransfer))
        cur.execute("""select min(id) from propose_issue where progress = 1""")
        res = cur.fetchone()
        conn.commit()
        if res[0]:
            minpropIssue = res[0] - 1
        else:
            minpropIssue = -1

        cur.execute("""select min(id) from propose_transfer where progress = 1""")
        res = cur.fetchone()
        conn.commit()
        if res[0]:
            minpropTran = res[0] - 1
        else:
            minpropTran = -1

        while True:
            ints = datetime.now()
            inload = os.getloadavg()[0]
            # process alias
            cur.execute("""select alias, "globalId" , id from alias_redo0 where progress = 1 and clique='3'
            and id > %s""", [minAlias])
            res = cur.fetchall()
            conn.commit()
            if res:
                for en in res:
                    aliasq.put("{0}||{1}".format(en[0].strip(), en[1].strip()).encode('utf-8'))
                    minAlias = en[2]

            # process symbol
            cur.execute("""select symbol, "globalId" , id from symbol_redo0 where progress = 1 and clique = '3'
            and id > %s""", [minSymbol])
            res = cur.fetchall()
            conn.commit()
            if res:
                for en in res:
                    symbolq.put("{0}||{1}".format(en[0].strip(), en[1].strip()).encode('utf-8'))
                    minSymbol = en[2]

            # process issue
            cur.execute("""select proposal ,id from issue_redo0 where progress = 1 and clique = '3'
            and id > %s""", [minIssue])
            res = cur.fetchall()
            conn.commit()
            if res:
                for en in res:
                    issueq.put("{0}".format(en[0].strip()).encode('utf-8'))
                    minIssue = en[1]

            # process transfer
            cur.execute("""select proposal,id from transfer_redo0 where progress = 1 and clique = '3'
            and id > %s""", [minTransfer])
            res = cur.fetchall()
            conn.commit()
            if res:
                for en in res:
                    transferq.put("{0}".format(en[0].strip()).encode('utf-8'))
                    minTransfer = en[1]
            # process proposeIssue
            cur.execute("""select symbol, quantity, "globalId",id from propose_issue where progress = 1 and id > %s
            """, [minpropIssue])
            res = cur.fetchall()
            conn.commit()
            if res:
                for en in res:
                    if not en[1] in [1, 2, 8]:
                        continue
                    propIssueq.put("{0}||{1}||{2}||{3}".format(en[0].strip(), en[1], en[2].strip(), en[3]).encode('utf-8'))
                    minpropIssue = en[3]

            # process proposeTransfer
            cur.execute("""select alias, "rawCode", lastsig3 , id, "globalId" from propose_transfer where progress = 1
            and id > %s""", [minpropTran])
            res = cur.fetchall()
            conn.commit()
            if res:
                for en in res:
                    propTranq.put("{0}&&{1}&&{2}&&{3}&&{4}".format(en[0].strip(), en[1].strip(), en[2].strip(), en[3], en[4].strip()).encode('utf-8'))
                    minpropTran = en[3]

            outts = datetime.now()
            outload = os.getloadavg()[0]

            time.sleep(1)
    except psycopg2.Error as err:
        print("SQLError {0}".format(err))
    finally:
        zk.stop()
        zk.close()
        cur.close()
        conn.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    pid = os.fork()
    if pid > 0:
        time.sleep(3)
        sys.exit(0)
    os.setsid()
    sys.stdin.close()
    freopen('/tmp/feeds3out', 'a', sys.stdout)
    freopen('/tmp/feeds3err', 'a', sys.stderr)
    feeds()
