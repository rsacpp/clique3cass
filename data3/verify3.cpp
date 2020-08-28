#include "bn40.h"
#include <boost/algorithm/hex.hpp>

int
main(int argc, char* argv[]){
  if(argc < 2){
    cout << "usage: ./verify3 {XXXX@@XXXX}" << endl;
    return 0;
  }
  string* input = new string(argv[1]);
  int pos = input->find("@@");
  if(pos < 0){
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
  string code = boost::algorithm::unhex(*rr);
  cout<<code<<endl;
  delete rr;
  delete r;
  delete _v;
  delete _e;
  delete _pq;
  delete v;
  delete pq;
  delete input;
  return 0;
}
