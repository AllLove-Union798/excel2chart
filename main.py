import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rcParams
from matplotlib.font_manager import FontProperties
import os
import ternary
df = pd.read_excel('demo.xlsx',header=1)
# print(df)
# 提取所有温度值并去重，获取要绘制的温度列表
if not os.path.exists('output'):
    os.makedirs('output')
font_path = "font/SimHei.ttf"
my_font = FontProperties(fname=font_path, size=12)
my_font2 = font_manager.FontProperties(fname=r"font/SimHei.ttf")
rcParams['font.family'] = my_font2.get_name()
rcParams['axes.unicode_minus'] = False
df['温度/℃'] = df['温度/℃'].ffill()
temperatures = df[f'温度/℃'].dropna().unique()
colors = plt.cm.rainbow(np.linspace(0, 1, len(temperatures)))
# 遍历每个温度，绘制对应相图
for temp in temperatures:
    # 筛选出当前温度下的数据
    # print(f"temp {temp}")
    temp_data = df[df['温度/℃'] == temp]
    # 提取绘制所需的数据列
    NaCl = temp_data['液相NaCl/%'].tolist()
    KCl = temp_data['液相KCl/%'].tolist()
    phases = temp_data['固相'].tolist()
    # print(f"NaCl {NaCl}")
    # print(f"KCl {KCl}")
    # 寻找共饱点（固相为'NaCl+KCl'的数据行）
    eutectic_row = temp_data[temp_data['固相'] == 'NaCl+KCl']
    if not eutectic_row.empty:
        eutectic_point = (eutectic_row['液相NaCl/%'].values[0],
                          eutectic_row['液相KCl/%'].values[0])
    else:
        eutectic_point = None  # 若没有共饱点，后续不绘制对应斜线

    # 创建新的图形窗口
    plt.figure()

    # 绘制三角形边界（按相图逻辑：左竖边、右斜边、底边 ）
    plt.plot([0, 0], [0, 100], 'k-')  # 左竖边
    plt.plot([0, 100], [100, 0], 'k-')  # 右斜边
    plt.plot([0, 100], [0, 0], 'k-')  # 底边

    # 如果有共饱点，绘制从共饱点引出的两条斜线
    if eutectic_point[0] is not None and eutectic_point[1] is not None:
        plt.plot([eutectic_point[0], 0], [eutectic_point[1], 100], 'k-')
        plt.plot([eutectic_point[0], 100], [eutectic_point[1], 0], 'k-')

        # 标注区域：根据共饱点位置确定标注位置
        # NaCl区域标注（共饱点左上方）
        nacl_label_x = 6.5
        nacl_label_y = 42
        plt.text(nacl_label_x, nacl_label_y, 'NaCl', fontsize=9,
                 )

        # KCl区域标注（共饱点右下方）
        kcl_label_x = 39.5
        kcl_label_y =1.7
        plt.text(kcl_label_x, kcl_label_y, 'KCl', fontsize=9,
                 )

        # 绘制数据点（蓝色圆点连线）
    plt.plot(NaCl, KCl, 'o-', color='blue')

    # 设置坐标轴范围与标题
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.title(f"{temp}℃", fontsize=16)

    # 显示图形
    save_path = f"output/{temp}℃相图.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()  # 关闭当前图形，释放内存
    print(f"已保存: {save_path}")

# 第二部分：创建整合所有温度曲线的图形
plt.figure(figsize=(10, 8))

# 绘制三角形边界
plt.plot([0, 0], [0, 100], 'k-')  # 左竖边
plt.plot([0, 100], [100, 0], 'k-')  # 右斜边
plt.plot([0, 100], [0, 0], 'k-')  # 底边

# 遍历每个温度，在整合图中绘制曲线和对应的斜线
for i, temp in enumerate(temperatures):
    # 筛选出当前温度下的数据
    temp_data = df[df['温度/℃'] == temp]

    # 提取绘制所需的数据列
    NaCl = temp_data['液相NaCl/%'].tolist()
    KCl = temp_data['液相KCl/%'].tolist()

    # 寻找共饱点
    eutectic_row = temp_data[temp_data['固相'] == 'NaCl+KCl']
    if not eutectic_row.empty:
        eutectic_point = (eutectic_row['液相NaCl/%'].values[0],
                          eutectic_row['液相KCl/%'].values[0])
    else:
        eutectic_point = None

    # 如果有共饱点，绘制从共饱点引出的两条斜线，使用与曲线相同的颜色
    if eutectic_point and eutectic_point[0] is not None and eutectic_point[1] is not None:
        plt.plot([eutectic_point[0], 0], [eutectic_point[1], 100], '-',
                 color=colors[i], alpha=0.7, linewidth=1.5)
        plt.plot([eutectic_point[0], 100], [eutectic_point[1], 0], '-',
                 color=colors[i], alpha=0.7, linewidth=1.5)

    # 绘制数据点（使用对应温度的颜色），添加标签用于图例
    plt.plot(NaCl, KCl, 'o-', color=colors[i], label=f'{temp}℃',
             linewidth=2, markersize=6)

# 标注区域
plt.text(6.5, 42, 'NaCl', fontsize=12, fontweight='bold')
plt.text(39.5, 1.7, 'KCl', fontsize=12, fontweight='bold')

# 设置坐标轴范围与标题
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.title('不同温度下的相图曲线整合',fontproperties=my_font, fontsize=16, fontweight='bold')

# 添加坐标轴标签
plt.xlabel('液相NaCl/%',fontproperties=my_font, fontsize=12)
plt.ylabel('液相KCl/%', fontproperties=my_font,fontsize=12)

# 添加图例，标明不同温度曲线
plt.legend(title='温度', title_fontproperties=my_font,
           prop=my_font, fontsize=10, loc='best')

# 添加网格线
plt.grid(True, alpha=0.3, linestyle='--')

# 调整布局
plt.tight_layout()

# 显示整合图形
integrated_save_path = "output/不同温度下的相图曲线整合.png"
plt.savefig(integrated_save_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"已保存: {integrated_save_path}")


# 设置绘图
scale = 100
fig, tax = ternary.figure(scale=scale)
fig.set_size_inches(8, 7)

# 三角边框和网格
tax.boundary(linewidth=1.5)
tax.gridlines(multiple=25, color="gray", linewidth=0.7, alpha=0.5)
tax.ticks(axis='lbr', multiple=25, linewidth=1, fontsize=9)

# 顶点标注（旋转后合理的位置）
fontsize = 14
tax.annotate("w(KCl)", (0, 0, scale), ha='center', va='bottom', fontsize=fontsize, fontweight="bold")  # 左下
tax.annotate("w(H$_2$O)", (0, scale, 0), ha='right', va='top', fontsize=fontsize, fontweight="bold")     # 上顶点
tax.annotate("w(NaCl)", (scale, 0, 0), ha='left', va='top', fontsize=fontsize, fontweight="bold")     # 右下

# 去掉默认的边标签
tax.clear_matplotlib_ticks()
tax.get_axes().axis('off')

# 遍历每个温度绘制曲线
for i, temp in enumerate(temperatures):
    temp_data = df[df['温度/℃'] == temp]
    NaCl = temp_data['液相NaCl/%'].tolist()
    KCl = temp_data['液相KCl/%'].tolist()
    H2O  = [100 - n - k for n, k in zip(NaCl, KCl)]

    # 转换为三元相 (NaCl, KCl, H2O)
    points = list(zip(NaCl, H2O,KCl ))

    # 绘制主线
    tax.plot(points, linewidth=2, marker='o', color=colors[i], label=f"{temp}℃")

    # ===== 共饱点辅助线 =====
    eutectic_row = temp_data[temp_data['固相'] == 'NaCl+KCl']
    if not eutectic_row.empty:
        eNaCl = eutectic_row['液相NaCl/%'].values[0]
        eKCl  = eutectic_row['液相KCl/%'].values[0]
        eH2O  = 100 - eNaCl - eKCl
        eutectic = (eNaCl,eH2O , eKCl)
        tax.scatter([eutectic], marker='o', color=colors[i], s=40)

        # 从共饱点连向 NaCl 顶点
        tax.line(eutectic, (100,0,0), linewidth=1, color=colors[i], alpha=0.7)
        # 从共饱点连向 KCl 顶点
        tax.line(eutectic, (0,0,100), linewidth=1, color=colors[i], alpha=0.7)

# 添加图例
tax.legend(title="温度",fontsize=9)

# 去掉外框白边
tax.clear_matplotlib_ticks()
tax.get_axes().axis('off')

plt.tight_layout()
# plt.show()
plt.savefig("output/三元相图_含刻度.png", dpi=300, bbox_inches="tight")
plt.close()
print("已保存: output/三元相图_含刻度.png")
