#include "bn40.h"
#include <boost/asio.hpp>
#include <boost/format.hpp>
#include <boost/algorithm/hex.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/algorithm/string/case_conv.hpp>

int
main(int argc, char* argv[]){
  try{
    using boost::asio::ip::tcp;
    boost::asio::io_service io_service;
    tcp::resolver resolver(io_service);
    tcp::resolver::query query(tcp::v4(), argv[1], "21821");
    tcp::resolver::iterator iterator = resolver.resolve(query);
    tcp::socket s(io_service);
    boost::asio::connect(s, iterator);

    using namespace std;
    string* input = new string(boost::algorithm::hex(string(argv[2])));
    boost::algorithm::to_lower(*input);

    if((input->find("5e5e") !=0 )||(input->rfind("2424") + 4 != input->length())){
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
    string* r2 = r->tohex();
    string* output = new string(*pq +"@@"+ *r2);
    cout<<"proposal:"<<*output<<endl;
    string size0 = boost::str(boost::format("%08d") % output->length());
    boost::asio::write(s, boost::asio::buffer(size0.c_str(), 8));
    boost::asio::write(s, boost::asio::buffer(output->c_str(), output->length()));
    delete output;
    delete r2;
    delete r;
    delete _pq;
    delete _val;
    delete _cre;
    delete id;
    delete pq;
    delete key;
    delete input;
    return 0;
  }catch (std::exception& e){
    std::cerr << "Exception: " << e.what() << "\n";
  }
  return 0;  
}
