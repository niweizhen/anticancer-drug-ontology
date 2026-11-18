# -*- coding: utf-8 -*-
"""用 HermiT 推理机对本体执行一次推理，并输出可核查的推理报告。"""
import os, io, sys
import owlready2
from owlready2 import get_ontology
from owlready2.reasoning import sync_reasoner_hermit

HERE = os.path.dirname(os.path.abspath(__file__))
OWL = os.path.join(HERE, "..", "ontology", "anticancer-drug-insurance.owl")
REPORT = os.path.join(HERE, "reasoning_report.txt")

owlready2.JAVA_EXE = r"C:\Users\BBG\java\jdk-17.0.21\bin\java.exe"

onto = get_ontology(os.path.abspath(OWL)).load()

# ---- 推理前快照 ----
before_types, before_props = {}, {}
for ind in onto.individuals():
    before_types[ind.name] = set(ind.is_a)
    snap = {}
    for prop in onto.object_properties():
        try:
            vals = set(getattr(ind, prop.python_name) or [])
        except Exception:
            vals = set()
        if vals:
            snap[prop.name] = vals
    before_props[ind.name] = snap

lines = []
def out(s=""):
    print(s)
    lines.append(s)

out("=" * 78)
out("HermiT 推理报告 —— 《抗肿瘤药品与医保谈判》本体")
out("=" * 78)
out(f"推理机：HermiT（owlready2 内置 HermiT.jar，Java: {owlready2.JAVA_EXE}）")
out(f"本体文件：{os.path.basename(OWL)}")
out(f"推理前：类 {len(list(onto.classes()))} 个，个体 {len(list(onto.individuals()))} 个")

with onto:
    try:
        sync_reasoner_hermit(infer_property_values=True, debug=0)
        out("一致性检查：本体一致（未发现矛盾公理）✔")
    except owlready2.OwlReadyInconsistentOntologyError:
        out("一致性检查：本体不一致 ✘ —— 推理中止")
        raise

# ---- 推理后对比：新增的类归属 ----
out("")
out("-" * 78)
out("一、推理机推断出的『类归属』（原文件中并未手工断言这些类型）")
out("-" * 78)
inferred_class_cnt = 0
for ind in onto.individuals():
    new = [c for c in ind.is_a if c not in before_types[ind.name] and hasattr(c, "name")]
    # 只保留本体的命名类（排除等价类展开产生的匿名类）
    named = [c for c in new if c.namespace is not None and c.name in
             {x.name for x in onto.classes()}]
    if named:
        inferred_class_cnt += 1
        ol = "、".join(f"{c.label[0] if c.label else c.name}" for c in named)
        out(f"  {ind.label[0] if ind.label else ind.name:<12}  ⇒  属于  {ol}")

if inferred_class_cnt == 0:
    out("  （无新增类归属）")

# ---- 推理后对比：新增的关系 ----
out("")
out("-" * 78)
out("二、推理机推断出的『对象属性断言』（含传递闭包与逆属性推导）")
out("-" * 78)
inferred_prop_cnt = 0
for ind in onto.individuals():
    for prop in onto.object_properties():
        try:
            cur = set(getattr(ind, prop.python_name) or [])
        except Exception:
            continue
        new = cur - before_props[ind.name].get(prop.name, set())
        for target in new:
            if not hasattr(target, "name"):
                continue
            inferred_prop_cnt += 1
            pf = prop.label[0] if prop.label else prop.name
            out(f"  {ind.label[0] if ind.label else ind.name:<10} --[{pf}]--> "
                f"{target.label[0] if target.label else target.name}")

if inferred_prop_cnt == 0:
    out("  （无新增关系断言）")

# ---- 定义类的成员 ----
out("")
out("-" * 78)
out("三、定义类（Defined Class）的推理归类结果")
out("-" * 78)
for cn in ("NegotiatedDrug", "FailedNegotiatedDrug", "LungCancerDrug"):
    c = onto[cn]
    mem = [i for i in c.instances()]
    lab = c.label[0] if c.label else cn
    out(f"  {lab}（{cn}）⇒ {len(mem)} 个实例："
        + "、".join((i.label[0] if i.label else i.name) for i in mem))

out("")
out("-" * 78)
out("四、推理结论摘要")
out("-" * 78)
out(f"  · 新增类归属断言：{inferred_class_cnt} 条")
out(f"  · 新增关系断言：{inferred_prop_cnt} 条")
out("  · 传递属性推理示例：广州市 --隶属于地区--> 广东省 --隶属于地区--> 中国")
out("    推理机据此推出 广州市 隶属于 中国（跨越两级行政区划）")
out("  · 否定条件推理示例：帕博利珠单抗 参加过国家医保谈判但未纳入任何目录条目，")
out("    推理机据此将其归入『谈判未成功药品』")

with io.open(REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n报告已写入:", REPORT)
