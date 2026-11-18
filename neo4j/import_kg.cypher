// =============================================================
// 《抗肿瘤药品与医保谈判》知识图谱 —— 建图脚本
// 数据来源：anticancer-drug-insurance.owl（本体实例层 ABox 的等价映射）
// 约定：类 → 节点标签；对象属性 → 关系类型；数据属性 → 节点/关系属性
// 全部使用 MERGE，可重复执行不产生重复数据
// =============================================================

// ---------- 0. 清空旧图（首次导入时执行；重复导入可注释掉） ----------
MATCH (n) DETACH DELETE n;

// ---------- 1. 制药企业与监管机构 ----------
MERGE (msd:Company {id:'msd'}) SET msd.name='默沙东', msd.type='外资药企', msd.founded=1891;
MERGE (innovent:Company {id:'innovent'}) SET innovent.name='信达生物', innovent.type='本土创新药企', innovent.founded=2011;
MERGE (astrazeneca:Company {id:'astrazeneca'}) SET astrazeneca.name='阿斯利康', astrazeneca.type='外资药企', astrazeneca.founded=1999;
MERGE (roche:Company {id:'roche'}) SET roche.name='罗氏', roche.type='外资药企', roche.founded=1896;
MERGE (hengrui:Company {id:'hengrui'}) SET hengrui.name='恒瑞医药', hengrui.type='本土药企', hengrui.founded=1970;
MERGE (nhsa:Agency {id:'nhsa'}) SET nhsa.name='国家医疗保障局';

// ---------- 2. 疾病与不良反应 ----------
MERGE (nsclc:Disease {id:'nsclc'}) SET nsclc.name='非小细胞肺癌', nsclc.icd='C34.9', nsclc.survival5y=0.26;
MERGE (breast:Disease {id:'breast_cancer'}) SET breast.name='乳腺癌', breast.icd='C50', breast.survival5y=0.83;
MERGE (crc:Disease {id:'crc'}) SET crc.name='结直肠癌', crc.icd='C18', crc.survival5y=0.65;
MERGE (hcc:Disease {id:'hcc'}) SET hcc.name='肝细胞癌', hcc.icd='C22.0', hcc.survival5y=0.14;
MERGE (ir_ae:AdverseReaction {id:'ir_ae'}) SET ir_ae.name='免疫相关性肺炎';
MERGE (neutropenia:AdverseReaction {id:'neutropenia'}) SET neutropenia.name='中性粒细胞减少症';
MERGE (cinv:AdverseReaction {id:'cinv'}) SET cinv.name='化疗相关恶心呕吐';

// ---------- 3. 药品 ----------
MERGE (pemb:Drug {id:'pembrolizumab'}) SET pemb.name='帕博利珠单抗', pemb.brand='可瑞达', pemb.category='免疫检查点抑制剂',
  pemb.form='注射剂', pemb.spec='100mg/4ml', pemb.annualCost=320000, pemb.domestic=false, pemb.launchYear=2018, pemb.approval='国药准字SJ20180019';
MERGE (sinti:Drug {id:'sintilimab'}) SET sinti.name='信迪利单抗', sinti.brand='达伯舒', sinti.category='免疫检查点抑制剂',
  sinti.form='注射剂', sinti.spec='100mg/10ml', sinti.annualCost=98000, sinti.domestic=true, sinti.launchYear=2018, sinti.approval='国药准字S20180016';
MERGE (osi:Drug {id:'osimertinib'}) SET osi.name='奥希替尼', osi.brand='泰瑞沙', osi.category='靶向治疗药',
  osi.form='片剂', osi.spec='80mg', osi.annualCost=183600, osi.domestic=false, osi.launchYear=2017, osi.approval='国药准字HJ20170150';
MERGE (tras:Drug {id:'trastuzumab'}) SET tras.name='曲妥珠单抗', tras.brand='赫赛汀', tras.category='靶向治疗药',
  tras.form='注射剂', tras.spec='440mg', tras.annualCost=165000, tras.domestic=false, tras.launchYear=2002, tras.approval='国药准字SJ20170046';
MERGE (bev:Drug {id:'bevacizumab'}) SET bev.name='贝伐珠单抗', bev.brand='安维汀', bev.category='靶向治疗药',
  bev.form='注射剂', bev.spec='100mg/4ml', bev.annualCost=120000, bev.domestic=false, bev.launchYear=2010, bev.approval='国药准字SJ20100047';
MERGE (pem:Drug {id:'pemetrexed'}) SET pem.name='培美曲塞', pem.brand='力比泰', pem.category='化学治疗药',
  pem.form='注射剂', pem.spec='500mg', pem.annualCost=60000, pem.domestic=true, pem.launchYear=2005, pem.approval='国药准字H20051288';
MERGE (nab:Drug {id:'paclitaxel_nab'}) SET nab.name='白蛋白结合型紫杉醇', nab.brand='艾越', nab.category='化学治疗药',
  nab.form='注射剂', nab.spec='100mg', nab.annualCost=72000, nab.domestic=true, nab.launchYear=2018, nab.approval='国药准字H20183044';
MERGE (palo:Drug {id:'palonosetron'}) SET palo.name='帕洛诺司琼', palo.brand='诺威', palo.category='辅助用药',
  palo.form='注射剂', palo.spec='0.25mg', palo.annualCost=6000, palo.domestic=true, palo.launchYear=2008, palo.approval='国药准字H20080776';

// ---------- 4. 谈判事件 / 目录条目 / 价格记录 / 证据 ----------
MERGE (neg2023:Negotiation {id:'neg2023'}) SET neg2023.name='2023年国家医保药品目录谈判', neg2023.year=2023, neg2023.round=6, neg2023.avgCut=0.615;
MERGE (neg2024:Negotiation {id:'neg2024'}) SET neg2024.name='2024年国家医保药品目录谈判', neg2024.year=2024, neg2024.round=7, neg2024.avgCut=0.63;
MERGE (vbp5:Negotiation {id:'vbp5'}) SET vbp5.name='第五批国家组织药品集中带量采购', vbp5.year=2021, vbp5.avgCut=0.56;
MERGE (list2023:Listing {id:'list2023'}) SET list2023.version='2023年版', list2023.effective='2023-03-01';
MERGE (list2024:Listing {id:'list2024'}) SET list2024.version='2024年版', list2024.effective='2024-01-01';
MERGE (pr_osi:PriceRecord {id:'pr_osi'}) SET pr_osi.name='奥希替尼2017年谈判价格记录', pr_osi.priceBefore=51000, pr_osi.priceAfter=15300, pr_osi.cutRate=0.70;
MERGE (pr_sin:PriceRecord {id:'pr_sin'}) SET pr_sin.name='信迪利单抗2019年谈判价格记录', pr_sin.priceBefore=7838, pr_sin.priceAfter=2843, pr_sin.cutRate=0.637;
MERGE (pr_tras:PriceRecord {id:'pr_tras'}) SET pr_tras.name='曲妥珠单抗2017年谈判价格记录', pr_tras.priceBefore=24500, pr_tras.priceAfter=7600, pr_tras.cutRate=0.69;
MERGE (pr_bev:PriceRecord {id:'pr_bev'}) SET pr_bev.name='贝伐珠单抗2017年谈判价格记录', pr_bev.priceBefore=5210, pr_bev.priceAfter=1998, pr_bev.cutRate=0.616;
MERGE (ct1:Evidence {id:'ct_keynote189'}) SET ct1.name='KEYNOTE-189 临床试验', ct1.type='临床试验', ct1.level='1a', ct1.year=2018;
MERGE (ct2:Evidence {id:'ct_orient11'}) SET ct2.name='ORIENT-11 临床试验', ct2.type='临床试验', ct2.level='1b', ct2.year=2020;
MERGE (pe1:Evidence {id:'pe_sin'}) SET pe1.name='信迪利单抗药物经济学评价', pe1.type='药物经济学评价', pe1.level='模型研究', pe1.year=2023;

// ---------- 5. 地区 ----------
MERGE (china:Region {id:'china'}) SET china.name='中国', china.adminCode='100000', china.level='国家';
MERGE (gd:Region {id:'guangdong'}) SET gd.name='广东省', gd.adminCode='440000', gd.level='省级行政区';
MERGE (gz:Region {id:'guangzhou'}) SET gz.name='广州市', gz.adminCode='440100', gz.level='地级市';
MERGE (bj:Region {id:'beijing'}) SET bj.name='北京市', bj.adminCode='110000', bj.level='地级市';
MERGE (sh:Region {id:'shanghai'}) SET sh.name='上海市', sh.adminCode='310000', sh.level='地级市';

// ---------- 6. 关系：生产（关系带属性 role） ----------
MATCH (d:Drug {id:'pembrolizumab'}), (c:Company {id:'msd'}) MERGE (d)-[r:MANUFACTURED_BY]->(c) SET r.role='原研厂家';
MATCH (d:Drug {id:'sintilimab'}), (c:Company {id:'innovent'}) MERGE (d)-[r:MANUFACTURED_BY]->(c) SET r.role='原研厂家';
MATCH (d:Drug {id:'osimertinib'}), (c:Company {id:'astrazeneca'}) MERGE (d)-[r:MANUFACTURED_BY]->(c) SET r.role='原研厂家';
MATCH (d:Drug {id:'trastuzumab'}), (c:Company {id:'roche'}) MERGE (d)-[r:MANUFACTURED_BY]->(c) SET r.role='原研厂家';
MATCH (d:Drug {id:'bevacizumab'}), (c:Company {id:'roche'}) MERGE (d)-[r:MANUFACTURED_BY]->(c) SET r.role='原研厂家';
MATCH (d:Drug {id:'pemetrexed'}), (c:Company {id:'hengrui'}) MERGE (d)-[r:MANUFACTURED_BY]->(c) SET r.role='仿制厂家';
MATCH (d:Drug {id:'paclitaxel_nab'}), (c:Company {id:'hengrui'}) MERGE (d)-[r:MANUFACTURED_BY]->(c) SET r.role='仿制厂家';

// ---------- 7. 关系：适应症（关系带属性 line/regimen/target） ----------
MATCH (d:Drug {id:'pembrolizumab'}), (t:Disease {id:'nsclc'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.regimen='联合培美曲塞+铂类';
MATCH (d:Drug {id:'sintilimab'}), (t:Disease {id:'nsclc'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.regimen='联合培美曲塞+铂类';
MATCH (d:Drug {id:'osimertinib'}), (t:Disease {id:'nsclc'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.target='EGFR T790M';
MATCH (d:Drug {id:'pemetrexed'}), (t:Disease {id:'nsclc'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.regimen='含铂双药方案';
MATCH (d:Drug {id:'trastuzumab'}), (t:Disease {id:'breast_cancer'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.target='HER2';
MATCH (d:Drug {id:'paclitaxel_nab'}), (t:Disease {id:'breast_cancer'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='二线';
MATCH (d:Drug {id:'bevacizumab'}), (t:Disease {id:'crc'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.target='VEGF';
MATCH (d:Drug {id:'bevacizumab'}), (t:Disease {id:'hcc'}) MERGE (d)-[r:INDICATED_FOR]->(t) SET r.line='一线', r.target='VEGF';

// ---------- 8. 关系：不良反应（关系带属性 incidence） ----------
MATCH (d:Drug {id:'pembrolizumab'}), (a:AdverseReaction {id:'ir_ae'}) MERGE (d)-[r:CAUSES]->(a) SET r.incidence='3%~5%';
MATCH (d:Drug {id:'sintilimab'}), (a:AdverseReaction {id:'ir_ae'}) MERGE (d)-[r:CAUSES]->(a) SET r.incidence='2%~4%';
MATCH (d:Drug {id:'osimertinib'}), (a:AdverseReaction {id:'neutropenia'}) MERGE (d)-[r:CAUSES]->(a) SET r.incidence='常见';
MATCH (d:Drug {id:'pemetrexed'}), (a:AdverseReaction {id:'neutropenia'}) MERGE (d)-[r:CAUSES]->(a) SET r.incidence='常见';
MATCH (d:Drug {id:'pemetrexed'}), (a:AdverseReaction {id:'cinv'}) MERGE (d)-[r:CAUSES]->(a) SET r.incidence='高';
MATCH (d:Drug {id:'paclitaxel_nab'}), (a:AdverseReaction {id:'neutropenia'}) MERGE (d)-[r:CAUSES]->(a) SET r.incidence='高';
MATCH (d:Drug {id:'palonosetron'}), (a:AdverseReaction {id:'cinv'}) MERGE (d)-[r:TREATS]->(a) SET r.efficacy='完全缓解率约60%';

// ---------- 9. 关系：联合用药（对称关系，双向各建一条） ----------
MATCH (a:Drug {id:'pembrolizumab'}), (b:Drug {id:'pemetrexed'}) MERGE (a)-[r:COMBINED_WITH]->(b) SET r.regimen='KEYNOTE-189';
MATCH (b:Drug {id:'pemetrexed'}), (a:Drug {id:'pembrolizumab'}) MERGE (a)-[r:COMBINED_WITH]->(b) SET r.regimen='KEYNOTE-189';
MATCH (a:Drug {id:'trastuzumab'}), (b:Drug {id:'paclitaxel_nab'}) MERGE (a)-[r:COMBINED_WITH]->(b) SET r.regimen='术后辅助化疗';
MATCH (b:Drug {id:'paclitaxel_nab'}), (a:Drug {id:'trastuzumab'}) MERGE (a)-[r:COMBINED_WITH]->(b) SET r.regimen='术后辅助化疗';

// ---------- 10. 关系：谈判（关系带属性 result/round） ----------
MATCH (n:Negotiation {id:'neg2023'}), (d:Drug {id:'sintilimab'}) MERGE (n)-[r:NEGOTIATED]->(d) SET r.result='成功', r.round=6;
MATCH (n:Negotiation {id:'neg2023'}), (d:Drug {id:'osimertinib'}) MERGE (n)-[r:NEGOTIATED]->(d) SET r.result='成功', r.round=6;
MATCH (n:Negotiation {id:'neg2023'}), (d:Drug {id:'trastuzumab'}) MERGE (n)-[r:NEGOTIATED]->(d) SET r.result='成功', r.round=6;
MATCH (n:Negotiation {id:'neg2023'}), (d:Drug {id:'bevacizumab'}) MERGE (n)-[r:NEGOTIATED]->(d) SET r.result='成功', r.round=6;
MATCH (n:Negotiation {id:'neg2023'}), (d:Drug {id:'pembrolizumab'}) MERGE (n)-[r:NEGOTIATED]->(d) SET r.result='未成功', r.round=6;
MATCH (n:Negotiation {id:'neg2024'}), (d:Drug {id:'pembrolizumab'}) MERGE (n)-[r:NEGOTIATED]->(d) SET r.result='未成功', r.round=7;
MATCH (n:Negotiation {id:'neg2023'}), (a:Agency {id:'nhsa'}) MERGE (n)-[r:ORGANIZED_BY]->(a) SET r.role='组织方';
MATCH (n:Negotiation {id:'neg2024'}), (a:Agency {id:'nhsa'}) MERGE (n)-[r:ORGANIZED_BY]->(a) SET r.role='组织方';
MATCH (n:Negotiation {id:'vbp5'}), (a:Agency {id:'nhsa'}) MERGE (n)-[r:ORGANIZED_BY]->(a) SET r.role='组织方';
MATCH (c:Company {id:'msd'}), (n:Negotiation {id:'neg2023'}) MERGE (c)-[r:PARTICIPATED_IN]->(n) SET r.role='谈判方', r.drugs=1;
MATCH (c:Company {id:'innovent'}), (n:Negotiation {id:'neg2023'}) MERGE (c)-[r:PARTICIPATED_IN]->(n) SET r.role='谈判方', r.drugs=1;
MATCH (c:Company {id:'astrazeneca'}), (n:Negotiation {id:'neg2023'}) MERGE (c)-[r:PARTICIPATED_IN]->(n) SET r.role='谈判方', r.drugs=1;
MATCH (c:Company {id:'roche'}), (n:Negotiation {id:'neg2023'}) MERGE (c)-[r:PARTICIPATED_IN]->(n) SET r.role='谈判方', r.drugs=2;

// ---------- 11. 关系：纳入目录（关系带属性 since/catalog） ----------
MATCH (d:Drug {id:'sintilimab'}), (l:Listing {id:'list2023'}) MERGE (d)-[r:LISTED_IN]->(l) SET r.since='2023-03-01', r.catalog='2023年版';
MATCH (d:Drug {id:'osimertinib'}), (l:Listing {id:'list2023'}) MERGE (d)-[r:LISTED_IN]->(l) SET r.since='2023-03-01', r.catalog='2023年版';
MATCH (d:Drug {id:'trastuzumab'}), (l:Listing {id:'list2023'}) MERGE (d)-[r:LISTED_IN]->(l) SET r.since='2023-03-01', r.catalog='2023年版';
MATCH (d:Drug {id:'bevacizumab'}), (l:Listing {id:'list2023'}) MERGE (d)-[r:LISTED_IN]->(l) SET r.since='2023-03-01', r.catalog='2023年版';
MATCH (l:Listing {id:'list2023'}), (rg:Region {id:'china'}) MERGE (l)-[r:COVERS]->(rg) SET r.scope='全国';
MATCH (l:Listing {id:'list2024'}), (rg:Region {id:'china'}) MERGE (l)-[r:COVERS]->(rg) SET r.scope='全国';

// ---------- 12. 关系：价格记录（关系带属性 basis） ----------
MATCH (d:Drug {id:'osimertinib'}), (p:PriceRecord {id:'pr_osi'}) MERGE (d)-[r:HAS_PRICE]->(p) SET r.basis='盒/月', r.currency='CNY';
MATCH (d:Drug {id:'sintilimab'}), (p:PriceRecord {id:'pr_sin'}) MERGE (d)-[r:HAS_PRICE]->(p) SET r.basis='瓶', r.currency='CNY';
MATCH (d:Drug {id:'trastuzumab'}), (p:PriceRecord {id:'pr_tras'}) MERGE (d)-[r:HAS_PRICE]->(p) SET r.basis='瓶', r.currency='CNY';
MATCH (d:Drug {id:'bevacizumab'}), (p:PriceRecord {id:'pr_bev'}) MERGE (d)-[r:HAS_PRICE]->(p) SET r.basis='瓶', r.currency='CNY';

// ---------- 13. 关系：证据支撑（关系带属性 weight） ----------
MATCH (n:Negotiation {id:'neg2023'}), (e:Evidence {id:'ct_keynote189'}) MERGE (n)-[r:SUPPORTED_BY]->(e) SET r.weight='高';
MATCH (n:Negotiation {id:'neg2023'}), (e:Evidence {id:'ct_orient11'}) MERGE (n)-[r:SUPPORTED_BY]->(e) SET r.weight='高';
MATCH (n:Negotiation {id:'neg2023'}), (e:Evidence {id:'pe_sin'}) MERGE (n)-[r:SUPPORTED_BY]->(e) SET r.weight='中';
MATCH (e:Evidence {id:'ct_keynote189'}), (d:Drug {id:'pembrolizumab'}) MERGE (e)-[r:EVALUATES]->(d) SET r.endpoint='OS/PFS';
MATCH (e:Evidence {id:'ct_orient11'}), (d:Drug {id:'sintilimab'}) MERGE (e)-[r:EVALUATES]->(d) SET r.endpoint='PFS';
MATCH (e:Evidence {id:'pe_sin'}), (d:Drug {id:'sintilimab'}) MERGE (e)-[r:EVALUATES]->(d) SET r.endpoint='ICER';

// ---------- 14. 关系：行政区划隶属（只有直接层级，跨层级由路径查询推出） ----------
MATCH (c:Region {id:'guangzhou'}), (p:Region {id:'guangdong'}) MERGE (c)-[r:PART_OF]->(p) SET r.type='地级市→省';
MATCH (c:Region {id:'guangdong'}), (p:Region {id:'china'}) MERGE (c)-[r:PART_OF]->(p) SET r.type='省→国家';
MATCH (c:Region {id:'beijing'}), (p:Region {id:'china'}) MERGE (c)-[r:PART_OF]->(p) SET r.type='直辖市→国家';
MATCH (c:Region {id:'shanghai'}), (p:Region {id:'china'}) MERGE (c)-[r:PART_OF]->(p) SET r.type='直辖市→国家';

// ---------- 15. 导入结果自检 ----------
MATCH (n) RETURN labels(n)[0] AS 节点类型, count(*) AS 数量 ORDER BY 数量 DESC;
MATCH ()-[r]->() RETURN type(r) AS 关系类型, count(*) AS 数量 ORDER BY 数量 DESC;
