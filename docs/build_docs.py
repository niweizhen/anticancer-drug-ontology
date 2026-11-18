# -*- coding: utf-8 -*-
"""生成两份提交文档：
   1) 概念结构表.docx
   2) Neo4j查询文档.docx
表格内容直接读本体文件与真实查询结果，保证与 .owl / 数据库一致。
"""
import os, io, json
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from owlready2 import get_ontology

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OWL = os.path.join(ROOT, "ontology", "anticancer-drug-insurance.owl")
RESULTS = os.path.join(ROOT, "neo4j", "query_results.json")
REPORT = os.path.join(ROOT, "results", "reasoning_report.txt")
IMG = os.path.join(HERE, "concept_structure.png")

onto = get_ontology(os.path.abspath(OWL)).load()
DEFINED = {"NegotiatedDrug", "FailedNegotiatedDrug", "LungCancerDrug"}
XSD = {str: "xsd:string", float: "xsd:decimal", int: "xsd:integer", bool: "xsd:boolean"}

# ---------------------------------------------------------------- 样式工具
def set_run(run, size=10.5, bold=False, color=None, mono=False, ea="宋体"):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = "Consolas" if mono else "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas" if mono else ea)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)

def shade(cell_or_par, fill):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), fill)
    target = cell_or_par._tc.get_or_add_tcPr() if hasattr(cell_or_par, "_tc") else cell_or_par._p.get_or_add_pPr()
    target.append(el)

def new_doc():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    for attr in ("top_margin", "bottom_margin"):
        setattr(sec, attr, Cm(2.2))
    sec.left_margin = sec.right_margin = Cm(2.2)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    pf = st.paragraph_format
    pf.line_spacing = 1.35
    pf.space_after = Pt(4)
    for name, size, color in (("Heading 1", 15, "1F4E79"), ("Heading 2", 12, "2E75B6")):
        h = doc.styles[name]
        h.font.name = "Times New Roman"
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = RGBColor.from_string(color)
        h.element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        h.paragraph_format.space_before = Pt(14 if name == "Heading 1" else 10)
        h.paragraph_format.space_after = Pt(6)
    add_page_number(sec)
    return doc

def add_page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for instr in ("begin", "PAGE", "end"):
        if instr in ("begin", "end"):
            fld = OxmlElement("w:fldChar")
            fld.set(qn("w:fldCharType"), instr)
        else:
            fld = OxmlElement("w:instrText")
            fld.set(qn("xml:space"), "preserve")
            fld.text = " PAGE "
        run._r.append(fld)
    set_run(run, 9, color="808080")

def title(doc, main, sub):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run(main), 20, bold=True, color="1F4E79", ea="黑体")
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p2.add_run(sub), 10.5, color="595959")
    p2.paragraph_format.space_after = Pt(16)

def para(doc, text, size=10.5, bold=False, indent=True, space_after=4, color=None):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.space_after = Pt(space_after)
    set_run(p.add_run(text), size, bold=bold, color=color)
    return p

def code_block(doc, text, size=8.5):
    for line in text.split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.left_indent = Cm(0.5)
        shade(p, "F4F5F7")
        set_run(p.add_run(line if line else " "), size, mono=True, color="1F2937")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def table(doc, header, rows, widths=None, font=8.5, header_fill="DCE6F1", align_center_cols=()):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    hdr = t.rows[0]
    trPr = hdr._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)
    for i, h in enumerate(header):
        cell = hdr.cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(1)
        set_run(p.add_run(h), font, bold=True, color="1F3864")
        shade(cell, header_fill)
        if widths:
            cell.width = Cm(widths[i])
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            if i in align_center_cols:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_run(p.add_run(str(v)), font)
            if widths:
                cells[i].width = Cm(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

# ---------------------------------------------------------------- 本体结构抽取
def label(c):
    return c.label[0] if c.label else c.name

names = {c.name for c in onto.classes()}
all_classes = [c for c in onto.classes() if c.name not in DEFINED]

def parents_of(c):
    return [p for p in c.is_a if hasattr(p, "name") and getattr(p, "name", None) in names]

top = sorted([c for c in all_classes if not parents_of(c)], key=lambda x: label(x))

class_rows, class_map = [], {}

def walk(c, depth):
    class_rows.append([len(class_rows) + 1,
                       "　" * depth + c.name,
                       label(c),
                       label(parents_of(c)[0]) if parents_of(c) else "owl:Thing",
                       (c.comment[0] if c.comment else "")])
    class_map[c.name] = label(c)
    for s in sorted(c.subclasses(), key=lambda x: label(x)):
        if s.name not in DEFINED:
            walk(s, depth + 1)

for c in top:
    walk(c, 0)

# 对象属性
obj_rows = []
for p in sorted(onto.object_properties(), key=lambda x: x.name):
    if p.inverse_property and p.inverse_property.name < p.name:
        continue  # 逆属性成对出现，只列主方向
    traits = []
    if any(t.__name__ == "TransitiveProperty" for t in p.is_a):
        traits.append("传递属性")
    if any(t.__name__ == "SymmetricProperty" for t in p.is_a):
        traits.append("对称属性")
    if any(t.__name__ == "FunctionalProperty" for t in p.is_a):
        traits.append("函数属性")
    if any(t.__name__ == "InverseFunctionalProperty" for t in p.is_a):
        traits.append("逆函数属性")
    obj_rows.append([p.name, p.label[0] if p.label else "",
                     "、".join(class_map.get(d.name, d.name) for d in p.domain),
                     "、".join(class_map.get(r.name, r.name) for r in p.range),
                     "、".join(traits) if traits else "—",
                     p.inverse_property.name if p.inverse_property else "—",
                     p.comment[0] if p.comment else ""])

# 数据属性
data_rows = []
for p in sorted(onto.data_properties(), key=lambda x: x.name):
    func = any(t.__name__ == "FunctionalProperty" for t in p.is_a)
    data_rows.append([p.name, p.label[0] if p.label else "",
                      "、".join(class_map.get(d.name, d.name) for d in p.domain),
                      XSD.get(p.range[0], "xsd:string") if p.range else "—",
                      "1（函数属性）" if func else "多值",
                      p.comment[0] if p.comment else ""])

# 定义类
defined_rows = [
    ["NegotiatedDrug", "医保谈判成功药品",
     "药品 ⊓ ∃纳入目录.医保目录条目",
     "凡纳入医保目录的药品自动归入本类（推理出 4 个实例）"],
    ["FailedNegotiatedDrug", "谈判未成功药品",
     "药品 ⊓ ∃经谈判于.国家医保药品谈判 ⊓ ¬∃纳入目录.医保目录条目",
     "参加过国家谈判但未进目录的药品（推理出 1 个实例：帕博利珠单抗）"],
    ["LungCancerDrug", "肺癌治疗药品",
     "抗肿瘤药品 ⊓ ∃适用于.{非小细胞肺癌}",
     "适用于非小细胞肺癌的抗肿瘤药（推理出 4 个实例）"],
]

# 个体实例
ind_rows = []
group_titles = [("PharmaceuticalCompany", "制药企业"), ("RegulatoryAgency", "监管机构"),
                ("Drug", "药品"), ("Disease", "恶性肿瘤"), ("AdverseReaction", "不良反应"),
                ("NegotiationEvent", "医保谈判事件"), ("InsuranceListing", "医保目录条目"),
                ("PriceRecord", "价格记录"), ("Evidence", "证据"), ("Region", "地区")]
for cls_name, gname in group_titles:
    cls = onto[cls_name]
    for ind in sorted(cls.instances(), key=lambda i: (i.label[0] if i.label else i.name)):
        props = []
        for dp in sorted(onto.data_properties(), key=lambda x: x.name):
            try:
                v = getattr(ind, dp.python_name)
            except Exception:
                continue
            if v not in (None, [], ""):
                if isinstance(v, bool):
                    v = "是" if v else "否"
                props.append(f"{dp.label[0] if dp.label else dp.name}={v}")
        ind_rows.append([gname, ind.label[0] if ind.label else ind.name, ind.name,
                         "；".join(props[:5]) + ("…" if len(props) > 5 else "")])

# ---------------------------------------------------------------- 文档一
doc = new_doc()
title(doc, "《抗肿瘤药品与医保谈判》领域本体", "概念结构表 · Protégé 5.6 / OWL 2 DL")

doc.add_heading("一、本体基本信息", level=1)
table(doc, ["项目", "内容"], [
    ["本体名称", "抗肿瘤药品与医保谈判本体（Anticancer Drug & Medical Insurance Negotiation Ontology）"],
    ["本体 IRI", "http://www.semanticweb.org/bbi/ontologies/2026/11/anticancer-drug-insurance"],
    ["文件格式", "anticancer-drug-insurance.owl（RDF/XML，可直接用 Protégé 打开）"],
    ["规模", f"类 {len(all_classes)} 个（另有 {len(DEFINED)} 个定义类）；"
             f"对象属性 {len(list(onto.object_properties()))} 个（含逆属性）；"
             f"数据属性 {len(list(onto.data_properties()))} 个；个体 {len(list(onto.individuals()))} 个"],
    ["推理机", "HermiT（Protégé 内置；本次另用 HermiT 批处理校验，结论见第七节）"],
    ["一致性", "一致（无矛盾公理），全部类、属性、个体均带中文 rdfs:label 与 rdfs:comment"],
], widths=[3.2, 13.0], font=9)

doc.add_heading("二、类层次结构表", level=1)
para(doc, "下表按 Protégé 的类层次（SubClass Of）自顶向下缩进排列，共 25 个命名类。"
          "所有一级分支之间设置了互斥（owl:AllDisjointClasses），用于支撑一致性检查。")
table(doc, ["序号", "类名（英文标识）", "中文标签", "父类", "说明"],
      class_rows, widths=[1.2, 4.6, 3.0, 2.6, 5.0], font=8,
      align_center_cols=(0,))

doc.add_heading("三、对象属性（Object Property）", level=1)
para(doc, "对象属性刻画两个类之间的语义关系，表中同时给出定义域（Domain）、值域（Range）、"
          "属性特性与逆属性。共 14 组、27 条（含逆属性）。")
table(doc, ["属性名", "中文标签", "定义域", "值域", "特性", "逆属性", "说明"],
      obj_rows, widths=[3.0, 2.2, 2.6, 2.6, 1.8, 2.6, 3.4], font=7.5,
      align_center_cols=(1, 4))

doc.add_heading("四、数据属性（Data Property）", level=1)
para(doc, "数据属性描述个体的属性值。除“是否国产”外均设为函数属性（FunctionalProperty），"
          "即同一主体该属性最多一个取值。")
table(doc, ["属性名", "中文标签", "所属类", "数据类型", "基数", "说明"],
      data_rows, widths=[3.4, 2.4, 3.0, 2.4, 2.2, 3.6], font=7.5,
      align_center_cols=(1, 3, 4))

doc.add_heading("五、定义类（Defined Class，供推理机推断）", level=1)
para(doc, "定义类只写“必要条件 + 充分条件”的等价定义，不手工断言成员；"
          "推理机据此自动判定哪些个体属于该类，这是本体与普通分类表的本质区别。")
table(doc, ["定义类", "中文标签", "等价类定义（Manchester 语法）", "推理作用"],
      defined_rows, widths=[3.4, 2.4, 6.4, 4.4], font=8, align_center_cols=(1,))

doc.add_heading("六、个体实例一览", level=1)
para(doc, "实例层（ABox）共 38 个个体，覆盖药品、企业、疾病、谈判事件、目录条目、"
          "价格记录、证据与地区八类实体，均带关键数据属性。")
table(doc, ["所属类", "中文名称", "标识符", "关键属性（节选）"],
      ind_rows, widths=[2.4, 3.4, 3.6, 7.2], font=7.5, align_center_cols=(0,))

doc.add_heading("七、类层次结构图", level=1)
doc.add_picture(IMG, width=Cm(15.6))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
cap = doc.add_paragraph()
cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(cap.add_run("图 1  本体类层次结构（深蓝为一级类，逐层向右展开）"), 9, color="595959")

doc.add_heading("八、推理机运行结果", level=1)
para(doc, "使用 HermiT 对本体执行一次完整推理，一致性检查通过，并推断出以下新知识"
          "（这些三元组原文件中并未手工断言）：", indent=True)
rep = io.open(REPORT, encoding="utf-8").read() if os.path.exists(REPORT) else ""
sec_start = rep.find("一、推理机推断出的")
sec_end = rep.find("四、推理结论摘要")
excerpt = rep[sec_start:sec_end].strip() if sec_start > 0 else rep[:1500]
code_block(doc, excerpt, 7.8)
para(doc, "推理结论：①医保谈判成功药品 = 4 个（信迪利单抗、奥希替尼、曲妥珠单抗、贝伐珠单抗）；"
          "②谈判未成功药品 = 1 个（帕博利珠单抗）；③肺癌治疗药品 = 4 个；"
          "④由传递属性推出“广州市 隶属于地区 中国”，跨越两级行政区划。")

doc.save(os.path.join(HERE, "概念结构表.docx"))
print("已生成 概念结构表.docx")

# ---------------------------------------------------------------- 文档二
res = json.load(io.open(RESULTS, encoding="utf-8"))
doc = new_doc()
title(doc, "《抗肿瘤药品与医保谈判》知识图谱", "Neo4j 查询文档 · 含 Cypher 批注与实测结果")

doc.add_heading("一、环境与连接", level=1)
table(doc, ["项目", "内容"], [
    ["图数据库", "Neo4j 5.26.33 Community（Windows 版）"],
    ["访问地址", "bolt://localhost:7687（Browser: http://localhost:7474）"],
    ["账号 / 密码", "neo4j / Neo4j@2026"],
    ["命令行", "cypher-shell -a bolt://localhost:7687 -u neo4j -p Neo4j@2026"],
    ["图谱规模", "节点 38 个 / 关系 56 条，均由本体实例层一对一映射生成"],
], widths=[3.2, 13.0], font=9)

doc.add_heading("二、本体到图模型的映射规则", level=1)
para(doc, "本体的类、对象属性、数据属性分别映射为 Neo4j 的节点标签、关系类型与属性；"
          "关系上的语义补充信息（如治疗线、谈判结果、证据权重）作为关系属性存储，"
          "这是纯节点属性无法表达的。")
table(doc, ["本体元素", "图元素", "示例", "数量"], [
    ["类（Class）", "节点标签（Label）", ":Drug、:Company、:Negotiation", "10 类 → 38 节点"],
    ["对象属性（Object Property）", "关系类型（Relationship Type）", "INDICATED_FOR、LISTED_IN", "14 类 → 56 关系"],
    ["数据属性（Data Property）", "节点属性（Property）", "name、annualCost、cutRate", "23 个"],
    ["关系附加语义", "关系属性", "r.line='一线'、r.result='成功'", "15 类属性"],
], widths=[4.6, 4.4, 5.2, 3.0], font=8.5)

doc.add_heading("三、建图脚本要点", level=1)
para(doc, "建图脚本 import_kg.cypher 全部使用 MERGE 语句，可重复执行而不产生重复节点；"
          "关系两侧的节点通过 MATCH 定位后建立，关系属性用 SET 写入。核心写法如下：")
code_block(doc, "// 药品节点（数据属性即节点属性）\n"
                "MERGE (d:Drug {id:'osimertinib'}) SET d.name='奥希替尼', d.annualCost=183600, ...;\n\n"
                "// 关系 + 关系属性（治疗线与联合方案）\n"
                "MATCH (d:Drug {id:'osimertinib'}), (t:Disease {id:'nsclc'})\n"
                "MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.target='EGFR T790M';")

doc.add_heading("四、查询语句与实测结果", level=1)
para(doc, "以下 17 条查询均在 Neo4j 5.26.33 上真实执行，结果表为 Cypher Shell 的原样输出。"
          "每条查询前给出批注：说明其语法要点与业务含义。")

for q in res:
    h = doc.add_heading(f"{q['id']}  {q['title']}", level=2)
    h.paragraph_format.space_before = Pt(10)
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.space_after = Pt(3)
    set_run(p.add_run("批注："), 9, bold=True, color="1F4E79")
    set_run(p.add_run(q["note"].replace("\n", "")), 9, color="404040")
    code_block(doc, q["cypher"], 8.2)
    if len(q["header"]) == 1 or not q["rows"]:
        code_block(doc, q["raw"], 7.6)
    else:
        max_rows = 30
        ncol = len(q["header"])
        rows = [((r + [""] * ncol)[:ncol]) for r in q["rows"][:max_rows]]
        table(doc, q["header"], rows, font=7.6,
              header_fill="E8F0FE")
        if len(q["rows"]) > max_rows:
            set_run(doc.add_paragraph().add_run(f"（共 {len(q['rows'])} 行，此处截取前 {max_rows} 行）"),
                    8, color="808080")

doc.add_heading("五、需求覆盖对照", level=1)
table(doc, ["作业要求", "对应实现", "查询编号"], [
    ["Match(n) 展示节点及其属性", "全图预览、药品节点属性、单节点 map 投影", "Q3、Q4、Q5"],
    ["展示关系及其属性", "适应症（治疗线/方案）、生产（角色）、不良反应（发生率）", "Q6、Q7、Q8"],
    ["关系属性参与筛选与聚合", "按发生率过滤、按降幅排序、企业药品数聚合", "Q8、Q10、Q14"],
    ["路径与多跳关联", "两跳路径、可变长度路径、最短路径", "Q11、Q12、Q13"],
    ["与本体推理结论对应", "PART_OF 传递路径对应本体传递属性推理", "Q12"],
    ["图谱规模与类型统计", "节点类型分布、关系类型分布", "Q1、Q2"],
], widths=[5.4, 8.0, 3.0], font=8.5, align_center_cols=(2,))

doc.save(os.path.join(HERE, "Neo4j查询文档.docx"))
print("已生成 Neo4j查询文档.docx")
