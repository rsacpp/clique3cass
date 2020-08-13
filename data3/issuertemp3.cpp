/**
* issuertemp.cpp for Clique3
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
#include <cstdlib>
#include <cstring>
#include <boost/asio.hpp>
#include <boost/format.hpp>
#include <boost/algorithm/hex.hpp>
#include <boost/algorithm/string/case_conv.hpp>

string* digest(string* input){
  using namespace std;
  /* string* input = new string(argv[1]); */
  string* symbol = new string("SYMBOL");
  string* alias = new string("ALIAS");
  
  if((input->find("5e5e") !=0 )||(input->rfind("2424") + 4 != input->length())){
    delete input;
    delete symbol;
    delete alias;
    cout<<"format error"<<endl;
    return NULL;
  }
  //manipulate the input
  input->insert(4, *symbol);
  input->insert(input->length() - 4 , *alias);

  string* key = new string("KEY");
  int pos = key->find("@@");
  string* pq = new string(key->substr(0,pos));
  string* id = new string(key->substr(pos + 2));
  bn40* _cre = fromhex(id);

  bn40* _val = fromhex(input);
  bn40* _pq = fromhex(pq);
  bn40* r = npmod(_val,_cre,_pq);
  /* cout<<*pq<<"@@";*/
  string* r2 = r->tohex();
  /* cout<< *r2<<endl; */
  delete r2;
  delete _pq;
  delete r;
  delete _val;
  delete pq;
  delete _cre;
  delete input;
  delete id;
  delete key;
  delete symbol;
  delete alias;

  string* rr = new string(*pq + "@@" + *r2);
  return rr;
}

int
main(int argc, char* argv[]){
    try{
    boost::asio::io_service io_service;
    tcp::resolver resolver(io_service);
    tcp::resolver::query query(tcp::v4(), argv[1], "21822");
    tcp::resolver::iterator iterator = resolver.resolve(query);
    tcp::socket s(io_service);
    boost::asio::connect(s, iterator);
    
    using namespace std;

    string* key = new string("KEY");
    int pos = key->find("@@");
    string* pq = new string(key->substr(0,pos));
    string* id = new string(key->substr(pos + 2));
    bn40* _cre = fromhex(id);
    string req = string(*pq + '||' + argv[1]);
    size_t req_length = req.length();
    string size_string = str(boost::format("%08d") % req_length);
    boost::asio::write(s, boost::asio::buffer(size_string.c_str(), 8));
    boost::asio::write(s, boost::asio::buffer(req.c_str(), req_length));
    // get the note id from remote;
    char reply_size[8];
    boost::asio::read(s, boost::asio::buffer(reply_size, 8));
    /*char request[] = "sslfdakdslflslldfs";
      size_t request_length = strlen(request);*/
    boost::asio::read(s, boost::asio::buffer(req.c_str(), req_length));
    
    delete _cre;
    delete id;
    delete pq;
    delete key;
  }catch (std::exception& e){
    std::cerr << "Exception: " << e.what() << "\n";
  }
    
  
}
