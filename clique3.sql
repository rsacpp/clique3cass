
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

insert into clique3.channel(peer, port, pq, d)values('*', 21822, 'd3d19b266dcc7393b544f5d4cb582d3cf44d4a4d3a4254ad875d5d253e43fa97293f8c133c9ac8242abf73a42cbad81abccfa36f4042d93a252313070d6ea4db6fe1bba792aa9e17c486bac695a9dbbf883d6a2ce287213db015970a366f9eefd940b0ce13263624876dc9c7c2015e2b8d1829568bb60d4be2d591d81a1ee70f', '97abccdfb45a4829aafa4be61ebb13c55a7b1a994111a3513906c9d47a8dcc1267aa81915f8b123bfc6d8a3c77117ae3a14c466abaf8ac0616dbc533e125b314cb7b0232563eadbe3b29293a051ce4cd21181cadb96e02fa2b4c63cdd47f0f158ff016c14b3f176e996eab78eaaeeb728a4758a243f90b0a118f1bccef1ffe7a');

insert into channel(peer, port, pq, d, e)values('127.0.0.1', 12821,'d19ef43ec1f584d92f6bddd41bdc722d8867fc33e276c655d050127e1699e3c641e757a11b6e8cc783b08104b70610ec3889965fe6495d439073eb0cad3bc381f86b099f1206ad1e565a2f85d035322f67caa011bbc3bebd797ffc23ca259d74003c6abfd1e31ba5f1b271d0fee6528733d3d20c82d337d43c64704e9848d575dcf4db8095f97ea9d4baa6ab0f21ae13e0b076e6970c43d70d4fd6115e15524865044a71c60134dcb98bd35de7c68203561a2da37986eda7be66e3b37949fabc00b596d07ded713de3ce172a29f0f62a0b57ae32c099c2461567d7ecd5533ef6ace70f1791085878c810bafcc3480adb50c4896a45b3e39c675b3fd6f8eacb6e','9b425c123b5b611432494f21dad84056162b45dfdb06cd03dce2fe94b82387fa987bb887af0ccd04538d677f60099f8212dd58cec58d177d81c1888b5302b86511d4ed151a4ec5d37ab5a728ef8924888937dec3d8831c9f2de62789b5f1dab51eb197a03bac754e5d0b2dbbaecfca434769404491c0489858c79bd771d54d3585645dca465fc77bc954ea75b6ea8882a42e2eb069f6b9e5af0eb327b8ae1826719b7211765123e2e8ea161f802a4f0f38b342b976c22fea515bf59c1fd6e0b14a4ad987b4042c8f8660d5c681657d2e51b8987900aef95c330f368b060a46084ec547104788bd3040c98c93fc21251f3176e56127cea580a9532a02083e8a45' ,'');

create table player0(
id bigint,
clique text,
global_id text,
pq text,
d text,
alias text,
setup timestamp,
hash_code text,
repo text,
step1repo text,
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
repo text,
step1repo text,
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
verdict0 text,
updated timestamp,
hash_code text,
primary key(note_id)
);
create index ownership0_seq on ownership0(seq);
create index ownership0_symbol on ownership0(symbol);


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

create table issue0stat(
ts bigint,
symbol text,
primary key(ts, symbol)
);
create index issue0stat_symbol on issue0stat(symbol);

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

