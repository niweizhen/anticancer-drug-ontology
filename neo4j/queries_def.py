# -*- coding: utf-8 -*-
"""全部 Cypher 查询定义 + 中文批注（供 run_queries.py 执行与文档引用）。"""

QUERIES = [
    ("Q1", "图谱规模：节点类型分布",
     "MATCH (n) 不限定标签，匹配全图所有节点；labels(n)[0] 取节点主标签，count(n) 聚合计数，\n"
     "用来快速核对本体类是否都落成了节点标签。",
     "MATCH (n) "
     "RETURN labels(n)[0] AS 节点类型, count(n) AS 数量 "
     "ORDER BY 数量 DESC"),

    ("Q2", "图谱规模：关系类型分布",
     "MATCH ()-[r]->() 匹配所有关系（两端节点用匿名占位），type(r) 返回关系类型，\n"
     "对应本体的 14 个对象属性（其中联合用药为对称关系，双向各存一条）。",
     "MATCH ()-[r]->() "
     "RETURN type(r) AS 关系类型, count(r) AS 数量 "
     "ORDER BY 数量 DESC"),

    ("Q3", "全图预览：MATCH (n) RETURN n",
     "最基础的图浏览语句，直接返回节点对象，Neo4j Browser 里会渲染成图形。\n"
     "LIMIT 25 防止一次拉取过多节点影响渲染性能。",
     "MATCH (n) RETURN n LIMIT 25"),

    ("Q4", "节点及其属性：全部抗肿瘤/辅助药品",
     "限定标签 :Drug，用 n.属性名 投影节点的数据属性；ORDER BY 按年治疗费用降序，\n"
     "体现本体的 8 个药品数据属性（商品名、类别、剂型、规格、年费用、是否国产、上市年份等）。",
     "MATCH (n:Drug) "
     "RETURN n.name AS 药品, n.brand AS 商品名, n.category AS 类别, n.form AS 剂型, "
     "n.spec AS 规格, n.annualCost AS 年治疗费用, n.domestic AS 是否国产, n.launchYear AS 上市年份 "
     "ORDER BY n.annualCost DESC"),

    ("Q5", "单个节点的完整属性：map 投影 n {.*}",
     "n {.*} 是 Cypher 的 map 投影语法，一次性取出该节点所有属性，\n"
     "适合不确定属性全集时做数据核查；此处查奥希替尼。",
     "MATCH (d:Drug {name:'奥希替尼'}) "
     "RETURN d {.*} AS 完整属性"),

    ("Q6", "关系及其属性：适应症关系（含治疗线与方案）",
     "MATCH (d:Drug)-[r:INDICATED_FOR]->(t:Disease) 匹配『药品→疾病』的有向关系，\n"
     "r.line、r.regimen 读取关系自身的属性，这是把本体对象属性加上属性值后的图谱化表达。",
     "MATCH (d:Drug)-[r:INDICATED_FOR]->(t:Disease) "
     "RETURN d.name AS 药品, type(r) AS 关系类型, t.name AS 疾病, "
     "r.line AS 治疗线, r.regimen AS 联合方案 "
     "ORDER BY 药品"),

    ("Q7", "关系及其属性：生产关系（含角色）",
     "MANUFACTURED_BY 关系上带 role 属性（原研厂家/仿制厂家），同时读取企业节点的 type、\n"
     "体现『关系属性 + 节点属性』的联合展示。",
     "MATCH (d:Drug)-[r:MANUFACTURED_BY]->(c:Company) "
     "RETURN d.name AS 药品, r.role AS 角色, c.name AS 企业, c.type AS 企业类型 "
     "ORDER BY 企业"),

    ("Q8", "关系属性过滤：发生率为『高』的不良反应",
     "WHERE r.incidence = '高' 直接对关系属性做条件过滤，\n"
     "说明关系属性可以和节点属性一样参与筛选、排序与聚合。",
     "MATCH (d:Drug)-[r:CAUSES]->(a:AdverseReaction) "
     "WHERE r.incidence = '高' "
     "RETURN d.name AS 药品, a.name AS 不良反应, r.incidence AS 发生率"),

    ("Q9", "医保谈判结果：关系属性 result / round",
     "谈判事件→药品的 NEGOTIATED 关系上存有 result（成功/未成功）与 round（轮次），\n"
     "可据此区分『进了目录』与『谈了但没进』两类药品，对应本体中的两个定义类。",
     "MATCH (n:Negotiation)-[r:NEGOTIATED]->(d:Drug) "
     "RETURN n.name AS 谈判事件, d.name AS 药品, r.result AS 结果, r.round AS 轮次 "
     "ORDER BY 结果, 药品"),

    ("Q10", "价格降幅对比：谈判前后价格与降幅",
     "round(表达式, 1) 保留一位小数；价格记录作为独立节点挂载，\n"
     "关系 HAS_PRICE 上再用 basis、currency 标注计价口径，避免单位歧义。",
     "MATCH (d:Drug)-[h:HAS_PRICE]->(p:PriceRecord) "
     "RETURN d.name AS 药品, p.priceBefore AS 谈判前价格, p.priceAfter AS 谈判后价格, "
     "round(p.cutRate*100, 1) AS 降幅百分比, h.basis AS 计价单位 "
     "ORDER BY 降幅百分比 DESC"),

    ("Q11", "两跳路径：药品→目录→覆盖地区",
     "沿着 LISTED_IN、COVERS 两条关系做两跳遍历，一次拿到『谁在哪个目录、何时纳入、覆盖到哪』，\n"
     "对应本体里 InsuranceListing 作为中介概念的建模价值。",
     "MATCH (d:Drug)-[l:LISTED_IN]->(li:Listing)-[c:COVERS]->(rg:Region) "
     "RETURN d.name AS 药品, li.version AS 目录版本, l.since AS 纳入时间, "
     "rg.name AS 覆盖地区, c.scope AS 覆盖范围"),

    ("Q12", "可变长度路径：行政区划的传递关系",
     "[:PART_OF*1..3] 表示沿 PART_OF 走 1~3 跳。库里只存了『广州市→广东省』『广东省→中国』\n"
     "两条直接关系，此处一趟查询就得到『广州市→中国』，与本体中传递属性 hasSubRegion/partOfRegion\n"
     "推出的结论一致。",
     "MATCH path = (c:Region {name:'广州市'})-[:PART_OF*1..3]->(p:Region {name:'中国'}) "
     "RETURN path"),

    ("Q13", "最短路径：企业到疾病的多跳关联",
     "shortestPath() 求两节点间最短关系链，[*..5] 表示不限关系类型、最多 5 跳，\n"
     "用于发现『默沙东』与『非小细胞肺癌』之间的关联链路（企业—药品—适应症）。",
     "MATCH p = shortestPath((c:Company {name:'默沙东'})-[*..5]-(t:Disease {name:'非小细胞肺癌'})) "
     "RETURN p"),

    ("Q14", "聚合统计：各企业在研/在售药品数",
     "count() 与 collect() 组合，按企业分组聚合，collect 把药品名收成列表，\n"
     "可直接用于谈判参与方的产品线画像。",
     "MATCH (c:Company)<-[:MANUFACTURED_BY]-(d:Drug) "
     "RETURN c.name AS 企业, count(d) AS 药品数量, collect(d.name) AS 药品列表 "
     "ORDER BY 药品数量 DESC"),

    ("Q15", "共同适应症：同类竞品发现",
     "同一疾病节点被多个药品指向时，两两配对即为潜在竞品；\n"
     "WHERE a.name < b.name 用来去掉重复与自配对（字符串比较保证只算一次）。",
     "MATCH (a:Drug)-[:INDICATED_FOR]->(t:Disease)<-[:INDICATED_FOR]-(b:Drug) "
     "WHERE a.name < b.name "
     "RETURN t.name AS 疾病, a.name AS 药品A, b.name AS 药品B "
     "ORDER BY 疾病"),

    ("Q16", "证据链：谈判→证据→药品",
     "三段关系串联，验证『谈判决策有据可依』的建模：SUPPORTED_BY 上的 weight 表示证据权重，\n"
     "EVALUATES 上的 endpoint 表示评价终点。",
     "MATCH (n:Negotiation)-[s:SUPPORTED_BY]->(e:Evidence)-[v:EVALUATES]->(d:Drug) "
     "RETURN n.name AS 谈判事件, e.name AS 证据, s.weight AS 证据权重, "
     "v.endpoint AS 评价终点, d.name AS 药品"),

    ("Q17", "关系属性：联合用药方案",
     "COMBINED_WITH 在本体中被定义为对称属性，图中双向各存一条，\n"
     "关系属性 regimen 记录该组合所属的临床研究/方案。",
     "MATCH (a:Drug)-[r:COMBINED_WITH]->(b:Drug) "
     "RETURN a.name AS 药品A, b.name AS 药品B, r.regimen AS 联合方案 "
     "ORDER BY 药品A"),
]
