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

drop table player0;
create table player0(
id bigint,
clique text,
"globalId" text,
pq text,
d text,
alias text,
setup timestamp,
"hashCode" text --hashCode over id
);


drop table issuer0;
create table issuer0(
id bigint,
clique text,
"globalId" text,
pq text,
d text,
alias text,
symbol text,
setup timestamp,
"hashCode" text --hashCode over id
);


drop table ownership0;
create table ownership0(
id bigint,
clique text,
symbol text,
"noteId" text,
quantity int,
owner text,
updated timestamp,
"hashCode" text --hashcode over id 
);


drop table issue_redo0;
create table issue_redo0(
id serial,
clique text,
"globalId" text,
proposal text,
setup timestamp,
progress int
);


drop table transfer_redo0;
create table transfer_redo0(
id serial,
clique text,
"globalId" text,
proposal text,
setup timestamp,
progress int
);


drop table alias_redo0;
create table alias_redo0(
id serial,
clique text,
"globalId" text,
alias text,
setup timestamp,
progress int
);

drop table symbol_redo0;
create table symbol_redo0(
id serial,
clique text,
"globalId" text,
symbol text,
setup timestamp,
progress int
);

drop table note_catalog0;
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
"hashCode" text 
);

drop table runstat0;
create table runstat0(
id serial,
executable text,
ints timestamp,
inload decimal,
outts timestamp,
outload decimal,
nodename text
);


drop table con0;
create table con0(
id serial,
param text,
val text
);

drop table params0;
create table params0(
id serial,
clique text,
pq text,
d text
);

drop table reserved0;
create table reserved0(
id serial,
word text
);

drop table propose_issue;
create table propose_issue(
id serial,
"globalId" text,
symbol text,
quantity int,
setup timestamp,
progress int
);

drop table propose_transfer;
create table propose_transfer(
id serial,
"globalId" text,
alias text,
"rawCode" text,
lastsig3 text,
setup timestamp,
progress int
);
