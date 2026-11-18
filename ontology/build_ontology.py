# -*- coding: utf-8 -*-
"""
构建《抗肿瘤药品与医保谈判》本体（Anticancer Drug & Medical Insurance Negotiation Ontology）
输出：anticancer-drug-insurance.owl（RDF/XML，Protégé 5.x 可直接打开）
"""
import os
from owlready2 import (
    get_ontology, Thing, ObjectProperty, DataProperty, FunctionalProperty,
    TransitiveProperty, SymmetricProperty, AllDisjoint, Not, OneOf, sync_reasoner_hermit,
)

BASE = "http://www.semanticweb.org/bbi/ontologies/2026/11/anticancer-drug-insurance"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anticancer-drug-insurance.owl")

onto = get_ontology(BASE)

with onto:
    # ============ 一、类（Class）层次结构 ============
    class Drug(Thing): pass                      # 药品
    class AnticancerDrug(Drug): pass             # 抗肿瘤药品
    class ChemotherapeuticAgent(AnticancerDrug): pass      # 化学治疗药
    class TargetedTherapyAgent(AnticancerDrug): pass       # 靶向治疗药
    class ImmuneCheckpointInhibitor(AnticancerDrug): pass  # 免疫检查点抑制剂
    class EndocrineTherapyAgent(AnticancerDrug): pass      # 内分泌治疗药
    class SupportiveCareDrug(Drug): pass         # 辅助用药

    class Organization(Thing): pass              # 组织机构
    class PharmaceuticalCompany(Organization): pass   # 制药企业
    class RegulatoryAgency(Organization): pass        # 监管机构

    class Disease(Thing): pass                   # 疾病
    class MalignantTumor(Disease): pass          # 恶性肿瘤
    class AdverseReaction(Disease): pass         # 不良反应

    class NegotiationEvent(Thing): pass          # 医保谈判
    class NationalDrugPriceNegotiation(NegotiationEvent): pass  # 国家医保药品谈判
    class VolumeBasedProcurement(NegotiationEvent): pass        # 集中带量采购

    class InsuranceListing(Thing): pass          # 医保目录条目
    class PriceRecord(Thing): pass               # 价格记录
    class Region(Thing): pass                    # 地区
    class Country(Region): pass                  # 国家
    class Province(Region): pass                 # 省级行政区
    class City(Region): pass                     # 地级市

    class Evidence(Thing): pass                  # 证据
    class ClinicalTrial(Evidence): pass          # 临床试验
    class PharmacoeconomicEvaluation(Evidence): pass  # 药物经济学评价

    # ---- 类的中文标签与注释 ----
    _class_meta = {
        Drug: ("药品", "以预防、治疗、诊断疾病为目的的物质，本体的核心类之一。"),
        AnticancerDrug: ("抗肿瘤药品", "以抑制肿瘤生长、杀伤肿瘤细胞为主要作用机制的药物。"),
        ChemotherapeuticAgent: ("化学治疗药", "细胞毒类抗肿瘤药，作用于 DNA 或细胞分裂过程。"),
        TargetedTherapyAgent: ("靶向治疗药", "作用于特定分子靶点（如 EGFR、HER2、VEGF）的抗肿瘤药。"),
        ImmuneCheckpointInhibitor: ("免疫检查点抑制剂", "PD-1/PD-L1/CTLA-4 等免疫检查点抑制剂，激活 T 细胞抗肿瘤。"),
        EndocrineTherapyAgent: ("内分泌治疗药", "用于激素依赖性肿瘤的内分泌治疗药物。"),
        SupportiveCareDrug: ("辅助用药", "止吐、升白、营养支持等肿瘤治疗辅助用药。"),
        Organization: ("组织机构", "承担药品研发、生产、监管或谈判职能的组织。"),
        PharmaceuticalCompany: ("制药企业", "药品的研发与生产企业，医保谈判的参与主体。"),
        RegulatoryAgency: ("监管机构", "负责药品审批与医保目录管理的政府部门。"),
        Disease: ("疾病", "包括恶性肿瘤及药物引起的不良反应。"),
        MalignantTumor: ("恶性肿瘤", "抗肿瘤药品的治疗对象，按 ICD 编码区分。"),
        AdverseReaction: ("不良反应", "用药过程中出现的有害反应。"),
        NegotiationEvent: ("医保谈判", "药品价格谈判或集中带量采购等价格形成事件。"),
        NationalDrugPriceNegotiation: ("国家医保药品谈判", "国家医保局组织的年度医保药品目录准入谈判。"),
        VolumeBasedProcurement: ("集中带量采购", "以量换价的国家组织药品集中带量采购。"),
        InsuranceListing: ("医保目录条目", "药品被纳入某一版医保目录的记录，含目录版本与覆盖地区。"),
        PriceRecord: ("价格记录", "某药品在特定时间点的谈判前后价格与降幅。"),
        Region: ("地区", "医保政策与目录的覆盖范围。"),
        Country: ("国家", "最高层级地区。"),
        Province: ("省级行政区", "省、自治区、直辖市。"),
        City: ("地级市", "地级行政区，隶属于省级行政区。"),
        Evidence: ("证据", "支撑谈判决策的临床与经济学证据。"),
        ClinicalTrial: ("临床试验", "药品有效性与安全性的试验证据。"),
        PharmacoeconomicEvaluation: ("药物经济学评价", "成本-效果、预算影响等经济学证据。"),
    }
    for c, (lab, cmt) in _class_meta.items():
        c.label = [lab]
        c.comment = [cmt]

    # ============ 二、对象属性（Object Property）============
    class manufacturedBy(ObjectProperty):
        domain = [Drug]; range = [PharmaceuticalCompany]
        label = ["生产于"]; comment = ["药品由某制药企业生产。"]
    class produces(ObjectProperty):
        domain = [PharmaceuticalCompany]; range = [Drug]
        label = ["生产药品"]; comment = ["制药企业生产某药品，是 manufacturedBy 的逆属性。"]
    manufacturedBy.inverse_property = produces

    class indicatedFor(ObjectProperty):
        domain = [AnticancerDrug]; range = [MalignantTumor]
        label = ["适用于"]; comment = ["药品获批的适应症（肿瘤类型）。"]
    class indicatedDrug(ObjectProperty):
        domain = [MalignantTumor]; range = [AnticancerDrug]
        label = ["适用药品"]; comment = ["某肿瘤类型可使用的药品，是 indicatedFor 的逆属性。"]
    indicatedFor.inverse_property = indicatedDrug

    class treats(ObjectProperty):
        domain = [Drug]; range = [Disease]
        label = ["治疗"]; comment = ["药品用于治疗某疾病，包含不良反应的对症处理。"]
    class treatedBy(ObjectProperty):
        domain = [Disease]; range = [Drug]
        label = ["被治疗于"]; comment = ["疾病由某药品治疗，是 treats 的逆属性。"]
    treats.inverse_property = treatedBy

    class causesAdverseReaction(ObjectProperty):
        domain = [Drug]; range = [AdverseReaction]
        label = ["引起不良反应"]; comment = ["药品可能导致的不良反应。"]
    class causedByDrug(ObjectProperty):
        domain = [AdverseReaction]; range = [Drug]
        label = ["由药品引起"]; comment = ["不良反应的来源药品，是 causesAdverseReaction 的逆属性。"]
    causesAdverseReaction.inverse_property = causedByDrug

    class combinedWith(ObjectProperty, SymmetricProperty):
        domain = [Drug]; range = [Drug]
        label = ["联合用药"]; comment = ["两种药品存在联合用药方案，属性为对称属性。"]

    class participatesIn(ObjectProperty):
        domain = [PharmaceuticalCompany]; range = [NegotiationEvent]
        label = ["参与谈判"]; comment = ["制药企业作为谈判方参与医保谈判。"]
    class hasParticipant(ObjectProperty):
        domain = [NegotiationEvent]; range = [PharmaceuticalCompany]
        label = ["谈判参与企业"]; comment = ["参与某次谈判的企业，是 participatesIn 的逆属性。"]
    participatesIn.inverse_property = hasParticipant

    class negotiatedDrug(ObjectProperty):
        domain = [NegotiationEvent]; range = [Drug]
        label = ["谈判药品"]; comment = ["某次谈判涉及的药品。"]
    class negotiatedIn(ObjectProperty):
        domain = [Drug]; range = [NegotiationEvent]
        label = ["经谈判于"]; comment = ["药品参与的谈判事件，是 negotiatedDrug 的逆属性。"]
    negotiatedDrug.inverse_property = negotiatedIn

    class organizedBy(ObjectProperty):
        domain = [NegotiationEvent]; range = [RegulatoryAgency]
        label = ["组织方"]; comment = ["谈判的组织机构。"]
    class organizes(ObjectProperty):
        domain = [RegulatoryAgency]; range = [NegotiationEvent]
        label = ["组织谈判"]; comment = ["机构组织某次谈判，是 organizedBy 的逆属性。"]
    organizedBy.inverse_property = organizes

    class listedIn(ObjectProperty):
        domain = [Drug]; range = [InsuranceListing]
        label = ["纳入目录"]; comment = ["药品被纳入某版医保目录，是推理『谈判成功』的关键属性。"]
    class listsDrug(ObjectProperty):
        domain = [InsuranceListing]; range = [Drug]
        label = ["收录药品"]; comment = ["某版目录收录的药品，是 listedIn 的逆属性。"]
    listedIn.inverse_property = listsDrug

    class coversRegion(ObjectProperty):
        domain = [InsuranceListing]; range = [Region]
        label = ["覆盖地区"]; comment = ["医保目录条目适用的行政区域。"]
    class coveredByListing(ObjectProperty):
        domain = [Region]; range = [InsuranceListing]
        label = ["被目录覆盖"]; comment = ["地区适用的目录条目，是 coversRegion 的逆属性。"]
    coversRegion.inverse_property = coveredByListing

    class hasSubRegion(ObjectProperty, TransitiveProperty):
        domain = [Region]; range = [Region]
        label = ["包含下级地区"]; comment = ["地区之间的包含关系，属性为传递属性，可推出跨层级包含。"]
    class partOfRegion(ObjectProperty, TransitiveProperty):
        domain = [Region]; range = [Region]
        label = ["隶属于地区"]; comment = ["下级地区隶属上级地区，是 hasSubRegion 的逆属性。"]
    hasSubRegion.inverse_property = partOfRegion

    class hasPriceRecord(ObjectProperty):
        domain = [Drug]; range = [PriceRecord]
        label = ["价格记录"]; comment = ["药品对应的价格记录。"]
    class priceOfDrug(ObjectProperty):
        domain = [PriceRecord]; range = [Drug]
        label = ["价格所属药品"]; comment = ["价格记录对应的药品，是 hasPriceRecord 的逆属性。"]
    hasPriceRecord.inverse_property = priceOfDrug

    class supportedBy(ObjectProperty):
        domain = [NegotiationEvent]; range = [Evidence]
        label = ["依据证据"]; comment = ["谈判决策所依据的临床或经济学证据。"]
    class supportsNegotiation(ObjectProperty):
        domain = [Evidence]; range = [NegotiationEvent]
        label = ["支撑谈判"]; comment = ["证据支撑的谈判事件，是 supportedBy 的逆属性。"]
    supportedBy.inverse_property = supportsNegotiation

    class evaluates(ObjectProperty):
        domain = [Evidence]; range = [Drug]
        label = ["评价对象"]; comment = ["证据所评价的药品。"]
    class evaluatedBy(ObjectProperty):
        domain = [Drug]; range = [Evidence]
        label = ["被评价于"]; comment = ["药品被某证据评价，是 evaluates 的逆属性。"]
    evaluates.inverse_property = evaluatedBy

    # ============ 三、数据属性（Data Property）============
    class genericName(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [str]
        label = ["通用名"]; comment = ["药品通用名（INN 中文名）。"]
    class brandName(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [str]
        label = ["商品名"]; comment = ["药品的商品名。"]
    class approvalNumber(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [str]
        label = ["批准文号"]; comment = ["国家药监局批准的药品批准文号。"]
    class dosageForm(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [str]
        label = ["剂型"]; comment = ["注射剂、片剂等剂型。"]
    class specification(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [str]
        label = ["规格"]; comment = ["药品最小包装规格。"]
    class annualTreatmentCost(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [float]
        label = ["年治疗费用"]; comment = ["按标准疗程估算的年治疗费用，单位：元。"]
    class isDomestic(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [bool]
        label = ["是否国产"]; comment = ["true 表示国产药品，false 表示进口药品。"]
    class launchYear(DataProperty, FunctionalProperty):
        domain = [Drug]; range = [int]
        label = ["上市年份"]; comment = ["在中国获批上市的年份，如 2018。"]
    class companyType(DataProperty, FunctionalProperty):
        domain = [PharmaceuticalCompany]; range = [str]
        label = ["企业类型"]; comment = ["外资药企、本土创新药企等。"]
    class foundedYear(DataProperty, FunctionalProperty):
        domain = [PharmaceuticalCompany]; range = [int]
        label = ["成立年份"]; comment = ["企业成立年份。"]
    class icdCode(DataProperty, FunctionalProperty):
        domain = [Disease]; range = [str]
        label = ["ICD编码"]; comment = ["ICD-10 疾病分类编码。"]
    class fiveYearSurvivalRate(DataProperty, FunctionalProperty):
        domain = [MalignantTumor]; range = [float]
        label = ["五年生存率"]; comment = ["0~1 之间的比例。"]
    class negotiationYear(DataProperty, FunctionalProperty):
        domain = [NegotiationEvent]; range = [int]
        label = ["谈判年份"]; comment = ["谈判所属公历年份。"]
    class negotiationRound(DataProperty, FunctionalProperty):
        domain = [NationalDrugPriceNegotiation]; range = [int]
        label = ["谈判轮次"]; comment = ["国家医保谈判的轮次序号。"]
    class averagePriceCut(DataProperty, FunctionalProperty):
        domain = [NegotiationEvent]; range = [float]
        label = ["平均降幅"]; comment = ["该次谈判的平均价格降幅，0~1 之间。"]
    class priceBefore(DataProperty, FunctionalProperty):
        domain = [PriceRecord]; range = [float]
        label = ["谈判前价格"]; comment = ["谈判前的价格，单位：元。"]
    class priceAfter(DataProperty, FunctionalProperty):
        domain = [PriceRecord]; range = [float]
        label = ["谈判后价格"]; comment = ["谈判后的价格，单位：元。"]
    class priceCutRate(DataProperty, FunctionalProperty):
        domain = [PriceRecord]; range = [float]
        label = ["价格降幅"]; comment = ["(前-后)/前，0~1 之间。"]
    class effectiveDate(DataProperty, FunctionalProperty):
        domain = [InsuranceListing]; range = [str]
        label = ["生效日期"]; comment = ["目录版本生效日期，格式 YYYY-MM-DD。"]
    class catalogVersion(DataProperty, FunctionalProperty):
        domain = [InsuranceListing]; range = [str]
        label = ["目录版本"]; comment = ["如『2023年版』。"]
    class adminCode(DataProperty, FunctionalProperty):
        domain = [Region]; range = [str]
        label = ["行政区划代码"]; comment = ["国家统计局行政区划代码。"]
    class evidenceLevel(DataProperty, FunctionalProperty):
        domain = [Evidence]; range = [str]
        label = ["证据等级"]; comment = ["如 1a、1b 等循证等级。"]
    class publishYear(DataProperty, FunctionalProperty):
        domain = [Evidence]; range = [int]
        label = ["发表年份"]; comment = ["证据发表或公布年份。"]

    # ============ 四、公理：互斥类（支撑一致性检查）============
    AllDisjoint([Drug, Organization, Disease, NegotiationEvent, InsuranceListing,
                 PriceRecord, Region, Evidence])
    AllDisjoint([ChemotherapeuticAgent, TargetedTherapyAgent,
                 ImmuneCheckpointInhibitor, EndocrineTherapyAgent])
    AllDisjoint([Country, Province, City])

    # ============ 五、定义类（供推理机推断，关键）============
    class NegotiatedDrug(Drug):
        """医保谈判成功药品 ≡ 药品 ∧ ∃纳入目录.医保目录条目"""
        equivalent_to = [Drug & listedIn.some(InsuranceListing)]
        label = ["医保谈判成功药品"]
        comment = ["被定义类：凡纳入了医保目录条目的药品，推理机可自动判定其属于本类。"]
    class FailedNegotiatedDrug(Drug):
        """谈判未成功药品 ≡ 药品 ∧ ∃经谈判于.国家医保药品谈判 ∧ ¬∃纳入目录.医保目录条目"""
        equivalent_to = [Drug & negotiatedIn.some(NationalDrugPriceNegotiation)
                         & Not(listedIn.some(InsuranceListing))]
        label = ["谈判未成功药品"]
        comment = ["被定义类：参加过国家医保谈判但未被纳入任何目录条目的药品。"]
    class LungCancerDrug(AnticancerDrug):
        """肺癌治疗药品 ≡ 抗肿瘤药品 ∧ ∃适用于.非小细胞肺癌（个体在下面创建后补充）"""
        label = ["肺癌治疗药品"]
        comment = ["被定义类：适用于非小细胞肺癌的抗肿瘤药品，推理机可自动归类。"]

    # ============ 六、个体（Individuals / ABox）============
    # 6.1 组织机构
    msd = PharmaceuticalCompany("msd"); msd.label = ["默沙东"]
    msd.companyType = "外资药企"; msd.foundedYear = 1891

    innovent = PharmaceuticalCompany("innovent"); innovent.label = ["信达生物"]
    innovent.companyType = "本土创新药企"; innovent.foundedYear = 2011

    astrazeneca = PharmaceuticalCompany("astrazeneca"); astrazeneca.label = ["阿斯利康"]
    astrazeneca.companyType = "外资药企"; astrazeneca.foundedYear = 1999

    roche = PharmaceuticalCompany("roche"); roche.label = ["罗氏"]
    roche.companyType = "外资药企"; roche.foundedYear = 1896

    hengrui = PharmaceuticalCompany("hengrui"); hengrui.label = ["恒瑞医药"]
    hengrui.companyType = "本土药企"; hengrui.foundedYear = 1970

    nhsa = RegulatoryAgency("nhsa"); nhsa.label = ["国家医疗保障局"]

    # 6.2 疾病
    nsclc = MalignantTumor("nsclc"); nsclc.label = ["非小细胞肺癌"]
    nsclc.icdCode = "C34.9"; nsclc.fiveYearSurvivalRate = 0.26

    breast_cancer = MalignantTumor("breast_cancer"); breast_cancer.label = ["乳腺癌"]
    breast_cancer.icdCode = "C50"; breast_cancer.fiveYearSurvivalRate = 0.83

    crc = MalignantTumor("crc"); crc.label = ["结直肠癌"]
    crc.icdCode = "C18"; crc.fiveYearSurvivalRate = 0.65

    hcc = MalignantTumor("hcc"); hcc.label = ["肝细胞癌"]
    hcc.icdCode = "C22.0"; hcc.fiveYearSurvivalRate = 0.14

    ir_ae = AdverseReaction("ir_ae"); ir_ae.label = ["免疫相关性肺炎"]
    neutropenia = AdverseReaction("neutropenia"); neutropenia.label = ["中性粒细胞减少症"]
    cinv = AdverseReaction("cinv"); cinv.label = ["化疗相关恶心呕吐"]

    # 6.3 药品
    pembrolizumab = ImmuneCheckpointInhibitor("pembrolizumab")
    pembrolizumab.label = ["帕博利珠单抗"]
    pembrolizumab.genericName = "帕博利珠单抗"; pembrolizumab.brandName = "可瑞达"
    pembrolizumab.dosageForm = "注射剂"; pembrolizumab.specification = "100mg/4ml"
    pembrolizumab.annualTreatmentCost = 320000.0; pembrolizumab.isDomestic = False
    pembrolizumab.launchYear = 2018; pembrolizumab.approvalNumber = "国药准字SJ20180019"

    sintilimab = ImmuneCheckpointInhibitor("sintilimab")
    sintilimab.label = ["信迪利单抗"]
    sintilimab.genericName = "信迪利单抗"; sintilimab.brandName = "达伯舒"
    sintilimab.dosageForm = "注射剂"; sintilimab.specification = "100mg/10ml"
    sintilimab.annualTreatmentCost = 98000.0; sintilimab.isDomestic = True
    sintilimab.launchYear = 2018; sintilimab.approvalNumber = "国药准字S20180016"

    osimertinib = TargetedTherapyAgent("osimertinib")
    osimertinib.label = ["奥希替尼"]
    osimertinib.genericName = "奥希替尼"; osimertinib.brandName = "泰瑞沙"
    osimertinib.dosageForm = "片剂"; osimertinib.specification = "80mg"
    osimertinib.annualTreatmentCost = 183600.0; osimertinib.isDomestic = False
    osimertinib.launchYear = 2017; osimertinib.approvalNumber = "国药准字HJ20170150"

    trastuzumab = TargetedTherapyAgent("trastuzumab")
    trastuzumab.label = ["曲妥珠单抗"]
    trastuzumab.genericName = "曲妥珠单抗"; trastuzumab.brandName = "赫赛汀"
    trastuzumab.dosageForm = "注射剂"; trastuzumab.specification = "440mg"
    trastuzumab.annualTreatmentCost = 165000.0; trastuzumab.isDomestic = False
    trastuzumab.launchYear = 2002; trastuzumab.approvalNumber = "国药准字SJ20170046"

    bevacizumab = TargetedTherapyAgent("bevacizumab")
    bevacizumab.label = ["贝伐珠单抗"]
    bevacizumab.genericName = "贝伐珠单抗"; bevacizumab.brandName = "安维汀"
    bevacizumab.dosageForm = "注射剂"; bevacizumab.specification = "100mg/4ml"
    bevacizumab.annualTreatmentCost = 120000.0; bevacizumab.isDomestic = False
    bevacizumab.launchYear = 2010; bevacizumab.approvalNumber = "国药准字SJ20100047"

    pemetrexed = ChemotherapeuticAgent("pemetrexed")
    pemetrexed.label = ["培美曲塞"]
    pemetrexed.genericName = "培美曲塞"; pemetrexed.brandName = "力比泰"
    pemetrexed.dosageForm = "注射剂"; pemetrexed.specification = "500mg"
    pemetrexed.annualTreatmentCost = 60000.0; pemetrexed.isDomestic = True
    pemetrexed.launchYear = 2005; pemetrexed.approvalNumber = "国药准字H20051288"

    paclitaxel_nab = ChemotherapeuticAgent("paclitaxel_nab")
    paclitaxel_nab.label = ["白蛋白结合型紫杉醇"]
    paclitaxel_nab.genericName = "白蛋白结合型紫杉醇"; paclitaxel_nab.brandName = "艾越"
    paclitaxel_nab.dosageForm = "注射剂"; paclitaxel_nab.specification = "100mg"
    paclitaxel_nab.annualTreatmentCost = 72000.0; paclitaxel_nab.isDomestic = True
    paclitaxel_nab.launchYear = 2018; paclitaxel_nab.approvalNumber = "国药准字H20183044"

    palonosetron = SupportiveCareDrug("palonosetron")
    palonosetron.label = ["帕洛诺司琼"]
    palonosetron.genericName = "帕洛诺司琼"; palonosetron.brandName = "诺威"
    palonosetron.dosageForm = "注射剂"; palonosetron.specification = "0.25mg"
    palonosetron.annualTreatmentCost = 6000.0; palonosetron.isDomestic = True
    palonosetron.launchYear = 2008; palonosetron.approvalNumber = "国药准字H20080776"

    # 6.4 谈判事件 / 目录 / 价格记录 / 证据
    neg2023 = NationalDrugPriceNegotiation("neg2023")
    neg2023.label = ["2023年国家医保药品目录谈判"]
    neg2023.negotiationYear = 2023; neg2023.negotiationRound = 6
    neg2023.averagePriceCut = 0.615

    neg2024 = NationalDrugPriceNegotiation("neg2024")
    neg2024.label = ["2024年国家医保药品目录谈判"]
    neg2024.negotiationYear = 2024; neg2024.negotiationRound = 7
    neg2024.averagePriceCut = 0.63

    vbp5 = VolumeBasedProcurement("vbp5")
    vbp5.label = ["第五批国家组织药品集中带量采购"]
    vbp5.negotiationYear = 2021; vbp5.averagePriceCut = 0.56

    list2023 = InsuranceListing("list2023"); list2023.label = ["2023年版国家医保药品目录"]
    list2023.catalogVersion = "2023年版"; list2023.effectiveDate = "2023-03-01"

    list2024 = InsuranceListing("list2024"); list2024.label = ["2024年版国家医保药品目录"]
    list2024.catalogVersion = "2024年版"; list2024.effectiveDate = "2024-01-01"

    pr_osi = PriceRecord("pr_osi"); pr_osi.label = ["奥希替尼2017年谈判价格记录"]
    pr_osi.priceBefore = 51000.0; pr_osi.priceAfter = 15300.0; pr_osi.priceCutRate = 0.70

    pr_sin = PriceRecord("pr_sin"); pr_sin.label = ["信迪利单抗2019年谈判价格记录"]
    pr_sin.priceBefore = 7838.0; pr_sin.priceAfter = 2843.0; pr_sin.priceCutRate = 0.637

    pr_tras = PriceRecord("pr_tras"); pr_tras.label = ["曲妥珠单抗2017年谈判价格记录"]
    pr_tras.priceBefore = 24500.0; pr_tras.priceAfter = 7600.0; pr_tras.priceCutRate = 0.69

    pr_bev = PriceRecord("pr_bev"); pr_bev.label = ["贝伐珠单抗2017年谈判价格记录"]
    pr_bev.priceBefore = 5210.0; pr_bev.priceAfter = 1998.0; pr_bev.priceCutRate = 0.616

    ct_keynote189 = ClinicalTrial("ct_keynote189")
    ct_keynote189.label = ["KEYNOTE-189 临床试验"]
    ct_keynote189.evidenceLevel = "1a"; ct_keynote189.publishYear = 2018

    ct_orient11 = ClinicalTrial("ct_orient11")
    ct_orient11.label = ["ORIENT-11 临床试验"]
    ct_orient11.evidenceLevel = "1b"; ct_orient11.publishYear = 2020

    pe_sin = PharmacoeconomicEvaluation("pe_sin")
    pe_sin.label = ["信迪利单抗药物经济学评价"]
    pe_sin.evidenceLevel = "模型研究"; pe_sin.publishYear = 2023

    # 6.5 地区
    china = Country("china"); china.label = ["中国"]; china.adminCode = "100000"
    guangdong = Province("guangdong"); guangdong.label = ["广东省"]; guangdong.adminCode = "440000"
    guangzhou = City("guangzhou"); guangzhou.label = ["广州市"]; guangzhou.adminCode = "440100"
    beijing = City("beijing"); beijing.label = ["北京市"]; beijing.adminCode = "110000"
    shanghai = City("shanghai"); shanghai.label = ["上海市"]; shanghai.adminCode = "310000"

    # ============ 七、对象属性断言（关系实例）============
    # 生产关系
    pembrolizumab.manufacturedBy.append(msd)
    sintilimab.manufacturedBy.append(innovent)
    osimertinib.manufacturedBy.append(astrazeneca)
    trastuzumab.manufacturedBy.append(roche)
    bevacizumab.manufacturedBy.append(roche)
    pemetrexed.manufacturedBy.append(hengrui)
    paclitaxel_nab.manufacturedBy.append(hengrui)

    # 适应症
    pembrolizumab.indicatedFor.append(nsclc)
    sintilimab.indicatedFor.append(nsclc)
    osimertinib.indicatedFor.append(nsclc)
    trastuzumab.indicatedFor.append(breast_cancer)
    bevacizumab.indicatedFor.append(crc)
    bevacizumab.indicatedFor.append(hcc)
    pemetrexed.indicatedFor.append(nsclc)
    paclitaxel_nab.indicatedFor.append(breast_cancer)

    # 不良反应
    pembrolizumab.causesAdverseReaction.append(ir_ae)
    sintilimab.causesAdverseReaction.append(ir_ae)
    osimertinib.causesAdverseReaction.append(neutropenia)
    pemetrexed.causesAdverseReaction.append(neutropenia)
    pemetrexed.causesAdverseReaction.append(cinv)
    paclitaxel_nab.causesAdverseReaction.append(neutropenia)
    palonosetron.treats.append(cinv)

    # 联合用药（对称属性）
    pembrolizumab.combinedWith.append(pemetrexed)
    trastuzumab.combinedWith.append(paclitaxel_nab)

    # 谈判关系
    neg2023.organizedBy.append(nhsa)
    neg2024.organizedBy.append(nhsa)
    vbp5.organizedBy.append(nhsa)

    for d in (sintilimab, osimertinib, trastuzumab, bevacizumab, pembrolizumab):
        neg2023.negotiatedDrug.append(d)
    neg2024.negotiatedDrug.append(pembrolizumab)
    neg2023.hasParticipant.append(msd)
    neg2023.hasParticipant.append(innovent)
    neg2023.hasParticipant.append(astrazeneca)
    neg2023.hasParticipant.append(roche)

    # 目录纳入（决定"谈判成功"推理结果）
    for d in (sintilimab, osimertinib, trastuzumab, bevacizumab):
        d.listedIn.append(list2023)
    # 帕博利珠单抗刻意不纳入任何目录 -> 应被推理为"谈判未成功药品"

    list2023.coversRegion.append(china)
    list2024.coversRegion.append(china)

    # 价格记录
    osimertinib.hasPriceRecord.append(pr_osi)
    sintilimab.hasPriceRecord.append(pr_sin)
    trastuzumab.hasPriceRecord.append(pr_tras)
    bevacizumab.hasPriceRecord.append(pr_bev)

    # 证据
    neg2023.supportedBy.append(ct_keynote189)
    neg2023.supportedBy.append(ct_orient11)
    neg2023.supportedBy.append(pe_sin)
    ct_keynote189.evaluates.append(pembrolizumab)
    ct_orient11.evaluates.append(sintilimab)
    pe_sin.evaluates.append(sintilimab)

    # 地区层级（传递属性推理的基础）
    guangzhou.partOfRegion.append(guangdong)
    guangdong.partOfRegion.append(china)
    beijing.partOfRegion.append(china)
    shanghai.partOfRegion.append(china)

    # 补全定义类"肺癌治疗药品"的等价定义（oneOf 名义类，指向非小细胞肺癌个体）
    LungCancerDrug.equivalent_to = [AnticancerDrug & indicatedFor.some(OneOf([nsclc]))]

    # 个体级闭合公理：明确声明帕博利珠单抗未被任何目录收录。
    # OWL 为开放世界语义，"没有断言"不等于"不存在"，因此用 max 0 基数约束表达这一否定事实，
    # 推理机才能证明 ¬∃纳入目录，从而判定其属于『谈判未成功药品』。
    pembrolizumab.is_a.append(listedIn.max(0, Thing))

    # ============ 八、本体级元数据 ============
    onto.metadata.comment = [
        "《抗肿瘤药品与医保谈判》领域本体：覆盖药品分类、适应症、企业、医保谈判事件、"
        "目录准入、价格记录、地区覆盖与证据支撑等核心概念，含推理机可推断的定义类。"
        "数据为公开报道量级的教学示例，非官方统计口径。"
    ]

print("类数量:", len(list(onto.classes())))
print("对象属性:", len(list(onto.object_properties())))
print("数据属性:", len(list(onto.data_properties())))
print("个体数量:", len(list(onto.individuals())))

onto.save(file=OUT, format="rdfxml")
print("已保存:", OUT)
