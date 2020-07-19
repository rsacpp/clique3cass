/**
* bn40.h for Clique3
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

#ifndef BN40
#define BN40
#include <iostream>
#include <string>
using namespace std;

/*bn40(hex) = bn64
 */
class bn40{
private:
  bn40(){};
  bn40(bn40& ){};
public:
  size_t* _ele;
  size_t _len;
  bn40(size_t len);
  virtual ~bn40();
  void addat(size_t pos, size_t v);
  void subat(size_t pos, size_t v);
  void shrink();
  bn40* leftpush(size_t bits);
  bn40* clone();
  size_t bits();
  void print();
  /*  void setpos(size_t pos);*/
  string* tohex();
};
/*20(hex) 32
 */
static const size_t _bits20 = 0xffffffff;

bn40* fromhex(string* txt);
bn40* add(bn40*, bn40*);
int cmp(bn40*, bn40*);
bn40* sub(bn40*, bn40*);
bn40* mul(bn40*, bn40*);
bn40* mod(bn40*, bn40*);
/*void div(bn40* a, bn40* b, bn40* r);*/
bn40* npmod(bn40* a, bn40* b, bn40* c);

bn40* mersenne(size_t n);
#endif
