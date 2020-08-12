#!/usr/bin/env python3
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


class Handler0(socketserver.BaseRequestHandler):
    def setupCass():
        cluster = Cluster(argv[1].split(','))
        session = cluster.connect('clique3')
        return session, cluster

    def setupKafka():
        kafkaProducer = KafkaProducer(bootstrap_servers=argv[2].split(','))
        return kafkaProducer


class AliasHandler(Handler0):
    # will recv request on user creation
    def handle(self):
        try:
            session, cluster = self.setupCass()
            kafkaProducer = self.setupKafka()
            r0 = session.execute('select pq, e from channel \
where port = 21823').one()
            if not r0:
                logging.info('no pq, e information, exit')
                return
            pq, e = r0.pq, r0.e
            count = str(self.request.recv(8).strip(), 'utf-8')
            if not count or not int(count):
                logging.info('got None payload')
                return
            payload = str(self.request.recv(int(count)).strip(), 'utf-8')
            if not payload:
                logging.info('got None payload')
            args = './crypt', pq, e, payload
            with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
                output = p.stdout.read()
                output = output.rstrip('0')
            rawCode = binascii.a2b_hex(output)
            logging.debug(rawCode)
            if not rawCode[:2] == '^^' or not rawCode[-2:] == '$$':
                logging.info('rawCode format wrong, will ignore')
                return
            # put the rawCode to kafka
            kafkaProducer.send('alias3', key=uuid.uuid4().bytes,
                               value=bytes(rawCode[2:-2], 'utf-8'))
        except Exception as err:
            logging.error(err)
        finally:
            cluster.shutdown()
            kafkaProducer.close()


class IssueHandler(Handler0):
    def handle(self):
        try:
            session, cluster = self.setupCass()
            kafkaProducer = self.setupKafka()
            r0 = session.execute('select pq, e from channel \
where port = 21822').one()
            if r0:
                pq, e = r0.pq, r0.e
            else:
                logging.info('pq/e can not be None')
                return
            count = str(self.request.recv(8).strip(), 'utf-8')
            if not count or not int(count):
                logging.info('got None payload')
                return
            payload = str(self.request.recv(int(count)).strip(), 'utf-8')
            if not payload:
                logging.info('got None payload')
            # the payload format: ^^pq||8$$
            if not payload[:2] == '^^' or not payload[-2:] == '$$':
                logging.info('rawCode format wrong, will ignore')
                return
            payload = payload[2:-2]
            pq, quantity = payload.split('||')
            if not pq:
                logging.info('pq can not be empty')
                return
            if not quantity or quantity not in ['8', '2', '1']:
                logging.info('quantity is not valid: {0}'.format(quantity))
                return
            r0 = session.execute('select symbol from issuer0 \
where pq = %s', [pq]).one()
            if r0:
                symbol = r0.symbol
            else:
                logging.info('symbol can not be empty')
                return
            sha256 = hashlib.sha256()
            while True:
                sha256.update("{0}".format(symbol).encode('utf-8'))
                sha256.update("{0}".format(random.random()).encode('utf-8'))
                sha256.update("{0}".format(quantity).encode('utf-8'))
                digest = sha256.hexdigest()
                noteId = digest[-8:]
                r0 = session.execute('select * from clique3.ownership0 \
where note_id = %s', [noteId])
                if not r0:
                    break
            logging.debug('noteId = {0}'.format(noteId))
            reply = '^^{0}||{1}||{2}$$'.format(symbol, noteId, quantity)
            code = str(binascii.b2a_hex(bytes(reply, 'utf-8')), 'utf-8')
            args = './crypt', pq, e, code
            with subprocess.Popen(args, stdout=subprocess.PIPE) as p:
                output = p.stdout.read()
                size = len(output)
            self.request.send(bytes('{:08}'.format(size), 'utf-8'))
            self.request.send(output)
            count = str(self.request.recv(8).strip(), 'utf-8')
            if not count or not int(count):
                logging.info('got None count, exit')
                return
            else:
                payload = self.request.recv(count).strip()
                kafkaProducer.send('issue3', key=uuid.uuid4().bytes,
                                   value=payload)
        except Exception as err:
            logging.error(err)
        finally:
            cluster.shutdown()
            kafkaProducer.close()


class TransferHandler(Handler0):
    def handle(self):
        try:
            kafkaProducer = self.setupKafka()
            count = str(self.request.recv(8).strip(), 'utf-8')
            if not count or not int(count):
                logging.info('got None payload')
                return
            payload = self.request.recv(int(count)).strip()
            if not payload:
                logging.info('got None payload')
            kafkaProducer.send('transfer3', key=uuid.uuid4().bytes,
                               value=payload)
        except Exception as err:
            logging.error(err)
        finally:
            kafkaProducer.close()


if __name__ == '__main__':
    fmt0 = "%(name)s %(levelname)s %(asctime)-15s %(process)d \
%(thread)d %(pathname)s:%(lineno)s %(message)s"
    logging.basicConfig(format=fmt0,
                        filename='clique0.log',
                        level=logging.INFO)

    with socketserver.TCPServer((argv[1], 21821), TransferHandler) as transfer:
        p21821 = Process(target=transfer.serve_forever)
        p21821.start()
    with socketserver.TCPServer((argv[1], 21822), IssueHandler) as issue:
        p21822 = Process(target=issue.serve_forever)
        p21822.start()
    with socketserver.TCPServer((argv[1], 21823), AliasHandler) as alias:
        p21823 = Process(target=alias.server_forever)
        p21823.start()
