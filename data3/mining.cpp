#include "bn40.h"

int
main(int argc, char* argv[]){
  bn40* m15 = mersenne(1279);
  bn40* m14 = mersenne(607);
  string* sha512 = new string(argv[1]);
  bn40* _input = fromhex(sha512);
  string* rand = new string(argv[2]);
  bn40* _r = fromhex(rand);
  bn40* _rr = _r->leftpush(512);
  bn40* _finalr = add(_input, _rr);
  bn40* r0 = npmod(_finalr, m14, m15);
  r0->print();
  delete r0;
  delete _finalr;
  delete _rr;
  delete _r;
  delete rand;
  delete _input;  
  delete sha512;
  delete m14;
  delete m15;
  return 0;
}
