#!/usr/bin/python3
#
# symbolredo3.py for Clique3
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
from kazoo.client import KazooClient
from kazoo.recipe.queue import LockingQueue
from datetime import datetime
from subprocess import Popen
sys.path.append('/the/path/of/util.py')
import util
executable = 'symbolredo3'


dbConnectStr = util.conf().get('pgConn3')
zkHost = util.conf().get('zkCluster3')
baseDir = util.conf().get('baseDir3')
workshopInstance = util.conf().get('workshop3')


def handle_exit(signum):
    sys.exit(0)


def freopen(f, mode, stream):
    oldf = open(f, mode)
    oldfd = oldf.fileno()
    newfd = stream.fileno()
    os.close(newfd)
    os.dup2(oldfd, newfd)


def processSymbol():
    try:
        conn = psycopg2.connect(dbConnectStr)
        cur = conn.cursor()
        zk = KazooClient(hosts=zkHost)
        zk.start()
        symbolq = LockingQueue(zk, util.conf().get('symbol3'))
        while True:
            rawCode = symbolq.get()
            ints = datetime.now()
            inload = os.getloadavg()[0]

            symbol = rawCode.decode().split('||')[0]
            globalId = rawCode.decode().split('||')[1]
            symbolq.consume()

            alias = ''
            while not alias:
                print("loop for the alias of {0}".format(globalId))
                cur.execute("""
                select alias from player0 where "globalId" = %s and clique = '3'
                """, [globalId])
                res = cur.fetchone()
                conn.commit()
                if res:
                    alias = res[0]

            print("process symbol:{0} alias:{1} globalId:{2}".format(symbol, alias, globalId))
            lock0 = zk.Lock(symbol, 'data3')
            with lock0:
                # the operation
                pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl', baseDir, '2048'], stdin=None, stdout=None, cwd=workshopInstance)
                pro0.wait()
                pro1 = Popen(['/usr/bin/perl', 'makeissuer.pl', alias, symbol, globalId], stdin=None, stdout=None, cwd=workshopInstance)
                pro1.wait()

                cur.execute("""
                update symbol_redo0 set progress= 0, setup=now() where symbol=%s and clique = '3'
                """, [symbol])
                conn.commit()
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
    freopen('/tmp/symbolredo3out', 'a', sys.stdout)
    freopen('/tmp/symbolredo3err', 'a', sys.stderr)
    processSymbol()
