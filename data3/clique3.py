#!/usr/bin/env python3
import os
import time
import sys
import signal
import hashlib
import configparser
import binascii
import logging
import random
import socket
import base64
import subprocess

from multiprocessing import Process
from subprocess import Popen, PIPE
from cassandra.cluster import Cluster
from kazoo.client import KazooClient
from kafka import KafkaProducer, KafkaConsumer
from cryptography.fernet import Fernet


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

    def queueName(self):
        pass

    def process(self):
        cluster, session, kafkaHost, zk = self.setup()
        queueName = self.queueName()
        logging.info('queue Name: {0}'.format(queueName))
        kafka = KafkaConsumer(queueName,
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        executionCounter = zk.Counter("/executions", default=0x7000)
        for m in kafka:
            while self.checkLoad():
                logging.info('it is too hot, sleep 2 seconds')
                time.sleep(2)
            proposal = str(m.value, 'utf-8')
            executionCounter += 1
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload)
            values(%s, %s, toTimestamp(now()), %s)
            """
            session.execute(stmt, [executionId, queueName, proposal])
            self.processProposal(proposal)

    def postTxn(self, txn):
        cluster, session, kafkaHost, zk = self.setup()
        res = session.execute('select peer, pq, d from clique3.channel where port =12821 limit 1').one()
        if res:
            [peer, pq, d] = res
            key = Fernet.generate_key()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer, 12821))
            cipher_str = str(binascii.b2a_hex(base64.urlsafe_b64decode(key)), 'utf-8')
            args = './crypt', pq, d, cipher_str
            with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
                cipher = p.stdout.read()
                if cipher:
                    cipher = str(cipher, 'utf-8').strip()
                    cipher = '^^^>>CIPHER<<{0}$$$'.format(cipher)
                    size = len(cipher)
                    sock.send(bytes('{:08}'.format(size), 'utf-8'))
                    sock.send(bytes(cipher, 'utf-8'))
                    f = Fernet(key)
                    token = f.encrypt(bytes(txn, 'utf-8'))
                    sock.send(bytes('{:08}'.format(len(token)), 'utf-8'))
                    sock.send(token)
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()

    def processProposal(self, proposal):
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
    def queueName(self):
        return 'alias3'

    def processProposal(self, proposal):
        (alias, globalId) = proposal.split('||')
        cluster, session, kafkaHost, zk = super().setup()
        baseDir = '/home/u/senate/'
        pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl', baseDir, '2048'], stdin=None, stdout=None, cwd='.')
        pro0.wait()
        pro1 = Popen(['/usr/bin/perl', 'makepayer.pl', alias, globalId], stdin=None, stdout=None, cwd='.')
        pro1.wait()
        # put a symbol message to kafka
        sha256 = hashlib.sha256()
        while True:
            sha256.update('{0}'.format(globalId).encode('utf-8'))
            sha256.update('{0}'.format(alias).encode('utf-8'))
            hashCode = sha256.hexdigest()
            symbol = hashCode[:5]
            symbol = symbol.upper()
            res = session.execute('select symbol from issuer0 where symbol = %s', [symbol]).one()
            if res:
                continue
            res = session.execute('select word from reserved0 where word = %s', [symbol]).one()
            if res:
                continue
            # end the loop
            break
        kafkaproducer = KafkaProducer(bootstrap_servers=kafkaHost.split(','))
        kafkaproducer.send('symbol3', key=bytes('{0}||{1}'.format(globalId, symbol), 'utf-8'),
                           value=bytes('{0}||{1}'.format(globalId, symbol), 'utf-8'))
        kafkaproducer.flush()
        cluster.shutdown()
        time.sleep(2)


class SymbolHandler(HandleBase):
    def queueName(self):
        return 'symbol3'

    def processProposal(self, proposal):
        (globalId, symbol) = proposal.split('||')
        cluster, session, kafkaHost, zk = super().setup()
        res = session.execute('select alias from player0  where global_id=%s', [globalId]).one()
        if not res:
            logging.error('alias can not be None')
            return
        [alias] = res
        baseDir = '/home/u/senate/'
        pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl', baseDir, '2048'], stdin=None, stdout=None, cwd='.')
        pro0.wait()
        pro1 = Popen(['/usr/bin/perl', 'makeissuer.pl', alias, symbol, globalId], stdin=None, stdout=None, cwd='.')
        pro1.wait()
        time.sleep(2)


class IssueHandler(HandleBase):
    def queueName(self):
        return 'issue3'

    def processProposal(self, proposal):
        cluster, session, kafkaHost, zk = super().setup()
        (pq, prop) = proposal.split('@@')
        pq = pq.strip()
        prop = prop.strip()
        stmt = 'select checksumpq, checksumd from runtime where id = 0 limit 1'
        (checksumpq, checksumd) = session.execute(stmt).one()
        pro1 = Popen(['./step1', checksumpq, checksumd, prop[-16:]], stdin=None, stdout=PIPE)
        checksum0 = pro1.communicate()[0].decode().strip()
        checksum0 = checksum0.rstrip('0')
        # logging.info('checksum0 = {0}'.format(checksum0))
        [symbol] = session.execute('select symbol from issuer0 where pq = %s limit 1', [pq]).one()
        # logging.info('symbol = {0}, pq = {1}'.format(symbol, pq))
        [step1path] = session.execute('select step1repo from runtime where id = 0 limit 1').one()
        if not step1path:
            logging.error('step1path can not be None')
            return
        step1path = '{0}/{1}'.format(step1path, super().path(symbol))
        # logging.info('step1path = {0}'.format(step1path))
        pro3 = Popen(['{0}/step1{1}'.format(step1path, symbol), prop, checksum0], stdin=None, stdout=PIPE)
        verdict = pro3.communicate()[0].decode().strip()
        verdict = verdict.rstrip('0')
        # logging.info('verdict = {0}'.format(verdict))
        pro2 = Popen(['./step2', pq, verdict], stdin=None, stdout=PIPE)
        note = pro2.communicate()[0].decode().strip()
        note = note.rstrip('0')
        if not note.startswith('5e5e'):
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
            self.save2ownershipcatalog(pq.strip(), verdict.strip(), prop.strip(), rawtext.strip(),
                                       symbol.strip(), noteId.strip(), quantity.strip(), target.strip())
            txnTxt = '{0}||{1}||{2}||{3}'.format(pq, prop, verdict, '30001')
            # logging.info(txnTxt)
            super().postTxn(txnTxt)
        cluster.shutdown()

    def save2ownershipcatalog(self, pq, verdict, proposal, rawtext, symbol, noteId, quantity, target):
        cluster, session, kafkaHost, zk = super().setup()
        zkc = zk.Counter("/ownershipId3", default=0x700)
        zkc += 1
        ownershipId = zkc.value
        zkc = zk.Counter("/noteId3", default=0x700)
        zkc += 1
        rowId = zkc.value
        zk.stop()
        zk.close()
        sha256 = hashlib.sha256()
        sha256.update("{0}{1}".format(noteId.strip(), target.strip()).encode('utf-8'))
        hashcode = sha256.hexdigest()
        # save into 2 tables ownership0& note_catalog0
        session.execute("""
        insert into ownership0(seq, clique, symbol, note_id, quantity, owner, updated, hash_code)
        values(%s, '3', %s, %s, %s, %s, toTimestamp(now()), %s)
        """, [int(ownershipId), symbol.strip(), noteId.strip(),
              int(quantity.strip()), target.strip(), hashcode.strip()])

        session.execute("""
        insert into note_catalog0(id, clique, pq, verdict, proposal, note, recipient, hook, stmt, setup, hash_code)
        values(%s, '3', %s, %s, %s, %s, %s, '', %s, toTimestamp(now()), %s)
        """, [int(rowId), pq.strip(), verdict.strip(), proposal.strip(), "{0}||{1}||{2}".format(symbol.strip(), noteId.strip(), quantity.strip()), target.strip(), rawtext.strip(), hashcode.strip()])
        cluster.shutdown()


class TransferHandler(HandleBase):
    def queueName(self):
        return 'transfer3'

    def processProposal(self, proposal):
        cluster, session, kafkaHost, zk = super().setup()
        (pq, prop) = proposal.split('@@')
        pq = pq.strip()
        prop = prop.strip()
        stmt = 'select checksumpq, checksumd from runtime where id = 0 limit 1'
        (checksumpq, checksumd) = session.execute(stmt).one()
        pro1 = Popen(['./step1', checksumpq, checksumd, proposal[-16:]],
                     stdin=None, stdout=PIPE)
        checksum0 = pro1.communicate()[0].decode().strip()
        checksum0 = checksum0.rstrip('0')
        [alias] = session.execute("""
        select alias from player0 where pq = %s
        """, [pq]).one()
        alias = alias.strip()
        if not alias:
            logging.error('alias can not be None')
            return
        [step1path] = session.execute("""
        select step1repo from runtime where id = 0 limit 1
        """).one()
        if not step1path:
            logging.error('step1path can not be None')
            return
        step1path = '{0}/{1}'.format(step1path, super().path(alias))
        pro1 = Popen(['{0}/step1{1}'.format(step1path, alias), prop, checksum0],
                     stdin=None, stdout=PIPE)
        verdict = pro1.communicate()[0].decode().strip()
        verdict = verdict.rstrip('0')

        pro2 = Popen(['./step2', pq, verdict], stdin=None, stdout=PIPE)
        note = pro2.communicate()[0].decode().strip()
        note = note.strip()
        note = note.rstrip('0')
        if not note.startswith('5e5e'):
            logging.error('invalid msg: {0}'.format(note))
            return
        rawtext = str(binascii.a2b_hex(bytes(note, 'utf-8')), 'utf-8')
        # logging.info('rawtext = {0}'.format(rawtext))
        (left, right) = rawtext.split('->')
        (target, lastsig, lastblock) = right.split('@@')
        # lastsig = lastsig[:-2]
        (symbol, noteId, quantity) = left.split('||')
        symbol = symbol.split('::')[1]
        logging.info('pq = {0}, symbol= {1}, noteId= {2}, quantity= {3}, lastsig ={4}'.
                     format(pq, symbol, noteId, quantity, lastsig))
        if self.verify(pq, symbol, noteId, quantity, lastsig):
            self.save2ownershipcatalog(pq, verdict, prop, rawtext, symbol, noteId, quantity, target, lastsig)
            txnTxt = '{0}||{1}||{2}||{3}'.format(pq, prop, verdict, '30001')
            super().postTxn(txnTxt)
        cluster.shutdown()

    def verify(self, pq, symbol, noteId, quantity, lastsig):
        cluster, session, kafkaHost, zk = super().setup()
        [owner0] = session.execute("""
        select owner from ownership0 where note_id = %s
        """, [noteId]).one()
        [owner1] = session.execute("""
        select alias from player0 where pq = %s
        """, [pq]).one()
        [verdict] = session.execute("""
        select verdict from note_catalog0 where note = %s
        """, ['{0}||{1}||{2}'.format(symbol, noteId, quantity)]).one()
        cluster.shutdown()
        return owner0 == owner1 and verdict[-16:] == lastsig

    def save2ownershipcatalog(self, pq, verdict, proposal, rawtext, symbol, noteId, quantity, target, lastsig):
        cluster, session, kafkaHost, zk = super().setup()
        zkc = zk.Counter("/noteId3", default=0x7000)
        zkc += 1
        rowId = zkc.value
        session.execute("""
        update ownership0 set owner= %s , updated = toTimestamp(now()) where note_id = %s
        """, [target, noteId])
        sha256 = hashlib.sha256()
        sha256.update("{0}{1}".format(noteId.strip(), target.strip()).encode('utf-8'))
        hashcode = sha256.hexdigest()
        session.execute("""insert into note_catalog0(id, clique, pq, verdict, proposal, note, recipient, hook, stmt, setup, hash_code)
        values(%s, '3', %s, %s, %s, %s, %s, %s,%s, toTimestamp(now()), %s)
        """, [int(rowId), pq, verdict, proposal, "{0}||{1}||{2}".format(symbol.strip(), noteId.strip(), quantity), target, lastsig, rawtext, hashcode])
        cluster.shutdown()


class IssueProposalHandler(HandleBase):
    def queueName(self):
        return 'issue0'

    def processProposal(self, payload):
        cluster, session, kafkaHost, zk = super().setup()
        (symbol, quantity, globalId) = payload.split('||')
        sha256 = hashlib.sha256()
        while True:
            sha256.update("{0}".format(symbol).encode('utf-8'))
            sha256.update("{0}".format(random.random()).encode('utf-8'))
            sha256.update("{0}".format(quantity).encode('utf-8'))
            digest = sha256.hexdigest()
            length = len(digest)
            noteId = digest[length-8:]
            res = session.execute("""
            select * from ownership0 where note_id = %s
            """, [noteId])
            if not res:
                break
        stmt = """
        select playerrepo from runtime where id=0
        """
        [folder] = session.execute(stmt).one()
        text = "||{0}||{1}->".format(noteId, quantity)
        pro3 = Popen(['/usr/bin/python3', '/{0}/{1}/issuer{2}.py'.format(folder, super().path(symbol), symbol), text, globalId], stdin=None, stdout=None)
        pro3.wait()
        cluster.shutdown()


class TransferProposalHandler(HandleBase):
    def queueName(self):
        return 'transfer0'

    def processProposal(self, payload):
        cluster, session, kafkaHost, zk = super().setup()
        stmt = """
        select playerrepo from runtime where id=0
        """
        [folder] = session.execute(stmt).one()
        (alias, rawCode, lastTxn, lastBlock, globalId) = payload.split('&&')
        # logging.info([alias, rawCode, lastTxn, lastBlock, globalId])
        pro3 = Popen(['/usr/bin/python3', '/{0}/{1}/payer{2}.py'.format(folder, super().path(alias), alias), rawCode, lastTxn, globalId, lastBlock],
                     stdin=None, stdout=None)
        pro3.wait()
        cluster.shutdown()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    pid = os.fork()
    if pid > 0:
        time.sleep(3)
        sys.exit(0)
    os.setsid()
    sys.stdin.close()
    freopen('/tmp/testout', 'a', sys.stdout)
    freopen('/tmp/testerr', 'a', sys.stderr)

    logging.basicConfig(filename='clique3.log', level=logging.INFO)
    issuePropsalHandler = IssueProposalHandler()
    issue0 = Process(target=issuePropsalHandler.process)
    issue0.start()

    issuehandler = IssueHandler()
    issue3 = Process(target=issuehandler.process)
    issue3.start()

    transferProposalHandler = TransferProposalHandler()
    transfer0 = Process(target=transferProposalHandler.process)
    transfer0.start()

    transferHandler = TransferHandler()
    transfer3 = Process(target=transferHandler.process)
    transfer3.start()

    aliasHandler = AliasHandler()
    alias3 = Process(target=aliasHandler.process)
    alias3.start()

    symbolHandler = SymbolHandler()
    symbol3 = Process(target=symbolHandler.process)
    symbol3.start()
    # from sys import argv
    # instance = argv[1]
    # if instance == 'issue0':
    #     logging.basicConfig(filename='issue0.log', level=logging.INFO)
    #     var = IssueProposalHandler()
    # if instance == 'issue3':
    #     logging.basicConfig(filename='issue3.log', level=logging.INFO)
    #     var = IssueHandler()
    # if instance == 'transfer0':
    #     logging.basicConfig(filename='transfer0.log', level=logging.INFO)
    #     var = TransferProposalHandler()
    # if instance == 'transfer3':
    #     logging.basicConfig(filename='transfer3.log', level=logging.INFO)
    #     var = TransferHandler()
    # if instance == 'symbol3':
    #     logging.basicConfig(filename='symbol3.log', level=logging.INFO)
    #     var = SymbolHandler()
    # if instance == 'alias3':
    #     logging.basicConfig(filename='alias3.log', level=logging.INFO)
    #     var = AliasHandler()
    # var.process()
