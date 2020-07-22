#!/usr/bin/env python3
import os
import time
import sys
import signal
import hashlib
import configparser
import binascii
import logging

from datetime import datetime
from subprocess import Popen, PIPE
from cassandra.cluster import Cluster
from kazoo.client import KazooClient
from kafka import KafkaProducer, KafkaConsumer


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

    def path(self, txt):
        m = hashlib.sha256()
        m.update(txt.encode('utf-8'))
        dig = m.hexdigest()
        return '{0}'.format(dig[0])

class AliasHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = super().setup()
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
            logging.info('executionId = {0}'.format(executionId))
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
        cluster, session, kafkaHost, zk = super().setup()
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
        cluster, session, kafkaHost, zk = super().setup()
        kafka = KafkaConsumer('issue3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        executionCounter = zk.Counter("/executions", default=0x7000)
        for m in kafka:
            logging.debug(m)
            proposal = str(m.value, 'utf-8')
            while self.checkLoad():
                logging.info('it is too hot, sleep 2 seconds')
                time.sleep(2)
            executionCounter += 1
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'issue', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, proposal])

            self.processProposal(proposal)
    def processProposal(self, proposal):
        cluster, session, kafkaHost, zk = super().setup()
        (pq, prop) = proposal.split('@@')
        pq = pq.strip()
        prop = prop.strip()
        stmt = 'select checksumpq, checksumd from runtime where id = 0 limit 1'
        (checksumpq, checksumd) = session.execute(stmt).one()
        logging.debug('checksumpq = {0}, checksumd = {1}'.format(checksumpq, checksumd))
        pro1 = Popen(['./step1', checksumpq, checksumd, prop[-16:]], stdin=None, stdout=PIPE)
        checksum0 = pro1.communicate()[0].decode().strip()
        checksum0 = checksum0.rstrip('0')
        logging.debug('checksum0 = {0}'.format(checksum0))
        row = session.execute('select symbol from issuer0 where pq = %s limit 1', [pq]).one()
        symbol = row.symbol
        logging.debug('symbol = {0}, pq = {1}'.format(symbol, pq))
        #step1path = getpath(symbol)
        row = session.execute('select step1repo from runtime where id = 0 limit 1').one()
        step1path = row.step1repo
        if not step1path:
            logging.error('step1path can not be None')
            return
        step1path = '{0}/{1}'.format(step1path, super().path(symbol))
        logging.debug('step1path = {0}'.format(step1path))
        pro3 = Popen(['{0}/step1{1}'.format(step1path, symbol), prop, checksum0], stdin=None, stdout=PIPE)
        verdict = pro3.communicate()[0].decode().strip()
        verdict = verdict.rstrip('0')
        logging.debug('verdict = {0}'.format(verdict))
        pro2 = Popen(['./step2', pq, verdict], stdin=None, stdout=PIPE)
        note = pro2.communicate()[0].decode().strip()
        note = note.rstrip('0')
        print("verdict={0} note={1}".format(verdict, note))
        if not note.startswith('5e5e'):
            print('invalid msg:{0}'.format(note))
            return
        else:
            rawtext = str(binascii.a2b_hex(bytes(note, 'utf-8')), 'utf-8')
        (left, right) = rawtext.split('->')
        target = right[:-2]
        (symbol, noteId, quantity) = left.split('||')
        symbol = symbol[2:]
        res = session.execute('select note_id from ownership0 where note_id = %s limit 1', [noteId]).one()
        if res:
            logging.error("the note {0} is already in place".format(noteId))
            return
        else:
            self.save2ownershipcatalog(pq.strip(), verdict.strip(), prop.strip(), rawtext.strip(), symbol.strip(), noteId.strip(), quantity.strip(), target.strip())
        cluster.shutdown()
        
    def save2ownershipcatalog(self, pq, verdict, proposal, rawtext, symbol, noteId, quantity, target):
        cluster, session, kafkaHost, zk = super().setup()
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
        #save 2
        session.execute("""
        insert into ownership0(id, clique, symbol, note_id, quantity, owner, updated, hash_code)
        values(%s, '3', %s, %s, %s, %s, toTimestamp(now()), %s)
        """, [int(ownershipId), symbol.strip(), noteId.strip(), int(quantity.strip()), target.strip(), hashcode.strip()])

        session.execute("""
        insert into note_catalog0(id, clique, pq, verdict, proposal, note, recipient, hook, stmt, setup, hash_code)
        values(%s, '3', %s, %s, %s, %s, %s, '', %s, toTimestamp(now()), %s)
        """,[int(rowId), pq.strip(), verdict.strip(), proposal.strip(),
             "{0}||{1}||{2}".format(symbol.strip(), noteId.strip(), quantity.strip()),
             target.strip(), rawtext.strip(), hashcode.strip()])
        cluster.shutdown()

class TransferHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = super().setup()
        kafka = KafkaConsumer('transfer3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        executionCounter = zk.Counter("/executions", default=0x7000)
        for m in kafka:
            while self.checkLoad():
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)
            proposal = str(m.value, 'utf-8')
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) values(%s, 'transfer', toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, proposal])

            pro1 = Popen(['/usr/bin/python3', './processproptran.py', proposal], stdin=None, stdout=None)
            pro1.wait()

class IssueProposalHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost, zk = super().setup()
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
        cluster, session, kafkaHost, zk = super().setup()
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
    #logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
#@    signal.signal(signal.SIGINT, handle_exit)
#@    signal.signal(signal.SIGTERM, handle_exit)
#@    pid = os.fork()
#@    if pid > 0:
#@        time.sleep(3)
#@        sys.exit(0)
#@    os.setsid()
#@    sys.stdin.close()
#@    freopen('/tmp/testout', 'a', sys.stdout)
#@    freopen('/tmp/testerr', 'a', sys.stderr)
#    alias = AliasHandler()
#    alias.process()
    a = IssueHandler()
    a.process()
