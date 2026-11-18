# 《抗肿瘤药品与医保谈判》领域本体与知识图谱

基于 **Protégé / OWL 2 DL** 构建的医药政策领域本体，并用 **Neo4j** 将其映射为知识图谱，配套推理机验证与 Cypher 查询集。

## 一、项目内容

| 类别 | 内容 |
|------|------|
| 本体 | 25 个命名类 + 3 个定义类、14 组对象属性（27 条含逆属性）、23 个数据属性、38 个个体 |
| 推理 | HermiT 推理机，一致性通过，推出 6 条类归属断言 + 2 条对象属性断言 |
| 图谱 | 38 个节点 / 56 条关系（含关系属性），17 条 Cypher 查询全部实测通过 |
| 文档 | `docs/概念结构表.docx`（含结构图）、`docs/Neo4j查询文档.docx`（含批注与实测结果） |

## 二、目录结构

```
.
├── ontology/
│   ├── anticancer-drug-insurance.owl    # 本体文件（RDF/XML，Protégé 直接打开）
│   └── build_ontology.py                # 本体构建脚本（owlready2，可复现）
├── neo4j/
│   ├── import_kg.cypher                 # 建图脚本（MERGE，可重复执行）
│   ├── queries.cypher                   # 17 条查询（带中文批注）
│   ├── queries_def.py                   # 查询定义与批注源文件
│   ├── run_queries.py                   # 批量执行查询并保存结果
│   └── n4j.py / start_neo4j.py          # Neo4j 命令行调用与启动辅助
├── docs/
│   ├── 概念结构表.docx                   # 类/属性/个体结构表 + 结构图 + 推理结果
│   ├── Neo4j查询文档.docx                # 查询批注 + 代码 + 实测结果表
│   ├── concept_structure.png            # 类层次结构图
│   └── build_docs.py / draw_tree.py     # 文档与图片生成脚本
├── results/
│   ├── reasoning_report.txt             # HermiT 推理报告
│   ├── query_results.txt                # 17 条查询的原始输出
│   └── query_results.json               # 结构化查询结果
└── screenshots/                         # 运行截图（Protégé / Neo4j Browser / GitHub）
```

## 三、本体设计要点

### 3.1 类层次（一级分支之间互斥）

```
药品 ─┬─ 抗肿瘤药品 ─┬─ 化学治疗药
      │              ├─ 靶向治疗药
      │              ├─ 免疫检查点抑制剂
      │              └─ 内分泌治疗药
      └─ 辅助用药
组织机构 ─┬─ 制药企业
          └─ 监管机构
疾病 ─┬─ 恶性肿瘤
      └─ 不良反应
医保谈判 ─┬─ 国家医保药品谈判
          └─ 集中带量采购
医保目录条目 / 价格记录 / 证据（临床试验、药物经济学评价）/ 地区（国家、省级行政区、地级市）
```

### 3.2 属性设计

- **对象属性**全部给出定义域/值域，并成对设置**逆属性**（如 `纳入目录` / `收录药品`）；
- `包含下级地区` 与 `隶属于地区` 设为**传递属性**，`联合用药` 设为**对称属性**；
- **数据属性**覆盖通用名、商品名、批准文号、剂型、规格、年治疗费用、是否国产、谈判前后价格、降幅、目录版本、生效日期、ICD 编码、证据等级等，并声明 xsd 数据类型与函数属性约束。

### 3.3 推理设计（3 个定义类）

| 定义类 | 等价定义 | 推理结果 |
|--------|----------|----------|
| 医保谈判成功药品 | 药品 ⊓ ∃纳入目录.医保目录条目 | 4 个实例 |
| 谈判未成功药品 | 药品 ⊓ ∃经谈判于.国家医保药品谈判 ⊓ ¬∃纳入目录.医保目录条目 | 1 个（帕博利珠单抗） |
| 肺癌治疗药品 | 抗肿瘤药品 ⊓ ∃适用于.{非小细胞肺癌} | 4 个实例 |

> 注：OWL 是开放世界语义，"没有断言"不等于"不存在"。因此对帕博利珠单抗额外加了
> 个体级闭合公理 `纳入目录 max 0`，推理机才能证明其否定条件。

## 四、如何复现

### 4.1 打开本体（Protégé）

1. 启动 Protégé → `File → Open` → 选择 `ontology/anticancer-drug-insurance.owl`；
2. 实体默认按 `rdfs:label` 渲染，界面上显示为中文；
3. 左侧 `Entities` 标签页可查看 Classes / Object properties / Data properties / Individuals。

### 4.2 运行推理机

`Reasoner → HermiT → Start reasoner`（或 `Ctrl+R`）。推理后：
- 被推断出的类归属以**浅黄色背景**出现在 Individuals 面板；
- 在 `DL Query` 标签页输入 `医保谈判成功药品`、`肺癌治疗药品` 可列出推断实例。

命令行复现（本仓库实测方式）：

```bash
python results/run_reasoner.py    # 需要 Java 17 + owlready2（内置 HermiT）
```

### 4.3 导入 Neo4j 并查询

```bash
# 启动
neo4j.bat console

# 建图
cypher-shell -a bolt://localhost:7687 -u neo4j -p Neo4j@2026 -f neo4j/import_kg.cypher

# 交互查询
cypher-shell -a bolt://localhost:7687 -u neo4j -p Neo4j@2026 -f neo4j/queries.cypher
```

或在 http://localhost:7474 的 Neo4j Browser 中逐条执行 `neo4j/queries.cypher`。

## 五、本体 → 图模型映射

| 本体元素 | Neo4j 元素 |
|----------|-----------|
| 类 | 节点标签（`:Drug`、`:Company`、`:Negotiation` …） |
| 对象属性 | 关系类型（`INDICATED_FOR`、`LISTED_IN` …） |
| 数据属性 | 节点属性（`name`、`annualCost` …） |
| 关系附加语义 | 关系属性（`r.line='一线'`、`r.result='成功'` …） |

## 六、数据说明

实例数据（药品价格、谈判年份、降幅等）为**公开报道量级的教学示例**。
