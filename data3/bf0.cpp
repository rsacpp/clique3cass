#include <cstdlib>
#include <cstring>
#include <boost/asio.hpp>
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/hex.hpp>
#include <boost/algorithm/string/case_conv.hpp>

int main(int argc, char* argv[]){
  try{
    using boost::asio::ip::tcp;
    boost::asio::io_service io_service;
    tcp::resolver resolver(io_service);
    tcp::resolver::query query(tcp::v4(), "localhost", "12345");
    tcp::resolver::iterator iterator = resolver.resolve(query);
    tcp::socket s(io_service);
    boost::asio::connect(s, iterator);

    using namespace std;
    string* pq = new string("b1d851ac07e704a8339581c851521cd23b2f19122208e0d845f18041d6f146981878f05f6c8cba8339a545d1552c32bebbb7b47a2ae8b7143c41e6dd725b382e90525e1901ec7fc856b9cb975d43d93c87e513b434e3a508783751aaaa4f5b8495c71ba9f3f7995a4c06ec0a13ccc6e265f765027866d437d5a2e48c86259ede176d9c21376c73b1db7dc3346525aaf95e8d4ca8a8689f47cd41ba277ac71628dfa0341071f940a30c97281581cded22089e2435e4140cb85fc3cdd3a3be260061d009d7878a29ea3f69923c3c1f8d03080e21de19764efe375d250ddb1cb643dd0dea1965e0e0d7b35c00289e70ec881f584adbcb2b2b30734591dc85eb949b");
    string* quantity = new string("2");
    string* req = new string(*pq + "||" + *quantity);
    string size0 = boost::str(boost::format("%08d") % req->length());
    boost::asio::write(s, boost::asio::buffer(size0.c_str(), 8));
    boost::asio::write(s, boost::asio::buffer(req->c_str(), req->length()));

    char size1buff[8];
    boost::asio::read(s, boost::asio::buffer(size1buff, 8));
    /* copy from char[] to string */
    string size1 = string(size1buff, size1buff + 8);
    size_t thesize1 = boost::lexical_cast<size_t>(size1);
    char note_id[thesize1];
    boost::asio::read(s, boost::asio::buffer(note_id, thesize1));
    string noteId = string(note_id, note_id + thesize1);
    std::cout<< noteId <<std::endl;
    
    string* laststep = new string("13023942jsldfkslafjsldfksdfiwowodkflslsls");
    string size2 = boost::str(boost::format("%08d") % laststep->length());
    boost::asio::write(s, boost::asio::buffer(size2.c_str(), 8));
    boost::asio::write(s, boost::asio::buffer(laststep->c_str(), laststep->length()));
    delete laststep;
    delete req;
    delete pq;
    delete quantity;
  }catch (std::exception& e){
      std::cerr << "Exception: " << e.what() << "\n";
  }
  return 0;
}
