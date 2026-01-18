#pragma once

#include <string>

namespace cc {

__attribute__((visibility("default"))) __attribute__((used)) void
hello_from_l2_exported_and_called(std::string name);

__attribute__((visibility("default"))) __attribute__((used)) void
hello_from_l2_exported_not_called(std::string name);

void hello_from_l2_not_exported_but_called(std::string name);

void hello_from_l2_not_exported_not_called(std::string name);

__attribute__((visibility("default"))) __attribute__((used)) void
hello_from_l2_ntu_exported_not_called(std::string name);

void hello_from_l2_ntu_not_exported_not_called(std::string name);

}  // namespace cc