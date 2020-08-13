#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>
#include <boost/asio.hpp>

using boost::asio::ip::tcp;

int main(int argc, char* argv[]){
  try{
    boost::asio::io_service io_service;
    tcp::resolver resolver(io_service);
    tcp::resolver::query query(tcp::v4(), argv[1], argv[2]);
    tcp::resolver::iterator iterator = resolver.resolve(query);

    tcp::socket s(io_service);
    boost::asio::connect(s, iterator);

    using namespace std;
    char request[] = "sslfdakdslflslldfs";
    size_t request_length = strlen(request);
    boost::asio::write(s, boost::asio::buffer(request, request_length));
  }catch (std::exception& e){
    std::cerr << "Exception: " << e.what() << "\n";
  }
  return 0;
}

// g++ -lboost_system -lpthread s0.cpp -o s0
// boost 1.53
