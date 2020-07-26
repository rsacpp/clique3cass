-- 
-- clique3.sql(for postgresql) for Clique3
-- Copyright (C) 2018, Gu Jun
-- 
-- This file is part of Clique3.
-- Clique3 is  free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or (at
-- your option) any later version.

-- Clique3 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.

-- You should have received a copy of the GNU General Public License
-- along with Clique3. If not, see <http://www.gnu.org/licenses/>.
create keyspace clique3 with replication={'class':'SimpleStrategy', 'replication_factor': 1};

create table channel(
peer text,
port int,
pq text,
d text,
e text,
primary key(peer, port)
);
create index channel_port on channel(port);

insert into channel(peer, port, pq, d, e)values('127.0.0.1', 12821,'d19ef43ec1f584d92f6bddd41bdc722d8867fc33e276c655d050127e1699e3c641e757a11b6e8cc783b08104b70610ec3889965fe6495d439073eb0cad3bc381f86b099f1206ad1e565a2f85d035322f67caa011bbc3bebd797ffc23ca259d74003c6abfd1e31ba5f1b271d0fee6528733d3d20c82d337d43c64704e9848d575dcf4db8095f97ea9d4baa6ab0f21ae13e0b076e6970c43d70d4fd6115e15524865044a71c60134dcb98bd35de7c68203561a2da37986eda7be66e3b37949fabc00b596d07ded713de3ce172a29f0f62a0b57ae32c099c2461567d7ecd5533ef6ace70f1791085878c810bafcc3480adb50c4896a45b3e39c675b3fd6f8eacb6e','9b425c123b5b611432494f21dad84056162b45dfdb06cd03dce2fe94b82387fa987bb887af0ccd04538d677f60099f8212dd58cec58d177d81c1888b5302b86511d4ed151a4ec5d37ab5a728ef8924888937dec3d8831c9f2de62789b5f1dab51eb197a03bac754e5d0b2dbbaecfca434769404491c0489858c79bd771d54d3585645dca465fc77bc954ea75b6ea8882a42e2eb069f6b9e5af0eb327b8ae1826719b7211765123e2e8ea161f802a4f0f38b342b976c22fea515bf59c1fd6e0b14a4ad987b4042c8f8660d5c681657d2e51b8987900aef95c330f368b060a46084ec547104788bd3040c98c93fc21251f3176e56127cea580a9532a02083e8a45' ,'');

create table encrypt(
port int,
peer text,
pq text,
e text,
primary key(port)
);

insert into encrypt(port, peer, e, pq) values(12822, '127.0.0.1', 'f81c5b2e25e878ab52efbd6fe3fe50fd', '70907a225af2602e541f802a86da2d916ad0e3c87ccbb7bc6a6c30b7712af73583f503859e574d4448ef31898e5b9f34e019239b495ec3320820a0b7fe41de7b331c4a2c98ac2e0ca8bea794dba9b066a8690f8e06f82c445b02d7cce1cb28bdbcc43002fd467ddc2d449b57ac5488fba3422bb8fcc3e1f944fb70679f9f7e42ca5e8d782afd6aad006f1bb7f5d61797fc5aa2f38ae50b7385b5cc7dcb09484cb38ba0f2549caa23e1df2e75b4a4a43de90388b92920a87e659727683b984f21f94a0458376011e5359d13dbcaaa95a0542bce901aa1380ee780a626bf772f789c81c164bbf1378b6d8df1138990d26d284962d1e29aed6533f658c590a69b5a');

create table player0(
id bigint,
clique text,
global_id text,
pq text,
d text,
alias text,
setup timestamp,
hash_code text,
primary key(id)
);
create index player0_pq on player0(pq);
create index player0_global_id on player0(global_id);
create index player0_alias on player0(alias);

create table issuer0(
id bigint,
clique text,
global_id text,
pq text,
d text,
alias text,
symbol text,
setup timestamp,
hash_code text,
primary key(id)
);
create index issuer0_pq on issuer0(pq);
create index issuer0_symbol on issuer0(symbol);

create table ownership0(
seq bigint,
clique text,
symbol text,
note_id text,
quantity int,
owner text,
updated timestamp,
hash_code text,
primary key(note_id)
);
create index ownership0_seq on ownership0(seq);

create table note_catalog0(
id bigint,
clique text,
pq text,
verdict text,
proposal text,
note text,
recipient text,
hook text,
stmt text,
setup timestamp,
hash_code text,
primary key(id)
);
create index note_catalog0_note on note_catalog0(note);


create table reserved0(
seq bigint,
word text,
primary key(word)
);

create table executions(
id bigint,
code text,
ts timestamp,
payload text,
primary key(id)
);
create index executions_code on executions(code);

create table runtime(
id int,
playerrepo text,
step1repo text,
load1_threshold decimal,
checksumpq text,
checksumd text,
checksume text,
primary key(id)
);
insert into runtime (id, playerrepo, step1repo, load1_threshold) values(0, '/tmp/var/player', '/tmp/var/step1', 0.7);
update runtime set checksumd = 'd9ae0dd8d040491a0982c8776666c63e8c8acc3638e5a843592d200f073a1c46' , checksumpq  = '55251ebd654d6e0f308291d2367f9177bba9f463c6163518db0ea2e2bf8c14e9', checksume = '10001' where id= 0;

