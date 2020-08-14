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
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/hex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/case_conv.hpp>

string* rtrim0(string* input){
  if(input->compare(string("0")) == 0){
    delete input;
    input = new string("");
    return input;
  }
  size_t size = input->length();
  string left = input->substr(0, size - 1);
  string right = input->substr(size -1 , 1);
  if(right.compare(string("0")) == 0){
    delete input;
    input = new string(left);
    return rtrim0(input);
  }else{
    return input;
  }
}


/*
 * g++ issuertemp3.cpp bn40.cpp -lboost_system -lpthread
 */
string* digest(string* input){
  using namespace std;

  if((input->find("5e5e") !=0 )||(input->rfind("2424") + 4 != input->length())){
    delete input;

    cout<<"format error"<<endl;
    return NULL;
  }

  string* key = new string("KEY");
  int pos = key->find("@@");
  string* pq = new string(key->substr(0,pos));
  string* id = new string(key->substr(pos + 2));
  bn40* _cre = fromhex(id);

  bn40* _val = fromhex(input);
  bn40* _pq = fromhex(pq);
  bn40* r = npmod(_val,_cre,_pq);

  string* r2 = r->tohex();


  delete r2;
  delete _pq;
  delete r;
  delete _val;
  delete pq;
  delete _cre;
  delete input;
  delete id;
  delete key;

  string* rr = new string(*pq + "@@" + *r2);
  return rr;
}


int
main(int argc, char* argv[]){
    try{
      using boost::asio::ip::tcp;
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
      /*
      string* id = new string(key->substr(pos + 2));
      bn40* _cre = fromhex(id);
      */
      string req = string(*pq + "||" + argv[1]);
      string size0 = boost::str(boost::format("%08d") % req.length());
      boost::asio::write(s, boost::asio::buffer(size0.c_str(), 8));
      boost::asio::write(s, boost::asio::buffer(req.c_str(), req.length()));
      // get the note id from remote;
      char size1buff[8];
      boost::asio::read(s, boost::asio::buffer(size1buff, 8));
      string size1 = string(size1buff, size1buff + 8);
      size_t thesize1 = boost::lexical_cast<size_t>(size1);
      char notebuff[thesize1];
      boost::asio::read(s, boost::asio::buffer(notebuff, thesize1));
      /* encrypted noteId, format: ^^PQ||SIG$$*/
      string noteId = string(notebuff, notebuff + thesize1);
      size_t pos0 = noteId.find("||");
      string pq0 = noteId.substr(2, pos0 - 2);
      string val0 = noteId.substr(pos0 + 2, noteId.length() - pos0 - 4);
      bn40* _pq = fromhex(pq0);
      bn40* _val = fromhex(val0);
      bn40* _e = new bn40(1);
      _e->addat(0, 0x10001);
      bn40* _res = npmod(_val, _e, _pq);
      string* rr = _res->tohex();
      rr = rtrim0(rr);
      //if noteId does not start with "SYMBOL", then exit;
      if(noteId.rfind("SYMBOL", 0) != 0){
	cout<<"symbol conflicts"<<endl;
      }else{
	string raw = string("^^"+noteId +"->ALIAS$$");
	string* code = new string(boost::algorithm::hex(raw));
	boost::algorithm::to_lower(*code);
	string* output = digest(code);
	string size2 = boost::str(boost::format("%08d") % output->length());
	boost::asio::write(s, boost::asio::buffer(size2.c_str(), 8));
	boost::asio::write(s, boost::asio::buffer(output->c_str(), output->length()));
	delete output;
      }
      delete rr;
      delete _res;
      delete _pq;
      delete _val;
      delete _e;
      delete pq;
      delete key;
    }catch (std::exception& e){
      std::cerr << "Exception: " << e.what() << "\n";
    }
}
