# -*- coding: utf-8 -*-
"""从本体自动抽取结构，绘制类层次结构图。"""
import os, io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from owlready2 import get_ontology

HERE = os.path.dirname(os.path.abspath(__file__))
OWL = os.path.join(HERE, "..", "ontology", "anticancer-drug-insurance.owl")
OUT = os.path.join(HERE, "concept_structure.png")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False

onto = get_ontology(os.path.abspath(OWL)).load()

DEFINED = {"NegotiatedDrug", "FailedNegotiatedDrug", "LungCancerDrug"}
classes = [c for c in onto.classes() if c.name not in DEFINED and hasattr(c, "name")]

def label(c):
    return c.label[0] if c.label else c.name

def children(c):
    return sorted([s for s in c.subclasses() if s.name not in DEFINED],
                  key=lambda x: label(x))

names = {c.name for c in classes}

def parents_of(c):
    return [p for p in c.is_a if hasattr(p, "name") and getattr(p, "name", None) in names]

# 顶层类：没有本体内的父类
top = sorted([c for c in classes if not parents_of(c)], key=lambda x: label(x))

# 布局：纸张从左到右生长
LEVEL_H = 0.62          # 每个叶节点的垂直高度
BOX_W, BOX_H = 1.55, 0.42
GAP_X = 0.55
positions = {}
_counter = [0]

def layout(node, depth):
    kids = children(node)
    if not kids:
        y = _counter[0] * LEVEL_H
        _counter[0] += 1
        positions[node.name] = (depth, y)
        return y
    ys = [layout(k, depth + 1) for k in kids]
    y = (ys[0] + ys[-1]) / 2
    positions[node.name] = (depth, y)
    return y

for t in top:
    layout(t, 0)
    _counter[0] += 0.35        # 顶层分支之间留空隙

max_y = max(y for _, y in positions.values())
max_d = max(d for d, _ in positions.values())

fig_w = (max_d + 1) * (BOX_W + GAP_X) + 1.6
fig_h = (max_y / LEVEL_H + 1) * LEVEL_H + 1.2
fig, ax = plt.subplots(figsize=(fig_w, fig_h))
ax.set_xlim(-0.3, (max_d + 1) * (BOX_W + GAP_X) + 0.3)
ax.set_ylim(-0.7, max_y + 0.7)
ax.axis("off")

DEPTH_COLORS = ["#1f4e79", "#2e75b6", "#4a90c2", "#7fb0d4"]
def color_for(d):
    return DEPTH_COLORS[min(d, len(DEPTH_COLORS) - 1)]

# 先画连线
for c in classes:
    d, y = positions[c.name]
    for s in children(c):
        ds, ys = positions[s.name]
        x1 = d * (BOX_W + GAP_X) + BOX_W
        x2 = ds * (BOX_W + GAP_X)
        ax.plot([x1, x1 + 0.18, x1 + 0.18, x2], [y, y, ys, ys],
                color="#b0b7bf", lw=1.0, zorder=1, solid_capstyle="round")

# 再画节点
for c in classes:
    d, y = positions[c.name]
    x = d * (BOX_W + GAP_X)
    col = color_for(d)
    box = FancyBboxPatch((x, y - BOX_H / 2), BOX_W, BOX_H,
                         boxstyle="round,pad=0.02,rounding_size=0.08",
                         linewidth=1.2, edgecolor=col,
                         facecolor=col if d == 0 else "white", zorder=3)
    ax.add_patch(box)
    ax.text(x + BOX_W / 2, y + (0.07 if c.name != label(c) else 0),
            label(c), ha="center", va="center", fontsize=9.5 if d < 2 else 8.8,
            color="white" if d == 0 else "#1f2937", zorder=4,
            fontweight="bold" if d == 0 else "normal")
    ax.text(x + BOX_W / 2, y - 0.115, c.name, ha="center", va="center",
            fontsize=6.4, color="#cfe2f3" if d == 0 else "#8a94a0", zorder=4,
            style="italic")

ax.set_title("《抗肿瘤药品与医保谈判》本体类层次结构图",
             fontsize=16, pad=16, color="#1f2937", fontweight="bold")
plt.tight_layout()
plt.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print("已生成:", OUT, os.path.getsize(OUT) // 1024, "KB")
