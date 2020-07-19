#include "bn40.h"

int
main(int argc, char* argv[]){
  string* spqr = new string("3c56f");
  bn40* pqr = fromhex(spqr);
  string* se = new string("7");
  bn40* e = fromhex(se);
  string* sd = new string("95");
  bn40* d = fromhex(sd);
  string* sf = new string("f881");
  bn40* f = fromhex(sf);
  string* sval = new string("b7");
  bn40* val = fromhex(sval);
  bn40* step1 = npmod(val, d, pqr);
  step1->print();
  bn40* step2 = npmod(step1, f, pqr);
  step2->print();
  bn40* step3 = npmod(step2, e, pqr);
  step3->print();
  delete step3;
  delete step2;
  delete step1;
  delete sval;
  delete sf;
  delete sd;
  delete se;
  delete spqr;
  delete val;
  delete f;
  delete d;
  delete e;
  delete pqr;
  return 0;
}
