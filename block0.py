#!/usr/bin/env python3
# set up block0
import time
from sys import argv
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

cassHost = argv[1]
cluster = Cluster(cassHost.split(','), protocol_version=4,
                  load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'))

session = cluster.connect('instance3')

stmt = 'truncate table forge.blocks_view'
session.execute(stmt)

stmt = 'truncate table forge.raw_txns'
session.execute(stmt)

stmt = """
insert into forge.blocks_view(sha3_256hash, block, nonce, seq, solid_hash, specification, ts, millis)values('f8bb3f089fa0599fcc5bb2adc2577a7771ecc2b62abb7a4a31505938b2bec7af', '<0/b51c189b47a342a58885aa8b8f47d5ff/ff9f3d4ea16e5fc804311a4338ad91eac22ce0c73e4de77d1930c698889df41d01c434846f929d0c4ab8265a5638d69da967688d4bb8442cac2ad912d9797eba910140e0009bdf73e67f2a4209453ab18be91f9d0920ba044e414f41b3b53e85865298820239d61000f06f88269bcfbca327dac0c2e30528c1bef398163abc6a0f5c99f6cd8443dde59c106c63533efc7b67984404e86faa0a093e89161b3ae1>,["In God We Trust"]', '90128c2146b947cd95653ffd83cdd251', 1, 'ff05c60cf9a1138e3f43034b806292a47142f48db71c5748d11cf28bdb09954520920f248c45d92a20f4debabbf563b2cd5770b26a09cb0235aa57273a67cb91dc1e2fa9695a70609823c043b9767f17455891f1402f4b48d9c4af4df4c6e5584525916f766cb375cd1aa33f599a5607ba99d5b14b3687d23b2bed7865feed3f914863372bf840ac4ea90304db800ecdad77382f3c428324ba14b66a81348215', 'Mersenne15Mersenne14', toTimestamp(now()), {0})""".format(int(time.time()*1000))
session.execute(stmt)

stmt = """
update forge.runtime set block_consent='f', block_counter=1, block_ptr='f8bb3f089fa0599fcc5bb2adc2577a7771ecc2b62abb7a4a31505938b2bec7af', interval = 128, nonce='90128c2146b947cd95653ffd83cdd251', solid_hash='ff05c60cf9a1138e3f43034b806292a47142f48db71c5748d11cf28bdb09954520920f248c45d92a20f4debabbf563b2cd5770b26a09cb0235aa57273a67cb91dc1e2fa9695a70609823c043b9767f17455891f1402f4b48d9c4af4df4c6e5584525916f766cb375cd1aa33f599a5607ba99d5b14b3687d23b2bed7865feed3f914863372bf840ac4ea90304db800ecdad77382f3c428324ba14b66a81348215', txn_counter = 0, tick={0} where seq = 0""".format(int(time.time()/128))
session.execute(stmt)

session.execute('truncate table instance3.blocks_view')
session.execute('truncate table instance3.notes_view')
session.execute('truncate table instance3.transactions_view')

stmt = """
insert into instance3.blocks_view(sha3_256hash, block, nonce, seq, solid_hash, specification, ts)values('f8bb3f089fa0599fcc5bb2adc2577a7771ecc2b62abb7a4a31505938b2bec7af', '<0/b51c189b47a342a58885aa8b8f47d5ff/ff9f3d4ea16e5fc804311a4338ad91eac22ce0c73e4de77d1930c698889df41d01c434846f929d0c4ab8265a5638d69da967688d4bb8442cac2ad912d9797eba910140e0009bdf73e67f2a4209453ab18be91f9d0920ba044e414f41b3b53e85865298820239d61000f06f88269bcfbca327dac0c2e30528c1bef398163abc6a0f5c99f6cd8443dde59c106c63533efc7b67984404e86faa0a093e89161b3ae1>,["In God We Trust"]', '90128c2146b947cd95653ffd83cdd251', 1, 'ff05c60cf9a1138e3f43034b806292a47142f48db71c5748d11cf28bdb09954520920f248c45d92a20f4debabbf563b2cd5770b26a09cb0235aa57273a67cb91dc1e2fa9695a70609823c043b9767f17455891f1402f4b48d9c4af4df4c6e5584525916f766cb375cd1aa33f599a5607ba99d5b14b3687d23b2bed7865feed3f914863372bf840ac4ea90304db800ecdad77382f3c428324ba14b66a81348215', 'Mersenne15Mersenne14', toTimestamp(now()))"""
session.execute(stmt)

stmt = """
update instance3.runtime set block_consent='f', block_counter=1, block_ptr='f8bb3f089fa0599fcc5bb2adc2577a7771ecc2b62abb7a4a31505938b2bec7af', interval = 128, nonce='90128c2146b947cd95653ffd83cdd251', solid_hash='ff05c60cf9a1138e3f43034b806292a47142f48db71c5748d11cf28bdb09954520920f248c45d92a20f4debabbf563b2cd5770b26a09cb0235aa57273a67cb91dc1e2fa9695a70609823c043b9767f17455891f1402f4b48d9c4af4df4c6e5584525916f766cb375cd1aa33f599a5607ba99d5b14b3687d23b2bed7865feed3f914863372bf840ac4ea90304db800ecdad77382f3c428324ba14b66a81348215' ,txn_counter = 0 where seq = 0"""
session.execute(stmt)
