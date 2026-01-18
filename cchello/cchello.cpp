#include "cchello.hpp"

#include <iostream>

#include "cchello/l1/l1.hpp"

namespace cc {

void hello(std::string name) {
  std::cout << "Hello, World! " << name << std::endl;
  hello_from_l1_exported_and_called(name);
  hello_from_l1_not_exported_but_called(name);
}

}  // namespace cc