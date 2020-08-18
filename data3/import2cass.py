#!/usr/bin/python3

from kazoo.client import KazooClient
from cassandra.cluster import Cluster
import hashlib
import os
import sys
sys.path.append('./util.py')
import util

zkHost = 'localhost:2181'

f = open('d.key', 'r')
txt = ''
while True:
    en = f.readline()
    if(en == ''):
        break
    txt += en
f.close()

arr = txt.split('@@')
pq = arr[0].strip()
d = arr[1].strip()
alias = sys.argv[1]
globalId = sys.argv[2]


zk = KazooClient(hosts=zkHost)
zk.start()
zkc = zk.Counter("/aliasId3", default=0x700)
zkc += 1
entryId = zkc.value
zk.stop()
zk.close()

sha256 = hashlib.sha256()
sha256.update('{0}'.format(entryId).encode('utf-8'))
hashCode = sha256.hexdigest()
print("entryId = {0}, hashCode = {1}".format(entryId, hashCode))

cluster = Cluster(['localhost'])
session = cluster.connect('clique3')
stmt = """
select playerrepo, step1repo from runtime where id=0
"""
(playerrepo, step1repo) = session.execute(stmt).one()
# a random path
path = '{0:02x}'.format(random.randint(0,255))

playerrepo = '{0}/{1}/'.format(playerrepo, path)
step1repo = '{0}/{1}/'.format(step1repo, path)

stmt = """
insert into player0(id, clique, global_id, pq, d, alias, hash_code, setup, repo, step1repo)
values(%s, '3', %s, %s, %s, %s, %s, toTimestamp(now()), %s, %s)
"""
session.execute(stmt, [int(entryId), globalId, pq, '', alias, hashCode,
                       '{0}/payer3{1}'.format(playerrepo, alias),
                       '{0}/step1{2}'.format(step1repo, alias)])


#os.popen('mkdir -p {0};mkdir -p {1}'.format(playerrepo, step1repo))
print("playerepo = {0}, step1repo = {1}".format(playerrepo, step1repo))

os.popen("mv payer3{0} {1}".format(alias, playerrepo))
os.popen("mv step1{0}    {1}".format(alias, step1repo))

cluster.shutdown()
