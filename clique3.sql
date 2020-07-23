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

