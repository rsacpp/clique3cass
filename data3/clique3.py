#!/usr/bin/env python3
import os
import re
import time
import sys
import hashlib
import configparser
import binascii
import logging
import socket
import base64
import subprocess

from datetime import datetime
from multiprocessing import Process
from subprocess import Popen, PIPE
from cassandra.cluster import Cluster
from kazoo.client import KazooClient
from kafka import KafkaProducer, KafkaConsumer
from cryptography.fernet import Fernet

config = configparser.ConfigParser()
config.read('config.ini')
baseDir = config['clique3cass']['senate']


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
            logging.info(m)
            while self.checkLoad():
                logging.info('it is too hot, sleep 2 seconds')
                time.sleep(2)
            proposal = str(m.value, 'utf-8')
            executionCounter += 1
            executionId = executionCounter.value
            stmt = """
            insert into executions(id, code, ts, payload) \
            values(%s, %s, toTimestamp(now()), %s) \
            """
            session.execute(stmt, [executionId, queueName, proposal])
            self.processProposal(proposal)

    def postTxn(self, txn):
        cluster, session, kafkaHost, zk = self.setup()
        res = session.execute('select peer, pq, d from clique3.channel \
        where port =12821 limit 1').one()
        if res:
            [peer, pq, d] = res
            key = Fernet.generate_key()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer, 12821))
            cipher_str = str(binascii.b2a_hex(
                base64.urlsafe_b64decode(key)), 'utf-8')
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
        zk.stop()
        zk.close()
        cluster.shutdown()

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
        pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl', baseDir, '2048'],
                     stdin=None, stdout=None, cwd='.')
        pro0.wait()
        pro1 = Popen(['/usr/bin/perl', 'makepayer.pl', alias, globalId],
                     stdin=None, stdout=None, cwd='.')
        pro1.wait()
        # put a symbol message to kafka
        sha256 = hashlib.sha256()
        while True:
            sha256.update('{0}'.format(globalId).encode('utf-8'))
            sha256.update('{0}'.format(alias).encode('utf-8'))
            hashCode = sha256.hexdigest()
            symbol = hashCode[:5]
            symbol = symbol.upper()
            res = session.execute('select symbol from clique3.issuer0 \
            where symbol = %s', [symbol]).one()
            if res:
                continue
            res = session.execute('select word from clique3.reserved0 \
            where word = %s', [symbol]).one()
            if res:
                continue
            # end the loop
            break
        kafkaproducer = KafkaProducer(bootstrap_servers=kafkaHost.split(','))
        kafkamsg = bytes('{0}||{1}'.format(globalId, symbol), 'utf-8')
        kafkaproducer.send('symbol3', key=kafkamsg, value=kafkamsg)
        kafkaproducer.flush()
        kafkaproducer.close()
        cluster.shutdown()
        zk.stop()
        zk.close()
        time.sleep(2)


class SymbolHandler(HandleBase):
    def queueName(self):
        return 'symbol3'

    def processProposal(self, proposal):
        (globalId, symbol) = proposal.split('||')
        cluster, session, kafkaHost, zk = super().setup()
        res = session.execute('select alias from player0 \
        where global_id=%s', [globalId]).one()
        if not res:
            logging.error('alias can not be None')
            return
        [alias] = res

        pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl',
                      baseDir, '2048'], stdin=None, stdout=None, cwd='.')
        pro0.wait()
        pro1 = Popen(['/usr/bin/perl', 'makeissuer.pl', alias,
                      symbol, globalId], stdin=None, stdout=None, cwd='.')
        pro1.wait()
        zk.stop()
        zk.close()
        cluster.shutdown()
        time.sleep(2)


class IssueHandler(HandleBase):
    def queueName(self):
        return 'issue3'

    def processProposal(self, proposal):
        cluster, session, kafkaHost, zk = super().setup()
        try:
            (pq, prop) = proposal.split('@@')
            if not pq or not prop:
                logging.error('pq or prop can not be None')
                return
            pq = pq.strip()
            prop = prop.strip()
            stmt = """select checksumpq, checksumd from runtime
            where id = 0 limit 1"""
            (checksumpq, checksumd) = session.execute(stmt).one()
            pro1 = Popen(['./step1', checksumpq, checksumd, prop[-16:]],
                         stdin=None, stdout=PIPE)
            checksum0 = pro1.communicate()[0].decode().strip()
            checksum0 = checksum0.rstrip('0')
            logging.debug('checksum0 = {0}'.format(checksum0))
            [symbol, step1repo] = session.execute("""
            select symbol, step1repo from clique3.issuer0
            where pq = %s limit 1""", [pq]).one()
            logging.debug('symbol = {0}, step1repo = {2}, \
pq = {1}'.format(symbol, pq, step1repo))
            if not symbol:
                logging.error('no symbol for pq:{0}'.format(pq))
                return
            if not step1repo:
                logging.error('step1repo can not be None')
                return
            pro3 = Popen([step1repo, prop, checksum0],
                         stdin=None, stdout=PIPE)
            verdict = pro3.communicate()[0].decode().strip()
            verdict = verdict.rstrip('0')
            logging.debug('verdict = {0}'.format(verdict))
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
            res = session.execute("""select note_id from ownership0
            where note_id = %s limit 1""", [noteId]).one()
            if res:
                logging.error("the note {0} is already there".format(noteId))
                return
            else:
                self.save2ownershipcatalog(pq.strip(),
                                           verdict.strip(),
                                           prop.strip(),
                                           rawtext.strip(),
                                           symbol.strip(),
                                           noteId.strip(),
                                           quantity.strip(),
                                           target.strip())
                txnTxt = '{0}||{1}||{2}||{3}'.format(pq,
                                                     prop,
                                                     verdict,
                                                     '30001')
                logging.debug(txnTxt)
                super().postTxn(txnTxt)
        except Exception as err:
            logging.error(err)
        finally:
            cluster.shutdown()
            zk.stop()
            zk.close()

    def save2ownershipcatalog(self, pq, verdict, proposal, rawtext,
                              symbol, noteId, quantity, target):
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
        sha256.update("{0}{1}".format(noteId.strip(),
                                      target.strip()).encode('utf-8'))
        hashcode = sha256.hexdigest()
        # save into 2 tables ownership0& note_catalog0
        session.execute("""
        insert into ownership0(seq, clique, symbol, note_id, quantity, owner, \
        updated, hash_code, verdict0)values(%s, '3', %s, %s, %s, %s, \
        toTimestamp(now()), %s, %s)
        """, [int(ownershipId), symbol.strip(), noteId.strip(),
              int(quantity.strip()), target.strip(),
              hashcode.strip(), verdict[-16:]])

        session.execute("""
        insert into note_catalog0(id, clique, pq, verdict, proposal, note, \
        recipient, hook, stmt, setup, hash_code)
        values(%s, '3', %s, %s, %s, %s, %s, '', %s, toTimestamp(now()), %s)
        """, [int(rowId), pq.strip(), verdict.strip(), proposal.strip(),
              "{0}||{1}||{2}".format(symbol.strip(),
                                     noteId.strip(), quantity.strip()),
              target.strip(), rawtext.strip(), hashcode.strip()])
        cluster.shutdown()


class TransferHandler(HandleBase):
    def queueName(self):
        return 'transfer3'

    def processProposal(self, proposal):
        logging.info(proposal)
        cluster, session, kafkaHost, zk = super().setup()
        try:
            (pq, prop) = proposal.split('@@')
            pq = pq.strip()
            prop = prop.strip()
            stmt = """select checksumpq, checksumd from runtime
            where id = 0 limit 1"""
            (checksumpq, checksumd) = session.execute(stmt).one()
            pro1 = Popen(['./step1', checksumpq, checksumd, proposal[-16:]],
                         stdin=None, stdout=PIPE)
            checksum0 = pro1.communicate()[0].decode().strip()
            checksum0 = checksum0.rstrip('0')
            [alias, step1repo] = session.execute("""
            select alias, step1repo from clique3.player0 where pq = %s
            """, [pq]).one()
            logging.info('alias={0}, step1repo={1}'.format(alias, step1repo))
            if not alias:
                logging.error('alias for pq {0} can not be None'.format(pq))
                return
            if not step1repo:
                logging.eror('step1repo for pq {0} can not be None'.format(pq))
                return
            alias = alias.strip()
            step1repo = step1repo.strip()
            pro1 = Popen([step1repo, prop, checksum0], stdin=None, stdout=PIPE)
            verdict = pro1.communicate()[0].decode().strip()
            verdict = verdict.rstrip('0')
            pro2 = Popen(['./step2', pq, verdict], stdin=None, stdout=PIPE)
            note = pro2.communicate()[0].decode().strip()
            note = note.strip()
            note = note.rstrip('0')
            logging.info(note)
            if not note.startswith('5e5e'):
                logging.error('invalid msg: {0}'.format(note))
                return
            rawtext = str(binascii.a2b_hex(bytes(note, 'utf-8')), 'utf-8')
            logging.debug('rawtext = {0}'.format(rawtext))
            regexp0 = r'\^\^\w+::\w+\|\|\w+\|\|\d-\>\w+@@\w+@@000\$\$'
            m = re.match(regexp0, rawtext)
            if not m:
                logging.error('rawtext is not in good format')
                return
            (left, right) = rawtext.split('->')
            (target, lastsig, lastblock) = right.split('@@')
            (symbol, noteId, quantity) = left.split('||')
            symbol = symbol.split('::')[1]
            logging.info("pq = {0}, symbol= {1}, noteId = {2}, quantity = {3}, \
            lastsig = {4}".format(pq, symbol, noteId, quantity, lastsig))
            if self.verify(pq, symbol, noteId, quantity, lastsig):
                self.save2ownershipcatalog(pq,
                                           verdict,
                                           prop,
                                           rawtext,
                                           symbol,
                                           noteId,
                                           quantity,
                                           target,
                                           lastsig)
                txnTxt = '{0}||{1}||{2}||{3}'.format(pq,
                                                     prop,
                                                     verdict,
                                                     '30001')
                super().postTxn(txnTxt)
        except Exception as err:
            logging.error(err)
        finally:
            cluster.shutdown()
            zk.stop()
            zk.close()

    def verify(self, pq, symbol, noteId, quantity, lastsig):
        cluster, session, kafkaHost, zk = super().setup()
        [owner0, verdict0] = session.execute("""
        select owner, verdict0 from ownership0 where note_id = %s
        """, [noteId]).one()
        [owner1] = session.execute("""
        select alias from player0 where pq = %s
        """, [pq]).one()

        cluster.shutdown()
        zk.stop()
        zk.close()
        logging.info('owner0 = {0}, owner1 = {1}, verdict[-16:] = {2}, \
        lastsig = {3}'.format(owner0, owner1, verdict0, lastsig))
        if owner0 == owner1 and verdict0 == lastsig:
            logging.info('{0}: return True'.format(datetime.now()))
            return True
        logging.info('{0}: return False'.format(datetime.now()))
        return False

    def save2ownershipcatalog(self, pq, verdict, proposal,
                              rawtext, symbol, noteId, quantity,
                              target, lastsig):
        cluster, session, kafkaHost, zk = super().setup()
        zkc = zk.Counter("/noteId3", default=0x7000)
        zkc += 1
        rowId = zkc.value
        session.execute("""
        update ownership0 set owner= %s , updated = toTimestamp(now()), \
        verdict0 = %s where note_id = %s""", [target, verdict[-16:], noteId])
        sha256 = hashlib.sha256()
        sha256.update("{0}{1}".format(noteId.strip(),
                                      target.strip()).encode('utf-8'))
        hashcode = sha256.hexdigest()
        session.execute("""insert into note_catalog0(id, clique, pq, \
        verdict, proposal, note, recipient, hook, stmt, setup, hash_code) \
        values(%s, '3', %s, %s, %s, %s, %s, %s,%s, toTimestamp(now()), %s) \
        """, [int(rowId), pq, verdict, proposal,
              "{0}||{1}||{2}".format(symbol.strip(), noteId.strip(), quantity),
              target, lastsig, rawtext, hashcode])
        logging.info('saving completes')
        cluster.shutdown()
        zk.stop()
        zk.close()


class IssueProposalHandler(HandleBase):
    def queueName(self):
        return 'issue0'

    def processProposal(self, payload):
        cluster, session, kafkaHost, zk = super().setup()
        (symbol, quantity, globalId) = payload.split('||')
        # sha256 = hashlib.sha256()
        # while True:
        #     sha256.update("{0}".format(symbol).encode('utf-8'))
        #     sha256.update("{0}".format(random.random()).encode('utf-8'))
        #     sha256.update("{0}".format(quantity).encode('utf-8'))
        #     digest = sha256.hexdigest()
        #     length = len(digest)
        #     noteId = digest[length-8:]
        #     res = session.execute("""
        #     select * from ownership0 where note_id = %s
        #     """, [noteId])
        #     if not res:
        #         break
        stmt = """
        select repo from clique3.issuer0 where symbol = %s limit 1
        """
        [repopath] = session.execute(stmt, [symbol]).one()
        logging.info(repopath)
        if not repopath:
            logging.eror('binary file for symbol {0} is None'.format(symbol))
            return
        pro3 = Popen([repopath, 'localhost', quantity],
                     stdin=None, stdout=None)
        pro3.wait()
        cluster.shutdown()
        zk.stop()
        zk.close()


class TransferProposalHandler(HandleBase):
    def queueName(self):
        return 'transfer0'

    def processProposal(self, payload):
        try:
            cluster, session, kafkaHost, zk = super().setup()
            stmt = """
            select playerrepo from runtime where id=0
            """
            [folder] = session.execute(stmt).one()
            regexp0 = r'\w+&&\w+\|\|\w+\|\|\d-\>\w+&&\w+&&000&&\w+'
            m = re.match(regexp0, payload)
            if not m:
                logging.error('payload is not in good format')
                return
            alias, rawCode, lastTxn, lastBlock, globalId = payload.split('&&')
            stmt = """
            select repo from clique3.player0 where global_id = %s
            """
            [binarypath] = session.execute(stmt, [globalId]).one()
            if not binarypath:
                logging.error('binarry not found for {0}'.format(globalId))
                return
            [binarypath2] = session.execute("""
            select repo from clique3.player0 where alias = %s
            """, [alias]).one()
            if not binarypath2 or binarypath2 != binarypath:
                logging.info('binary not correct for {0}'.format(alias))
                return
            raw = "^^{0}::{1}@@{2}@@{3}$$".format(
                alias, rawCode, lastTxn, lastBlock)
            logging.info(raw)
            pro3 = Popen([binarypath, 'localhost', raw],
                         stdin=None, stdout=None)
            pro3.wait()
        except Exception as err:
            logging.error(err)
        finally:
            cluster.shutdown()
            zk.stop()
            zk.close()


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    pid = os.fork()
    if pid > 0:
        time.sleep(3)
        sys.exit(0)
    os.setsid()
    sys.stdin.close()
    freopen('./stdoutclique3', 'a', sys.stdout)
    freopen('./stderrclique3', 'a', sys.stderr)

    fmt0 = "%(name)s %(levelname)s %(asctime)-15s %(pathname)s:%(lineno)s \
    %(message)s"
    logging.basicConfig(filename='senate.log', format=fmt0,
                        level=logging.INFO)
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
