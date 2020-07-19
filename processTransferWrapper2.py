#!/usr/bin/python3
#
# processTransferWrapper2.py for Clique3
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
import os
import psycopg2
import time
import signal
from kazoo.client import KazooClient
from kazoo.recipe.queue import LockingQueue
from datetime import datetime
from subprocess import Popen
sys.path.append('/the/path/of/util.py')
import util

executable = 'processTransferWrapper2'
zkHost = util.conf().get('zkCluster3')
dbConnectStr = util.conf().get('pgConn3')


def handle_exit(signum):
    sys.exit(0)


def freopen(f, mode, stream):
    oldf = open(f, mode)
    oldfd = oldf.fileno()
    newfd = stream.fileno()
    os.close(newfd)
    os.dup2(oldfd, newfd)


def wrapper():
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        zk = KazooClient(hosts=zkHost)
        zk.start()
        propTranq = LockingQueue(zk, util.conf().get('proposeTran'))
        # get the config param for load, if current load > param, will wait
        cur.execute("""select val from con0 where param = 'load'""")
        load = cur.fetchone()[0]
        conn.commit()
        load = float(load)
        print("load param = {0}".format(load))
        while True:
            entryload = os.getloadavg()[0]
            if entryload >= load:
                time.sleep(3)
                print('{0} load = {1}'.format(datetime.now(), entryload))
                continue
            rawC = propTranq.get()
            ints = datetime.now()
            inload = os.getloadavg()[0]

            alias = rawC.decode().split('&&')[0]
            rawCode = rawC.decode().split('&&')[1]
            lastsig = rawC.decode().split('&&')[2]
            entryId = rawC.decode().split('&&')[3]
            globalId = rawC.decode().split('&&')[4]

            pro3 = Popen(['/usr/bin/python3', '/{0}/{1}/payer{2}.py'.format(util.conf().get('playerepo3'), util.path(alias), alias), rawCode, lastsig, globalId], stdin=None, stdout=None)
            pro3.wait()

            cur.execute("""update propose_transfer set progress = 0 , setup = now() where id = %s
            """, [entryId])
            conn.commit()

            propTranq.consume()

            outts = datetime.now()
            outload = os.getloadavg()[0]
            nodename = os.uname().nodename
            cur.execute("""
            insert into runstat0(executable,ints,inload,outts,outload,nodename) values (%s, %s, %s, %s, %s, %s)
            """, [executable, ints, inload, outts, outload, nodename])
            conn.commit()

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
    freopen('/tmp/processTransferWrapper2out', 'a', sys.stdout)
    freopen('/tmp/processTransferWrapper2err', 'a', sys.stderr)
    wrapper()
