# -*- coding: utf-8 -*-
"""执行全部 Cypher 查询，保存真实结果（供查询文档引用），并生成 queries.cypher。"""
import subprocess, os, sys, json, csv, io, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = r"D:\neo4j\neo4j-community-5.26.33\bin"
JAVA_HOME = r"C:\Users\BBG\java\jdk-17.0.21"
PWD = "Neo4j@2026"

spec = importlib.util.spec_from_file_location("n4j", os.path.join(HERE, "n4j.py"))
n4j = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n4j)

from queries_def import QUERIES   # (编号, 标题, 说明, Cypher)


def run_cypher(cypher: str) -> str:
    tmp = os.path.join(HERE, "_tmp_query.cypher")
    with io.open(tmp, "w", encoding="utf-8") as f:
        f.write(cypher.strip().rstrip(";") + ";\n")
    r = subprocess.run(
        [os.path.join(BIN, "cypher-shell.bat"),
         "-a", "bolt://localhost:7687", "-u", "neo4j", "-p", PWD,
         "--format", "plain", "-f", tmp],
        capture_output=True, env=n4j.clean_env(), cwd=BIN)
    os.remove(tmp)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    err = "\n".join(l for l in err.splitlines()
                    if l.strip() and "Picked up JAVA_TOOL_OPTIONS" not in l)
    if err.strip() and "warning" not in err.lower():
        out += "\n[ERR] " + err.strip()
    return out.strip()


def parse_plain(text: str):
    """把 cypher-shell plain 输出（首行为表头）解析成二维列表。"""
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return [], []
    rows = list(csv.reader(lines, quotechar='"', skipinitialspace=True))
    header, body = rows[0], rows[1:]
    return header, body


results = []
for qid, title, note, cypher in QUERIES:
    print(f"执行 {qid}: {title}", flush=True)
    raw = run_cypher(cypher)
    header, body = parse_plain(raw)
    results.append({"id": qid, "title": title, "note": note,
                    "cypher": cypher.strip(), "raw": raw,
                    "header": header, "rows": body})

with io.open(os.path.join(HERE, "query_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)

# 生成可提交的 queries.cypher（带中文批注）
lines = ["// ============================================================",
         "// 《抗肿瘤药品与医保谈判》知识图谱 —— 查询语句集",
         "// 连接：cypher-shell -a bolt://localhost:7687 -u neo4j -p Neo4j@2026",
         "// 对应查询结果见 docs/Neo4j查询文档.docx 与 results/query_results.json",
         "// ============================================================", ""]
for q in results:
    lines.append(f"// ---------- {q['id']} {q['title']} ----------")
    for ln in q["note"].split("\n"):
        lines.append("// " + ln)
    lines.append(q["cypher"].strip() + ";")
    lines.append("")

with io.open(os.path.join(HERE, "queries.cypher"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

# 生成纯文本结果，便于肉眼核查
with io.open(os.path.join(HERE, "..", "results", "query_results.txt"), "w",
             encoding="utf-8") as f:
    f.write("《抗肿瘤药品与医保谈判》知识图谱 —— 查询结果实录\n")
    f.write("Neo4j 5.26.33 / Cypher Shell 实测输出\n\n")
    for q in results:
        f.write("=" * 70 + "\n")
        f.write(f"{q['id']} {q['title']}\n")
        f.write("-" * 70 + "\n")
        f.write(q["cypher"] + "\n\n")
        f.write(q["raw"] + "\n\n")

print(f"\n完成 {len(results)} 条查询，结果已保存。")
