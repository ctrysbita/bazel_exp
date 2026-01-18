#include "cchello/l1/l1.hpp"

#include <iostream>

#include "cchello/l1/l2/l2.hpp"

namespace cc {

namespace {

void hello_from_l1_impl(std::string name) {
  hello_from_l2_exported_and_called(name);
  hello_from_l2_not_exported_but_called(name);
  std::cout << "Hello " << name << " from L1!";
}

}  // namespace

void hello_from_l1_exported_and_called(std::string name) {
  hello_from_l1_impl(name);
  std::cout << " exported_and_called" << std::endl;
}

void hello_from_l1_exported_not_called(std::string name) {
  hello_from_l1_impl(name);
  std::cout << " exported_not_called" << std::endl;
}

void hello_from_l1_not_exported_but_called(std::string name) {
  hello_from_l1_impl(name);
  std::cout << " not_exported_but_called" << std::endl;
}

void hello_from_l1_not_exported_not_called(std::string name) {
  hello_from_l1_impl(name);
  std::cout << " not_exported_not_called" << std::endl;
}

}  // namespace cc