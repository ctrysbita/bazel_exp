#pragma once

#include <string>

#define EXPORT __attribute__((visibility("default"))) __attribute__((used))

namespace cc {

EXPORT void hello(std::string name);

}
