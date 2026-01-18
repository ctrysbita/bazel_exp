#!/usr/bin/env python3
"""
分析动态库 (.dylib / .so) 的大小分布，支持 macOS 和 Linux
"""

import platform
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {cmd}")
        print(f"错误: {e.stderr}")
        return ""


def parse_hex_size(hex_str):
    """将十六进制字符串转换为整数"""
    try:
        return int(hex_str, 16)
    except ValueError:
        return 0


def get_platform():
    """获取操作系统类型"""
    return platform.system()


def analyze_macos(dylib_path):
    """分析 macOS 动态库的大小分布"""
    print("=" * 60)
    print(f"动态库大小分析: {Path(dylib_path).name}")
    print("=" * 60)
    print()

    # 1. 文件总大小
    print("1. 文件总大小:")
    size_output = run_command(f"ls -lh '{dylib_path}'")
    print(f"   {size_output.strip()}")
    print()

    # 2. 各段大小
    print("2. 各段大小:")
    size_output = run_command(f"size '{dylib_path}'")
    print(f"   {size_output.strip()}")
    print()

    # 3. 各节详细信息
    print("3. 各节详细信息:")
    print("   节名称              大小 (字节)  十六进制")
    print("   " + "-" * 50)

    otool_output = run_command(f"otool -l '{dylib_path}'")
    sections = []
    lines = otool_output.split("\n")

    current_sectname = None
    for line in lines:
        if "sectname" in line:
            current_sectname = line.split()[1]
        elif "size" in line and current_sectname and "0x" in line:
            size_hex = line.split()[1]
            size_bytes = parse_hex_size(size_hex)
            sections.append((current_sectname, size_bytes, size_hex))
            print(f"   {current_sectname:<20} {size_bytes:>12}  0x{size_hex}")
            current_sectname = None

    print()

    # 4. 符号表信息
    print("4. 符号表信息:")
    symtab_info = run_command(f"otool -l '{dylib_path}' | grep -A 10 'LC_SYMTAB'")
    for line in symtab_info.split("\n"):
        if any(x in line for x in ["symoff", "nsyms", "stroff", "strsize"]):
            print(f"   {line.strip()}")
    print()

    # 5. 动态符号表信息
    print("5. 动态符号表信息:")
    dysymtab_info = run_command(f"otool -l '{dylib_path}' | grep -A 20 'LC_DYSYMTAB'")
    for line in dysymtab_info.split("\n"):
        if any(
            x in line for x in ["nlocalsym", "nextdefsym", "nundefsym", "nindirectsyms"]
        ):
            print(f"   {line.strip()}")
    print()

    # 6. 代码签名信息
    print("6. 代码签名信息:")
    sig_info = run_command(f"otool -l '{dylib_path}' | grep -A 4 'LC_CODE_SIGNATURE'")
    for line in sig_info.split("\n"):
        if any(x in line for x in ["dataoff", "datasize"]):
            print(f"   {line.strip()}")
    print()

    # 7. 依赖的动态库
    print("7. 依赖的动态库:")
    deps = run_command(f"otool -L '{dylib_path}'")
    for line in deps.split("\n")[1:]:  # 跳过第一行（文件名）
        if line.strip():
            print(f"   {line.strip()}")
    print()

    # 8. 导出的符号
    print("8. 导出的符号:")
    exports = run_command(f"nm -g '{dylib_path}' | grep ' T '")
    for line in exports.split("\n"):
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                print(f"   {parts[2]}")
    print()

    # 9. 未定义的符号（需要从其他库导入）
    print("9. 未定义的符号 (需要从其他库导入) - 前10个:")
    undefs = run_command(
        f"nm -u '{dylib_path}' | awk '{{print $3}}' | sort -u | head -10"
    )
    for line in undefs.split("\n"):
        if line.strip():
            print(f"   {line.strip()}")
    print("   ...")
    print()

    # 10. 总结
    print("10. 大小总结:")
    total_code = sum(s[1] for s in sections if s[0] in ["__text", "__stubs"])
    total_data = sum(s[1] for s in sections if s[0] in ["__got", "__data"])
    total_strings = sum(s[1] for s in sections if s[0] == "__cstring")
    total_except = sum(s[1] for s in sections if s[0] == "__gcc_except_tab")
    total_unwind = sum(s[1] for s in sections if s[0] == "__unwind_info")

    print(f"   代码段 (__text + __stubs):     {total_code:>8} 字节")
    print(f"   数据段 (__got):                {total_data:>8} 字节")
    print(f"   字符串常量 (__cstring):       {total_strings:>8} 字节")
    print(f"   异常表 (__gcc_except_tab):     {total_except:>8} 字节")
    print(f"   展开信息 (__unwind_info):     {total_unwind:>8} 字节")
    print(
        f"   其他节:                        {sum(s[1] for s in sections) - total_code - total_data - total_strings - total_except - total_unwind:>8} 字节"
    )
    print()

    # 计算实际使用空间 vs 分配空间
    print("11. 空间使用分析:")
    file_size = Path(dylib_path).stat().st_size
    print(
        f"   文件总大小:                    {file_size} 字节 ({file_size/1024:.0f} KB)"
    )
    print(f"   实际使用空间:                  {sum(s[1] for s in sections):>8} 字节")
    if sum(s[1] for s in sections) > 0:
        print(
            f"   空间利用率:                    {sum(s[1] for s in sections) / file_size * 100:.1f}%"
        )
    print()
    print("   注意: macOS 动态库的段按页对齐（每页 16KB），")
    print("   因此即使实际代码很小，也会占用完整的页空间。")


def analyze_linux(so_path):
    """分析 Linux 共享库的大小分布"""
    print("=" * 60)
    print(f"共享库大小分析: {Path(so_path).name}")
    print("=" * 60)
    print()

    # 1. 文件总大小
    print("1. 文件总大小:")
    size_output = run_command(f"ls -lh '{so_path}'")
    print(f"   {size_output.strip()}")
    file_size = Path(so_path).stat().st_size
    print()

    # 2. 各段大小
    print("2. 各段大小 (readelf -l):")
    segments_output = run_command(
        f"readelf -l '{so_path}' 2>/dev/null | grep LOAD | head -5"
    )
    if segments_output.strip():
        print(segments_output)
    print()

    # 3. 各节详细信息
    print("3. 各节详细信息:")
    print("   节名称              大小 (字节)")
    print("   " + "-" * 50)

    # 获取所有节信息，跳过表头
    sections_output = run_command(
        f"readelf --wide -S '{so_path}' 2>/dev/null | awk '/Name.*Type/{{flag=1; next}} flag && /^\\s+\\[/{{print}}'"
    )
    sections = []

    for line in sections_output.split("\n"):
        if line.strip() and line.startswith("  ["):
            # 解析：  [号] 名称 类型 地址 偏移 大小 ...
            parts = line.split()
            if len(parts) >= 6:
                sect_name = parts[1]  # 名称在第二列
                if sect_name and sect_name != "NULL":
                    try:
                        # Size is at index 5 (6th column)
                        sect_size = int(parts[5], 16)
                        # 只添加有实际名称的节（以.开头或是NULL）
                        if sect_name.startswith("."):
                            sections.append((sect_name, sect_size))
                            print(f"   {sect_name:<20} {sect_size:>12}")
                    except (ValueError, IndexError):
                        pass

    print()

    # 4. 符号表信息
    print("4. 符号表信息:")
    symtab_count = run_command(
        f"readelf -s '{so_path}' 2>/dev/null | grep -c '^[ ]*[0-9]'"
    )
    try:
        print(f"   符号总数: {int(symtab_count.strip())}")
    except:
        print(f"   符号总数: 未知")
    print()

    # 5. 依赖的动态库
    print("5. 依赖的动态库:")
    deps_readelf = run_command(f"readelf -d '{so_path}' 2>/dev/null | grep 'NEEDED'")
    if deps_readelf.strip():
        for line in deps_readelf.split("\n"):
            if "NEEDED" in line:
                # 提取库名 (格式: 0x.........  (NEEDED)             Shared library: [libc.so.6])
                if "[" in line and "]" in line:
                    lib_name = line[line.find("[") + 1 : line.find("]")]
                    print(f"   {lib_name}")
    print()

    # 6. 导出的符号
    print("6. 导出的符号 (全局符号) - 前20个:")
    exports = run_command(f"nm '{so_path}' 2>/dev/null | grep ' T '")
    count = 0
    if exports.strip():
        for line in exports.split("\n"):
            if line.strip() and count < 20:
                parts = line.split()
                if len(parts) >= 3:
                    print(f"   {parts[2]}")
                    count += 1
        all_exports = len([l for l in exports.split("\n") if l.strip()])
        if all_exports > 20:
            print(f"   ... 还有 {all_exports - 20} 个符号")
    else:
        print("   (没有全局符号)")
    print()

    # 7. 未定义的符号
    print("7. 未定义的符号 (需要从其他库导入) - 前20个:")
    undefs = run_command(f"nm -u '{so_path}' 2>/dev/null")
    count = 0
    for line in undefs.split("\n"):
        if line.strip() and count < 20:
            parts = line.split()
            if len(parts) >= 1:
                # nm -u 格式: "                 U symbol_name"
                print(f"   {parts[-1]}")
                count += 1
    all_undefs = len([l for l in undefs.split("\n") if l.strip()])
    if all_undefs > 20:
        print(f"   ... 还有 {all_undefs - 20} 个符号")
    print()

    # 8. 总结
    print("8. 大小总结:")
    code_sections = sum(
        s[1]
        for s in sections
        if s[0] in [".text", ".init", ".fini", ".plt", ".init_array", ".fini_array"]
    )
    data_sections = sum(
        s[1] for s in sections if s[0] in [".data", ".got", ".got.plt", ".data.rel.ro"]
    )
    rodata_sections = sum(s[1] for s in sections if s[0] in [".rodata", ".rodata1"])
    bss_sections = sum(s[1] for s in sections if s[0] == ".bss")
    exception_sections = sum(s[1] for s in sections if ".eh_frame" in s[0])
    dynsym_sections = sum(
        s[1]
        for s in sections
        if s[0]
        in [".dynsym", ".dynstr", ".rel.dyn", ".rel.plt", ".rela.dyn", ".rela.plt"]
    )

    print(f"   代码段 (.text):               {code_sections:>8} 字节")
    print(f"   数据段 (.data/.got):          {data_sections:>8} 字节")
    print(f"   只读数据 (.rodata):           {rodata_sections:>8} 字节")
    print(f"   未初始化数据 (.bss):         {bss_sections:>8} 字节")
    print(f"   异常处理表 (.eh_frame):       {exception_sections:>8} 字节")
    print(f"   动态符号表:                   {dynsym_sections:>8} 字节")
    total_named = (
        code_sections
        + data_sections
        + rodata_sections
        + bss_sections
        + exception_sections
        + dynsym_sections
    )
    other = sum(s[1] for s in sections) - total_named
    print(f"   其他节:                       {other:>8} 字节")
    print()

    # 9. 空间使用分析
    print("9. 空间使用分析:")
    print(
        f"   文件总大小:                    {file_size} 字节 ({file_size/1024:.0f} KB)"
    )
    total_sections = sum(s[1] for s in sections)
    print(f"   所有节总大小:                  {total_sections:>8} 字节")
    if total_sections > 0 and file_size > 0:
        print(
            f"   空间利用率:                    {total_sections / file_size * 100:.1f}%"
        )
    print()
    print("   注意: Linux 共享库的节大小为实际占用大小。")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 analyze_dylib.py <library_path>")
        print()
        print("示例:")
        print(
            "  python3 analyze_dylib.py bazel-bin/hello/libhello_shared.dylib  # macOS"
        )
        print(
            "  python3 analyze_dylib.py bazel-bin/cchello/libcchello_bin.so    # Linux"
        )
        sys.exit(1)

    lib_path = sys.argv[1]

    if not Path(lib_path).exists():
        print(f"错误: 文件不存在: {lib_path}")
        sys.exit(1)

    # 自动检测操作系统并调用相应的分析函数
    os_type = get_platform()
    if os_type == "Darwin":
        analyze_macos(lib_path)
    elif os_type == "Linux":
        analyze_linux(lib_path)
    else:
        print(f"错误: 不支持的操作系统: {os_type}")
        print("仅支持 macOS (Darwin) 和 Linux")
        sys.exit(1)


if __name__ == "__main__":
    main()
