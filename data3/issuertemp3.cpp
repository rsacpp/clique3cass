#include "bn40.h"
#include <cstdlib>
#include <cstring>
#include <boost/asio.hpp>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/hex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/case_conv.hpp>

string rtrim0(string a){
  if(a.empty()){
    return a;
  }
  int index = a.length() - 1;
  while(a.at(index) == '0'){
    index--;
    if(index <= 0){
      index = -1;
      break;
    }
  }
  /*  cout<<index<<endl; */
  return a.substr(0, index+1);
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
  delete r;
  delete _pq;
  delete _val;
  delete _cre;
  delete id;
  delete pq;
  delete key;
  delete input;
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
      string* note_hex = new string(notebuff, notebuff + thesize1);
      string* pq01 = new string("d3d19b266dcc7393b544f5d4cb582d3cf44d4a4d3a4254ad875d5d253e43fa97293f8c133c9ac8242abf73a42cbad81abccfa36f4042d93a252313070d6ea4db6fe1bba792aa9e17c486bac695a9dbbf883d6a2ce287213db015970a366f9eefd940b0ce13263624876dc9c7c2015e2b8d1829568bb60d4be2d591d81a1ee70f");
      string* e01 = new string("989c091c6c210412a12dbecb068de36f");
      /*
	string d01 = string("97abccdfb45a4829aafa4be61ebb13c55a7b1a994111a3513906c9d47a8dcc1267aa81915f8b123bfc6d8a3c77117ae3a14c466abaf8ac0616dbc533e125b314cb7b0232563eadbe3b29293a051ce4cd21181cadb96e02fa2b4c63cdd47f0f158ff016c14b3f176e996eab78eaaeeb728a4758a243f90b0a118f1bccef1ffe7a");
       */
      bn40* _note_hex = fromhex(note_hex);
      bn40* _pq01 = fromhex(pq01);
      bn40* _e01 = fromhex(e01);
      bn40* _r01 = npmod(_note_hex, _e01, _pq01);
      string* rr01 = _r01->tohex();
      string code01 = rtrim0(*rr01);
      string raw_noteId = string(boost::algorithm::unhex(code01));
      std::cout<<"raw noteId:"<<raw_noteId<<std::endl;
      delete rr01;
      delete _r01;
      delete _e01;
      delete _pq01;
      delete _note_hex;
      delete e01;
      delete pq01;
      delete note_hex;
      if(raw_noteId.rfind("^^SYMBOL", 0) != 0){
	cout<<"symbol conflicts"<<endl;
      }else{
	string noteId = raw_noteId.substr(2, raw_noteId.length() - 4);
	string raw = string("^^"+noteId +"->ALIAS$$");
	string* code = new string(boost::algorithm::hex(raw));
	boost::algorithm::to_lower(*code);
	string* output = digest(code);
	string size2 = boost::str(boost::format("%08d") % output->length());
	boost::asio::write(s, boost::asio::buffer(size2.c_str(), 8));
	boost::asio::write(s, boost::asio::buffer(output->c_str(), output->length()));
	delete output;
      }
      delete pq;
      delete key;
    }catch (std::exception& e){
      std::cerr << "Exception: " << e.what() << "\n";
    }
}
