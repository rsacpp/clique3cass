/**
* bn40.cpp for Clique3
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
#include <cstring>
using namespace std;

int
main(int argc, char* argv[]){
  string* input = new string(argv[1]);
  int pos = input->find("@@");
  if(argc < 2 || pos < 0){
    cout << "usage: ./verify3 {XXXX@@XXXX}" << endl;
    delete input;
    return 0;
  }
  string* pq = new string(input->substr(0, pos));
  string* v  = new string(input->substr(pos + 2));
  bn40* _pq = fromhex(pq);
  bn40* _e = new bn40(1);
  _e->addat(0,0x10003);
  bn40* _v  = fromhex(v);
  bn40* r = npmod(_v,_e,_pq);
  string* rr = r->tohex();
  /*cout <<*rr<<endl;
   */
  if(rr->find("e500e500") !=0 ){
    cout<<"wrong code"<<endl;
  }else{
    char* codes = new char[rr->length() + 1];
    std::strcpy(codes,rr->c_str());
    for(int i = 0; i < rr->length(); i = i + 4){
      char val = 0;
      for(int j = 0; j < 4; j++){
	char ch = codes[i + j];
	if((ch >= '0') &&( ch <='9')){
	  val+= ((ch - '0')<<(j*4));
	}
	if((ch >= 'a') && (ch <='f')){
	  val += ((ch - 'a' + 10)<<(j*4));
	}
      }
      cout<<val;
    }
    cout<<endl;
    delete[] codes;
  }
  delete rr;
  delete r;
  delete _pq;
  delete _e;
  delete _v;
  delete v;
  delete pq;
  delete input;
  return 0;
}
