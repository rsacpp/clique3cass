/**
* step1v2.cpp for Clique3
* Copyright (C) 2018, Gu Jun
* 
* This file is part of Clique3.
* Clique3 is  free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or (at
* your option) any later version.

* Clique3 is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.

* You should have received a copy of the GNU General Public License
* along with Clique3. If not, see <http://www.gnu.org/licenses/>.
**/

#include "bn40.h"
using namespace std;

int
main(int argc, char* argv[]){

  string* v  = new string(argv[1]);
  /*checksum part*/
  string* checksum = new string(argv[2]);
  string* pq2 = new string("");
  string* d2 = new string("10001");
  bn40* checksum_v  = fromhex(checksum);
  bn40* pq2_v = fromhex(pq2);
  bn40* d2_v = fromhex(d2);
  bn40* r2_v = npmod(checksum_v, d2_v, pq2_v);
  string* r2 = r2_v->tohex();
  delete r2_v;
  delete d2_v;
  delete pq2_v;
  delete checksum_v;
  delete checksum;
  delete pq2;
  delete d2;

  if(v->find(*r2)==string::npos){
    delete v;
    delete r2;
    return 0;
  }
  delete r2;
  
  /*endof checksum part*/
  string*key = new string("STEP1KEY");
  int pos = key->find("@@");
  string* pq = new string(key->substr(0,pos));
  string* d  = new string(key->substr(pos+2));
  bn40* _pq = fromhex(pq);
  bn40* _d  = fromhex(d);
  bn40* _v  = fromhex(v);
  bn40* r = npmod(_v,_d,_pq);
  string* rr = r->tohex();
  cout<< *rr <<endl;
  delete key;
  delete rr;
  delete r;
  delete _pq;
  delete _d;
  delete _v;
  delete d;
  delete v;
  delete pq;
  return 0;
}
