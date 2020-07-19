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
#include <iostream>
#include <string>
using namespace std;

bn40::bn40(size_t len){
  this->_len = len;
  this->_ele = new size_t[len];
  for(size_t i=0; i < len; i++){
    this->_ele[i] = 0;
  }
}

bn40::~bn40(){
  delete[] this->_ele;
}

size_t bn40::bits(){
  this->shrink();
  size_t v = 0x40 * this->_len ;
  size_t tmp = 0x8000000000000000;
  size_t p = this->_ele[this->_len - 1];

  while(((p & tmp) == 0) && (v > 0)){
    tmp = tmp >> 1;
    v--;
  }
  return v;
}

bn40* bn40::leftpush(size_t bits){
  size_t i = bits % 0x40;
  size_t o = bits / 0x40;
  bn40* r;
  if(i == 0){
    r = new bn40(this->_len + o);
    for(size_t index=0; index < this->_len; index++){
      r->addat(index + o, this->_ele[index]);
    }
  }else{
    r = new bn40(this->_len + o + 1);
    size_t remain = 0x40 - i;
    for(size_t index=0; index < this->_len; index++){
      r->addat(index + o, this->_ele[index] << i);
      r->addat(index + o + 1, this->_ele[index] >> remain);
    }
  }
  r->shrink();
  return r;
}

void bn40::addat(size_t p, size_t v){
  size_t val = this->_ele[p];
  size_t sum = val + v;
  this->_ele[p] = sum;
  if(sum < val){
    this->addat(p + 1, 1);
  }
}

void bn40::subat(size_t p, size_t v){
  size_t val = this->_ele[p];
  size_t out = val - v;
  this->_ele[p] = out;
  if(out > val){
    this->subat(p + 1, 1);
  }
}

void bn40::shrink(){
  size_t index = this->_len - 1;
  while(index > 0){
    if(this->_ele[index] == 0){
      index--;
    }else{
      break;
    }
  }
  this->_len = index + 1;
}

int cmp(bn40* a, bn40* b){
  int r = 0; /*by default a == b*/
  a->shrink();
  b->shrink();

  if(a->_len > b->_len){
    return 1;
  }
  if(a->_len < b->_len){
    return -1;
  }
  size_t index = a->_len - 1;
  while((a->_ele[index] == b->_ele[index]) && (index > 0)){
    index--;
  }
  if(a->_ele[index] > b->_ele[index]){
    return 1;
  }
  if(a->_ele[index] < b->_ele[index]){
    return -1;
  }
  return r;
}

bn40* add(bn40* a, bn40* b){
  a->shrink();
  b->shrink();
  size_t len = a->_len;
  if( len < b->_len){
    len = b->_len;
  }
  len += 1;
  bn40* r = new bn40(len);
  int index = 0;
  for(; index < a->_len; index++){
    r->addat(index, a->_ele[index]);
  }
  index = 0;
  for(; index < b->_len; index++){
    r->addat(index, b->_ele[index]);
  }
  r->shrink();
  return r;
}

bn40* sub(bn40* a, bn40* b){
  a->shrink();
  b->shrink();
  bn40* r = new bn40(a->_len);
  int index = 0;
  for(; index < a->_len; index++){
    r->addat(index, a->_ele[index]);
  }
  index = 0;
  for(; index < b->_len; index++){
    r->subat(index, b->_ele[index]);
  }
  r->shrink();
  return r;
}

bn40* mul(bn40* a, bn40* b){
  a->shrink();
  b->shrink();
  size_t len = a->_len + b->_len;
  bn40* r = new bn40(len);
  size_t ia = 0;
  size_t ib = 0;
  size_t index = 0;
  for( ia = 0; ia < a->_len; ia++){
    size_t aright = a->_ele[ia] & _bits20;
    size_t aleft = a->_ele[ia] >> 0x20;
    for(ib = 0; ib < b->_len; ib++){
      size_t bright = b->_ele[ib] & _bits20;
      size_t bleft = b->_ele[ib] >> 0x20;
      index = ia + ib;
      r->addat(index, aright * bright);
      r->addat(index + 1, aleft * bleft);
      size_t val1 = aleft * bright;
      r->addat(index, val1 << 0x20);
      r->addat(index + 1, val1 >> 0x20);
      size_t val2 = aright * bleft;
      r->addat(index, val2 << 0x20);
      r->addat(index + 1, val2 >> 0x20);
    }
  }
  r->shrink();
  return r;
}

bn40* bn40::clone(){
  this->shrink();
  bn40* r = new bn40(this->_len);
  size_t i = 0;
  for(; i < this->_len; i++){
    r->_ele[i] = this->_ele[i];
  }
  return r;
}

bn40* mod(bn40* a, bn40* b){
  /*if a < b*/
  if(cmp(a,b) < 0){
    bn40* r = a->clone();
    return r;
  }
  int diff = a->bits() - b->bits();
  if(diff < 0){
    cout<<"logic error, diff = "<<diff<<endl;
  }
  if( diff == 0){
    bn40* tmp = sub(a, b);
    bn40* r = mod(tmp, b);
    delete tmp;
    return r;
  }else{
    bn40* nb = b->leftpush(diff);
    bn40* nb1 = b->leftpush(diff - 1);
    bn40* tmp;
    if(cmp(a, nb) >= 0){
      tmp = sub(a, nb);
    }else{
      tmp = sub(a, nb1);
    }
    bn40* r = mod(tmp, b);
    delete tmp;
    delete nb;
    delete nb1;
    return r;
  }
}

bn40* npmod(bn40* a, bn40* b, bn40* c){
  a->shrink();
  b->shrink();
  c->shrink();
  size_t bbits = b->bits();

  bn40* ar[bbits];
  ar[0] = mod(a,c);
  size_t index = 1;
  /*  cout<<"L247"<<endl;*/
  for(index = 1; index < bbits; index++){
    bn40* m = mul(ar[index - 1], ar[index - 1]);
    /*    cout<<"L222 index="<<index<<endl;*/
    bn40* tmp = mod(m, c);
    /*    cout<<"L224 index="<<index<<endl;*/
    ar[index] = tmp;
    delete m;
  }
  /*  cout<<"L254"<<endl;*/
  bn40* r = new bn40(1);
  r->addat(0,1);
  for(size_t index = 0; index < bbits; index++){
    size_t v_1 = 1;
    size_t o = index / 0x40;
    size_t i = index % 0x40;
    size_t v = v_1 << i;
    if((b->_ele[o] & v) != 0){
      bn40* tmp = mul(r, ar[index]);
      delete r;
      r = mod(tmp, c);
      delete tmp;
    }
  }
  for(size_t index = 0; index < bbits; index++){
    delete ar[index];
  }
  return r;
}

bn40* mersenne(size_t n){
  size_t len = n/64 + 1;
  size_t pos = n%64;
  bn40* r = new bn40(len);
  size_t v_1 = 1;
  v_1 <<= pos;
  r->addat(len - 1, v_1);
  r->subat(0, 1);
  return r;
}

string* bn40::tohex(){
  size_t  chars = (this->_len) << 4;
  size_t f = 0xf;
  string* str = new string();
  for(size_t i = 0 ; i < chars; i++){
    int o_index = i / 0x10;
    int i_index = i % 0x10;
    size_t v = *(this->_ele + o_index);
    size_t a = (v >> (i_index*4))& f;
    char tc;
    if(a <= 9){
      tc = '0' + a;
    }else {
      tc = 'a' + a - 10;
    }
    *str += tc;
  }
  return str;
}

bn40* fromhex(string* str){
  size_t len = str->length();
  size_t length = len >> 4;
  if((len % 0x10) !=0){
    length++;
  }
  bn40* r = new bn40(length);
  
  for(size_t i = 0 ; i < len ; i++){
    size_t o_index = i / 0x10;
    size_t i_index = i % 0x10;
    
    char c = *(str->c_str() + i);
    size_t v;
    if((c >='0') && (c<='9')){
      v = c - '0';
    }
    if((c >= 'a') && (c <= 'f')){
      v = c - 'a' + 0xa;
    }
    v <<= (i_index * 4);
    r->addat(o_index, v);
  }
  return r;
}

void bn40::print(){
  this->shrink();
  string* s = this->tohex();
  cout<<"^^"<< *s <<"$$"<<endl;
  delete s;
}
