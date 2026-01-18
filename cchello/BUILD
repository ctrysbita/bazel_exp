cc_library(
    name = "l0",
    srcs = ["cchello.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "//cchello/l1",
        "//include",
    ],
)

cc_binary(
    name = "cchello_bin",
    srcs = ["cchello.cpp"],
    linkshared = True,
    visibility = ["//visibility:public"],
    deps = [
        "//cchello/l1",
        "//include",
    ],
)

cc_shared_library(
    name = "cchello_shared",
    visibility = ["//visibility:public"],
    deps = [
        ":l0",
    ],
)
