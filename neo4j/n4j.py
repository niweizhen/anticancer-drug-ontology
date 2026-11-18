# -*- coding: utf-8 -*-
"""在干净环境中调用 Neo4j 的 .bat 工具（规避 Git Bash 大小写重复环境变量导致的 PowerShell 崩溃）。

用法: python n4j.py <bat文件名> [参数...]
例:   python n4j.py cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p xxx "RETURN 1"
"""
import subprocess, os, sys

BIN = r"D:\neo4j\neo4j-community-5.26.33\bin"
JAVA_HOME = r"C:\Users\BBG\java\jdk-17.0.21"


def clean_env():
    env, seen = {}, set()
    for k, v in os.environ.items():
        ku = k.upper()
        if ku in seen:          # 同名不同大小写（PATH / Path）只保留首个
            continue
        seen.add(ku)
        env[k] = v
    if "Path" not in env and "PATH" in env:
        env["Path"] = env.pop("PATH")
    env["JAVA_HOME"] = JAVA_HOME
    env["Path"] = os.path.join(JAVA_HOME, "bin") + ";" + env.get("Path", "")
    # 强制 JVM 以 UTF-8 读写文件与标准输出，避免中文在 GBK 代码页下损坏
    env["JAVA_TOOL_OPTIONS"] = ("-Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 "
                                "-Dsun.stderr.encoding=UTF-8")
    return env


def decode(b):
    if not b:
        return ""
    if b.count(b"\x00") > len(b) // 4:      # 近似判断 UTF-16LE
        return b.decode("utf-16-le", "replace")
    try:
        return b.decode("utf-8")           # cypher-shell 输出为 UTF-8
    except UnicodeDecodeError:
        return b.decode("gbk", "replace")  # neo4j.bat / PowerShell 输出为 GBK


if __name__ == "__main__":
    tool, args = sys.argv[1], sys.argv[2:]
    r = subprocess.run([os.path.join(BIN, tool)] + args,
                       capture_output=True, env=clean_env(), cwd=BIN)
    # cypher-shell 已被强制输出 UTF-8；其余 .bat 走 GBK/UTF-16 探测
    if tool.lower().startswith("cypher-shell"):
        out = r.stdout.decode("utf-8", "replace")
        err = r.stderr.decode("utf-8", "replace")
    else:
        out = decode(r.stdout)
        err = decode(r.stderr)
    out = "\n".join(l for l in out.splitlines() if "Picked up JAVA_TOOL_OPTIONS" not in l)
    err = "\n".join(l for l in err.splitlines() if "Picked up JAVA_TOOL_OPTIONS" not in l)
    if out:
        print(out, end="")
    if err.strip():
        print(err, end="", file=sys.stderr)
    sys.exit(r.returncode)
