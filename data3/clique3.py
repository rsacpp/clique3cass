#!/usr/bin/env python3

import os
import time
import sys
import signal
import hashlib
import configparser

from datetime import datetime
from cassandra.cluster import Cluster


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
        cluster = Cluster(cassHost.split(','))
        session = cluster.connect(cassKeyspace)
        return cluster, session, kafkaHost

    def process(self):
        pass
        
class AliasHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost = setup()
        kafka = KafkaConsumer('alias3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        for m in kafka:
            payload = str(m.value, 'utf-8')
            #save it to cass
            alias, globalId = payload.split('||')
            stmt = """
            insert into executions(code, ts, payload) values('alias3', toTimestamp(now()), %s)
            """
            session.execute(stmt, [payload])
            while os.getloadavg()[0] > 1:
                print('it is too hot, sleep 2 seconds')
                time.sleep(2)
                        with lock0:
            # the operation
            pro0 = Popen(['/usr/bin/perl', 'keywrapper.pl', baseDir, '2048'], stdin=None, stdout=None, cwd='/var/tmp')
            pro0.wait()
            pro1 = Popen(['/usr/bin/perl', 'makepayer.pl', alias, globalId], stdin=None, stdout=None, cwd='/var/tmp')
            pro1.wait()

class SymbolHandler(HandleBase):
    def process(self):
        cluster, session, kafkaHost = setup()
        kafka = KafkaConsumer('symbol3',
                              group_id='clique3',
                              bootstrap_servers=kafkaHost.split(','))
        for m in kafka:
            pass

class IssueHandler(HandleBase):
    def process(self):
        pass

class TransferHandler(HandleBase):
    def process(self):
        pass

        

            

        
