#!/usr/bin/env python3
# set up the channels
import psycopg2
from sys import argv

clique3conn = psycopg2.connect("dbname={0} user={1}".format('clique3', 'clique3'))
clique3session = clique3conn.cursor()

forgeconn = psycopg2.connect("dbname={0} user={1}".format('forge', 'clique3'))
forgesession = forgeconn.cursor()

instance3conn = psycopg2.connect("dbname={0} user={1}".format('instance3', 'clique3'))
instance3session = instance3conn.cursor()

primaryHost = argv[1]

stmt = """
delete from channel where peer='*' and port = 21822
"""
clique3session.execute(stmt)

stmt = """
delete from channel where peer='{0}' and port = {1}
""".format(primaryHost, 12821)
clique3session.execute(stmt)

stmt = """
delete from channel where peer='{0}' and port = {1}
""".format(primaryHost, 12822)
forgesession.execute(stmt)

stmt = """
delete from channel where peer='{0}' and port = {1}
""".format(primaryHost, 12823)
instance3session.execute(stmt)

stmt = """insert into channel(peer, port, pq, d)values('*', 21822, 'd3d19b266dcc7393b544f5d4cb582d3cf44d4a4d3a4254ad875d5d253e43fa97293f8c133c9ac8242abf73a42cbad81abccfa36f4042d93a252313070d6ea4db6fe1bba792aa9e17c486bac695a9dbbf883d6a2ce287213db015970a366f9eefd940b0ce13263624876dc9c7c2015e2b8d1829568bb60d4be2d591d81a1ee70f', '97abccdfb45a4829aafa4be61ebb13c55a7b1a994111a3513906c9d47a8dcc1267aa81915f8b123bfc6d8a3c77117ae3a14c466abaf8ac0616dbc533e125b314cb7b0232563eadbe3b29293a051ce4cd21181cadb96e02fa2b4c63cdd47f0f158ff016c14b3f176e996eab78eaaeeb728a4758a243f90b0a118f1bccef1ffe7a')"""
clique3session.execute(stmt)

stmt = """
insert into channel(peer, port, pq, d) values('{0}', 12821, '3b18bfc56b053e2b0fb91b56de85b3410918d2a428a68d28e55892fb52a7e7ece12002d2e98f654b7eaf480f56f603d90c517e8923bb70076717a1997411edc2baa6d9a58fe147a27d87357929b0c69c423033d3d883b9f23defd1949d1dab5c',
'12e7a5ef2408abd2a34c4463b1250cd4480110d2cdbab13e906e020ca4d1641b5e219fd480847f8b0a4d17bd346779f8126d9e8f72f45d6b0b4799ac69942d7e739d57898835d7e5b311e0ca9991e8f6be6724498889499d030b481e21700418')""".format(primaryHost)
clique3session.execute(stmt)

stmt = """
insert into channel(peer, port, pq,  e) values('{0}', 12821, '3b18bfc56b053e2b0fb91b56de85b3410918d2a428a68d28e55892fb52a7e7ece12002d2e98f654b7eaf480f56f603d90c517e8923bb70076717a1997411edc2baa6d9a58fe147a27d87357929b0c69c423033d3d883b9f23defd1949d1dab5c','95045c28f14796793d2596eec43146ee')
""".format(primaryHost)
forgesession.execute(stmt)

stmt = """
insert into channel(peer, port, pq, d, e) values('{0}', 12822, '1e5c36efefc4dda52e111289a5b261a68a0b595730c84103243cc17ae636a818aa6df9b25281d060b6bb19b670d7a67e14d745d54b3f8089b182381fffa81b2b8fcedbed75a52ff3d559f581cf7f03360d1a0886f3d8ca1371f7e092ee3f55ba',
'9e24abea289a9c70e63d13167eb37fcaa58577d0a77999e7966183e915b9097fc3f3916e4d51b0c6e3517229449b60959e9e74741a3289e05e9294f8dc281834c1299fb00fb7698bbf3aeb2f0e0a3a7b7a10ba6432acfaa5950dd67347f03e67','95be10ff1fbca034458d1558a290648d')
""".format(primaryHost)
forgesession.execute(stmt)


stmt = """
insert into channel(peer, port, pq, d) values('{0}', 12823, '7e6d15d35b3c657b31cd986c70b121ed1c582e3ea235a814fdb7792bd951c4e47e86327eb8e6c67b5ff02474b3e2db1dba8a1ab7635cb77d37d291226a28dd3c56cd7423700a6b03e8f008ced9af97ff5d6b895aa9608777178a77e364013c3a',
'be28a1a98f59df2d0e4473e2a859b66d3e523891d64a639a68d0190d9faeed16c009230b6427ac828ba0d8e7dbe9bd18bbaa5aa1a5252588abe91d03169977de1a2e10b6a48d40fcbb205d659cdd0b5887b8796e8ce16d768b2eb364d1261c89')
""".format(primaryHost)
instance3session.execute(stmt)

stmt = """
insert into channel(peer, port, pq, e) values('172.31.50.102', 12823, '7e6d15d35b3c657b31cd986c70b121ed1c582e3ea235a814fdb7792bd951c4e47e86327eb8e6c67b5ff02474b3e2db1dba8a1ab7635cb77d37d291226a28dd3c56cd7423700a6b03e8f008ced9af97ff5d6b895aa9608777178a77e364013c3a',
'3e3748164a59612df36689c949d589fc')
"""
forgesession.execute(stmt)

clique3session.commit()
clique3session.close()
clique3conn.close()

forgesession.commit()
forgesession.close()
forgeconn.close()

instance3session.commit()
instance3session.close()
instance3conn.close()
