/**
* payertemp.cpp for Clique3
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
  string* input = new string(argv[1]);
  if((input->find("e500e500") !=0 )||(input->rfind("42004200") + 8 != input->length())){
    delete input;
    cout<<"format error"<<endl;
    return 0;
  }
  string* key = new string("KEY");
  int pos = key->find("@@");
  string* pq = new string(key->substr(0,pos));
  string* id = new string(key->substr(pos + 2));
  bn40* _cre = fromhex(id);

  bn40* _val = fromhex(input);
  bn40* _pq = fromhex(pq);
  bn40* r = npmod(_val,_cre,_pq);
  cout<<*pq<<"@@";
  string* r2 = r->tohex();
  cout<< *r2<<endl;
  delete r2;
  delete _pq;
  delete r;
  delete _val;
  delete pq;
  delete _cre;
  delete input;
  delete id;
  delete key;
  return 0;
}
