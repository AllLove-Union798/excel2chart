import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rcParams
from matplotlib.font_manager import FontProperties
import os
import ternary

# ========== 读取数据 ==========
df = pd.read_excel('docs/demo.xlsx', header=1)

# 保证温度列没有缺失
df['温度/℃'] = df['温度/℃'].ffill()
temperatures = df['温度/℃'].dropna().unique()

# 创建输出目录
os.makedirs('output', exist_ok=True)

# 设置字体
font_path = "font/SimHei.ttf"
my_font = FontProperties(fname=font_path, size=12)
rcParams['font.family'] = my_font.get_name()
rcParams['axes.unicode_minus'] = False

# 配色
colors = plt.cm.rainbow(np.linspace(0, 1, len(temperatures)))

# ========== 数据预处理：一次循环，存储所有温度的数据 ==========
all_data = {}
for i, temp in enumerate(temperatures):
    temp_data = df[df['温度/℃'] == temp]
    NaCl = temp_data['液相NaCl/%'].tolist()
    KCl = temp_data['液相KCl/%'].tolist()
    H2O = [100 - n - k for n, k in zip(NaCl, KCl)]

    # 共饱点
    eutectic_row = temp_data[temp_data['固相'] == 'NaCl+KCl']
    eutectic = None
    if not eutectic_row.empty:
        eNaCl = eutectic_row['液相NaCl/%'].values[0]
        eKCl  = eutectic_row['液相KCl/%'].values[0]
        eH2O  = 100 - eNaCl - eKCl
        eutectic = (eNaCl, eKCl, eH2O)

    all_data[temp] = {
        "NaCl": NaCl,
        "KCl": KCl,
        "H2O": H2O,
        "points": list(zip(NaCl, KCl, H2O)),
        "eutectic": eutectic,
        "color": colors[i]
    }

# ========== Part 1: 单温度二维相图 ==========
for temp, data in all_data.items():
    plt.figure()

    # 三角形边界
    plt.plot([0, 0], [0, 100], 'k-')
    plt.plot([0, 100], [100, 0], 'k-')
    plt.plot([0, 100], [0, 0], 'k-')

    # 共饱点辅助线
    if data["eutectic"]:
        eNaCl, eKCl, _ = data["eutectic"]
        plt.plot([eNaCl, 0], [eKCl, 100], 'k-')
        plt.plot([eNaCl, 100], [eKCl, 0], 'k-')
        plt.text(6.5, 42, 'NaCl', fontsize=9)
        plt.text(39.5, 1.7, 'KCl', fontsize=9)

    # 数据点
    plt.plot(data["NaCl"], data["KCl"], 'o-', color='blue')

    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.title(f"{temp}℃", fontsize=16)

    save_path = f"output/{temp}℃相图.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"已保存: {save_path}")

# ========== Part 2: 整合二维相图 ==========
plt.figure(figsize=(10, 8))
plt.plot([0, 0], [0, 100], 'k-')
plt.plot([0, 100], [100, 0], 'k-')
plt.plot([0, 100], [0, 0], 'k-')

for temp, data in all_data.items():
    if data["eutectic"]:
        eNaCl, eKCl, _ = data["eutectic"]
        plt.plot([eNaCl, 0], [eKCl, 100], '-', color=data["color"], alpha=0.7)
        plt.plot([eNaCl, 100], [eKCl, 0], '-', color=data["color"], alpha=0.7)

    plt.plot(data["NaCl"], data["KCl"], 'o-', color=data["color"],
             label=f'{temp}℃', linewidth=2, markersize=6)

plt.text(6.5, 42, 'NaCl', fontsize=12, fontweight='bold')
plt.text(39.5, 1.7, 'KCl', fontsize=12, fontweight='bold')
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.title('不同温度下的相图曲线整合', fontproperties=my_font, fontsize=16, fontweight='bold')
plt.xlabel('液相NaCl/%', fontproperties=my_font, fontsize=12)
plt.ylabel('液相KCl/%', fontproperties=my_font, fontsize=12)
plt.legend(title='温度', title_fontproperties=my_font, prop=my_font, fontsize=10, loc='best')
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()

integrated_save_path = "output/不同温度下的相图曲线整合.png"
plt.savefig(integrated_save_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"已保存: {integrated_save_path}")

# ========== Part 3: 三元相图 ==========
scale = 100
fig, tax = ternary.figure(scale=scale)
fig.set_size_inches(8, 7)

tax.boundary(linewidth=1.5)
tax.gridlines(multiple=25, color="gray", linewidth=0.7, alpha=0.5)
tax.ticks(axis='lbr', multiple=25, linewidth=1, fontsize=9)

fontsize = 14
tax.annotate("w(KCl)", (0, 0, scale), ha='center', va='bottom', fontsize=fontsize, fontweight="bold")
tax.annotate("w(H$_2$O)", (0, scale, 0), ha='right', va='top', fontsize=fontsize, fontweight="bold")
tax.annotate("w(NaCl)", (scale, 0, 0), ha='left', va='top', fontsize=fontsize, fontweight="bold")

tax.clear_matplotlib_ticks()
tax.get_axes().axis('off')

for temp, data in all_data.items():
    tax.plot(data["points"], linewidth=2, marker='o', color=data["color"], label=f"{temp}℃")
    if data["eutectic"]:
        tax.scatter([data["eutectic"]], marker='o', color=data["color"], s=40)
        tax.line(data["eutectic"], (100,0,0), linewidth=1, color=data["color"], alpha=0.7)
        tax.line(data["eutectic"], (0,100,0), linewidth=1, color=data["color"], alpha=0.7)

tax.legend(title="温度", fontsize=9)
plt.tight_layout()
plt.savefig("output/三元相图_含刻度.png", dpi=300, bbox_inches="tight")
plt.close()
print("已保存: output/三元相图_含刻度.png")
