#pragma once

#include <string>

namespace cc {

__attribute__((visibility("default"))) __attribute__((used)) void
hello_from_l1_exported_and_called(std::string name);

__attribute__((visibility("default"))) __attribute__((used)) void
hello_from_l1_exported_not_called(std::string name);

void hello_from_l1_not_exported_but_called(std::string name);

void hello_from_l1_not_exported_not_called(std::string name);

}  // namespace cc