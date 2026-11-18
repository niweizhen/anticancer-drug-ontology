# -*- coding: utf-8 -*-
"""以子进程方式启动 Neo4j console（供本会话做建图与查询验证）。"""
import subprocess, winreg, os

def read_env(root, subkey):
    d = {}
    try:
        k = winreg.OpenKey(root, subkey)
    except OSError:
        return d
    i = 0
    while True:
        try:
            n, v, t = winreg.EnumValue(k, i)
        except OSError:
            break
        d[n] = v
        i += 1
    return d

sys_env = read_env(winreg.HKEY_LOCAL_MACHINE,
                   r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
user_env = read_env(winreg.HKEY_CURRENT_USER, r"Environment")
env = dict(os.environ)          # 以当前会话环境为基底（含 APPDATA、USERPROFILE 等登录变量）
env.update(sys_env)
env.update(user_env)
env["Path"] = os.path.expandvars(
    os.environ.get("Path", "") + ";" + sys_env.get("Path", "") + ";" + user_env.get("Path", "")
)

bin_dir = r"D:\neo4j\neo4j-community-5.26.33\bin"
print("启动 Neo4j console ...", flush=True)
subprocess.run([os.path.join(bin_dir, "neo4j.bat"), "console"], env=env, cwd=bin_dir)
