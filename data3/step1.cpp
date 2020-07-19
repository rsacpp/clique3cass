/**
* step1.cpp for Clique3
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
  string* pq = new string(argv[1]);
  string* d  = new string(argv[2]);
  string* v  = new string(argv[3]);
  bn40* _pq = fromhex(pq);
  bn40* _d  = fromhex(d);
  bn40* _v  = fromhex(v);
  bn40* r = npmod(_v,_d,_pq);
  string* rr = r->tohex();
  cout<< *rr <<endl;
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
