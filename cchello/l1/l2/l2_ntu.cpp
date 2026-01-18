#include <iostream>

#include "cchello/l1/l2/l2.hpp"

namespace cc {

void hello_from_l2_ntu_exported_not_called(std::string name) {
  std::cout << "Hello " << name << " from L2 NTU exported not called!"
            << std::endl;
}

void hello_from_l2_ntu_not_exported_not_called(std::string name) {
  std::cout << "Hello " << name << " from L2 NTU not exported not called!"
            << std::endl;
}

}  // namespace cc