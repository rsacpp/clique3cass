#!/usr/bin/env python3

import os
import time
import sys
import signal
import hashlib
import configparser

from datetime import datetime
from cassandra.cluster import Cluster
from kazoo.client import KazooClient
from kafka import KafkaProducer,KafkaConsumer

def handle_exit(signum):
    sys.exit(0)

def freopen(f, mode, stream):
    oldf = open(f, mode)
    oldfd = oldf.fileno()
    newfd = stream.fileno()
    os.close(newfd)
    os.dup2(oldfd, newfd)

class HandleBase:
    def setup(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        cassHost = config['clique3cass']['cassandraHost']
        cassKeyspace = config['clique3cass']['cassandraKeyspace']
        kafkaHost = config['clique3cass']['kafkaHost']
        zkHost = config['clique3cass']['zkHost']
        cluster = Cluster(cassHost.split(','))
        session = cluster.connect(cassKeyspace)
        zk = KazooClient(hosts=zkHost)
        zk.start()
        return cluster, session, kafkaHost, zk

    def process(self):
        pass

    def checkLoad(self):
        (load1, load5, load15) = os.getloadavg()
        return load1 > 0.8

class AliasHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = setup()
        kafka = KafkaConsumer('alias3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))

        executionCounter = zk.Counter("/executions", default=0x7000)

        for m in kafka:
            while self.checkLoad():
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)

            payload = str(m.value, 'utf-8')
            #save it to cass
            alias, globalId = payload.split('||')
            executionCounter += 1
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'alias', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, payload])

            with lock0:
                # the operation
                pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl', baseDir, '2048'], stdin=None, stdout=None, cwd='/var/tmp')
                pro0.wait()
                pro1 = Popen(['/usr/bin/perl', 'makepayer.pl', alias, globalId], stdin=None, stdout=None, cwd='/var/tmp')
                pro1.wait()
                #put a symbol message to kafka
                sha256 = hashlib.sha256()
                while True:
                    sha256.update('{0}'.format(globalId).encode('utf-8'))
                    sha256.update('{0}'.format(alias).encode('utf-8'))
                    hashCode = sha256.hexdigest()
                    symbol = hashCode[:5]
                    symbol = symbol.upper()
                    res = session.execute("""
                    select symbol from symbol_redo0 where symbol = %s
                    """, [symbol])
                    if res:
                        continue
                    res = session.execute("""
                    select symbol from issuer0 where symbol = %s
                    """, [symbol])
                    if res:
                        continue
                    res = session.execute("""
                    select word from reserved0 where word = %s
                    """, [symbol])
                    if res:
                        continue
                    break
                kafkaproducer = KafkaProducer(bootstrap_servers=kafkaHost.split(','))
                kafkaproducer.send('symbol3', key=bytes('{0}||{1}'.format(globalId, symbol), 'utf-8'), value=bytes('{0}||{1}'.format(globalId, symbol), 'utf-8'))
                kafkaproducer.flush()

class SymbolHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = setup()
        kafka = KafkaConsumer('symbol3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        for m in kafka:
            while self.checkLoad():
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)

            payload = str(m.value, 'utf-8')
            (globalId, symbol) = payload.split('||')
            executionCounter = zk.Counter("/executions", default=0x7000)
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'symbol', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, payload])

            pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl', baseDir, '2048'], stdin=None, stdout=None, cwd=workshopInstance)
            pro0.wait()
            pro1 = Popen(['/usr/bin/perl', 'makeissuer.pl', alias, symbol, globalId], stdin=None, stdout=None, cwd=workshopInstance)
            pro1.wait()

class IssueHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = setup()
        kafka = KafkaConsumer('issue3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        for m in kafka:
            while self.checkLoad():
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)
            executionCounter = zk.Counter("/executions", default=0x7000)
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'issue', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, payload])
            proposal = str(m.value, 'utf-8')
            pro1 = Popen(['/usr/bin/python3', 'processpropiss.py', proposal], stdin=None, stdout=None)
            pro1.wait()

class TransferHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = setup()
        kafka = KafkaConsumer('transfer3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        for m in kafka:
            while self.checkLoad():
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)
            proposal = str(m.value, 'utf-8')
            executionCounter = zk.Counter("/executions", default=0x7000)
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'transfer', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, proposal])

            pro1 = Popen(['/usr/bin/python3', './processproptran.py', proposal], stdin=None, stdout=None)
            pro1.wait()

class IssueProposalHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = setup()
        kafka = KafkaConsumer('issue0',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        for m in kafka:
            while self.checkLoad():
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)
            payload = str(m.value, 'utf-8')
            executionCounter = zk.Counter("/executions", default=0x7000)
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'issue0', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, payload])
            (symbol, quantity, globalId) = payload.split('||')
            # first get the id of the note, take a random number
            sha256 = hashlib.sha256()
            sha256.update("{0}".format(symbol).encode('utf-8'))
            sha256.update("{0}".format(random.random()).encode('utf-8'))
            sha256.update("{0}".format(quantity).encode('utf-8'))
            digest = sha256.hexdigest()
            length = len(digest)
            noteId = digest[length-8:]
            while True:
                res = session.execute('select * from ownership0 where note_id = %s', [noteId])
                if res:
                    sha256.update("{0}".format(random.random()).encode('utf-8'))
                    digest = sha256.hexdigest()
                    length = len(digest)
                    noteId = digest[length-8:]
                else:
                    break
            text = "||{0}||{1}->".format(noteId, quantity)

            pro3 = Popen(['/usr/bin/python3', '/{0}/{1}/issuer{2}.py'.format(util.conf().get('playerepo3'), util.path(symbol), symbol), text, globalId], stdin=None, stdout=None)
            pro3.wait()

class TransferProposalHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = setup()
        kafka = KafkaConsumer('transfer0',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        for m in kafka:
            while self.checkLoad():
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)
            payload = str(m.value, 'utf-8')
            executionCounter = zk.Counter("/executions", default=0x7000)
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'issue0', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, payload])
            (alias, raw_code, last_txn, last_block, global_id) = payload.split('&&')
            pro3 = Popen(['/usr/bin/python3', '/{0}/{1}/payer{2}.py'.format(util.conf().get('playerepo3'), util.path(alias), alias), rawCode, lastsig, globalId], stdin=None, stdout=None)
            pro3.wait()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    pid = os.fork()
    if pid > 0:
        time.sleep(3)
        sys.exit(0)
    os.setsid()
    sys.stdin.close()
    freopen('/tmp/aliasredo3out', 'a', sys.stdout)
    freopen('/tmp/aliasredo3err', 'a', sys.stderr)
    alias = AliasHandler()
    alias.process()

        
