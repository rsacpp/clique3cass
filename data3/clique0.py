#!/usr/bin/env python3
import os
import time
import sys
import socketserver
import subprocess
import binascii
import uuid
import logging
import random
import hashlib
from sys import argv
from multiprocessing import Process
from cassandra.cluster import Cluster
from kafka import KafkaProducer


def handle_exit(signum):
    sys.exit(0)


def freopen(f, mode, stream):
    oldf = open(f, mode)
    oldfd = oldf.fileno()
    newfd = stream.fileno()
    os.close(newfd)
    os.dup2(oldfd, newfd)


class Handler0(socketserver.BaseRequestHandler):
    def setupCass(self):
        cluster = Cluster(argv[1].split(','))
        session = cluster.connect('clique3')
        return session, cluster

    def setupKafka(self):
        kafkaProducer = KafkaProducer(bootstrap_servers=argv[2].split(','))
        return kafkaProducer


class IssueHandler(Handler0):
    def handle(self):
        session, cluster = self.setupCass()
        kafkaProducer = self.setupKafka()
        try:
            r0 = session.execute('select pq, d from channel \
where port = 21822').one()
            if r0:
                pq, d = r0.pq, r0.d
            else:
                logging.info('pq/e can not be None')
                return
            logging.debug('pq = {0}, d = {1}'.format(pq, d))
            count = str(self.request.recv(8).strip(), 'utf-8')
            if not count or not int(count):
                logging.info('got None payload')
                return
            payload = str(self.request.recv(int(count)).strip(), 'utf-8')
            logging.debug(payload)
            if not payload:
                logging.info('got None payload')
            # the payload format: ^^pq||8$$
            if not payload[:2] == '^^' or not payload[-2:] == '$$':
                logging.info('rawCode format wrong, will ignore')
                return
            payload = payload[2:-2]
            pq0, quantity0 = payload.split('||')
            if not pq0:
                logging.info('pq0 can not be empty')
                return
            if not quantity0 or quantity0 not in ['8', '2', '1']:
                logging.info('quantity is not valid: {0}'.format(quantity0))
                return
            r0 = session.execute('select symbol from issuer0 \
where pq = %s', [pq0]).one()
            if r0:
                symbol = r0.symbol
            else:
                logging.info('symbol can not be empty')
                return
            sha256 = hashlib.sha256()
            while True:
                sha256.update("{0}".format(symbol).encode('utf-8'))
                sha256.update("{0}".format(random.random()).encode('utf-8'))
                sha256.update("{0}".format(quantity0).encode('utf-8'))
                digest = sha256.hexdigest()
                noteId = digest[-8:]
                r0 = session.execute('select * from clique3.ownership0 \
where note_id = %s', [noteId])
                if not r0:
                    break
            logging.debug('noteId = {0}'.format(noteId))
            reply = '^^{0}||{1}||{2}$$'.format(symbol, noteId, quantity0)
            logging.debug(reply)
            code = str(binascii.b2a_hex(bytes(reply, 'utf-8')), 'utf-8')
            logging.debug(code)
            args = './crypt', pq, d, code
            with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
                output = p.stdout.read().strip()
                size = len(output)
                logging.debug(output)
            self.request.send(bytes('{:08}'.format(size), 'utf-8'))
            self.request.send(output)

            count = str(self.request.recv(8).strip(), 'utf-8')
            logging.debug('count={0}'.format(count))
            if not count or not int(count):
                logging.info('got None count, exit')
                return
            else:
                payload = self.request.recv(int(count)).strip()
                logging.debug(payload.decode('utf-8'))
                kafkaProducer.send('issue3', key=uuid.uuid4().bytes,
                                   value=payload)
        except Exception as err:
            logging.error(err)
        finally:
            cluster.shutdown()
            kafkaProducer.close()


class TransferHandler(Handler0):
    def handle(self):
        kafkaProducer = self.setupKafka()
        try:
            count = str(self.request.recv(8).strip(), 'utf-8')
            if not count or not int(count):
                logging.info('got None payload')
                return
            payload = self.request.recv(int(count)).strip()
            if not payload:
                logging.info('got None payload')
            logging.debug(payload.decode('utf-8'))
            kafkaProducer.send('transfer3', key=uuid.uuid4().bytes,
                               value=payload)
        except Exception as err:
            logging.error(err)
        finally:
            kafkaProducer.close()


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
    freopen('./stdoutclique0', 'a', sys.stdout)
    freopen('./stderrclique0', 'a', sys.stderr)

    fmt0 = "%(name)s %(levelname)s %(asctime)-15s %(process)d \
%(thread)d %(pathname)s:%(lineno)s %(message)s"
    logging.basicConfig(format=fmt0,
                        filename='clique0.log',
                        level=logging.INFO)

    with socketserver.TCPServer((argv[3], 21821), TransferHandler) as transfer:
        p21821 = Process(target=transfer.serve_forever)
        p21821.start()
    with socketserver.TCPServer((argv[3], 21822), IssueHandler) as issue:
        p21822 = Process(target=issue.serve_forever)
        p21822.start()
