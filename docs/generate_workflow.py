"""生成工作流图"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.set_aspect('equal')
ax.axis('off')

# 颜色定义
color_input = '#e3f2fd'    # 浅蓝 - 输入
color_io = '#fff3e0'       # 浅橙 - IO层
color_analysis = '#e8f5e9' # 浅绿 - 分析层
color_output = '#fce4ec'   # 浅粉 - 输出
color_border = '#546e7a'

def draw_box(x, y, w, h, color, title, items=None, title_size=11):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.2",
                         facecolor=color, edgecolor=color_border, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + w/2, y + h - 0.25, title, ha='center', va='top', 
            fontsize=title_size, fontweight='bold')
    if items:
        for i, item in enumerate(items):
            ax.text(x + w/2, y + h - 0.6 - i*0.35, item, ha='center', va='top', 
                    fontsize=9, color='#37474f')

def draw_arrow(x1, y1, x2, y2, color='#78909c'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

# === 绘制模块 ===

# 入口
draw_box(5.5, 9, 3, 0.8, '#fff9c4', '🚀 run_pipeline.py')

# 原始数据
draw_box(1, 7.5, 3, 1.2, color_input, '📂 data/raw/', 
         ['TL.CFE.xlsx'])

# IO 层
draw_box(5, 6.5, 4, 2.2, color_io, '📦 src/io/',
         ['loader.py → load_ohlc()', 
          'schema.py → OHLCData',
          'adapters/ → WindCFEAdapter'])

# Analysis 层
draw_box(5, 3.5, 4, 2.5, color_analysis, '📊 src/analysis/',
         ['process_ohlc.py', 
          'merging.py → K线合并',
          'fractals.py → 分型识别',
          'kline_logic.py'])

# 输出 - CSV
draw_box(1, 0.8, 4, 2, color_output, '📂 data/processed/',
         ['*_processed.csv',
          '*_merged.csv', 
          '*_strokes.csv'])

# 输出 - 图表
draw_box(9, 0.8, 4, 2, color_output, '📂 output/',
         ['*_merged_kline.png',
          '*_strokes.png'])

# === 绘制箭头 ===
# 入口 -> IO
draw_arrow(7, 9, 7, 8.8)

# 原始数据 -> IO
draw_arrow(4, 7.8, 5, 7.6)

# IO -> Analysis
draw_arrow(7, 6.5, 7, 6.1)

# Analysis -> CSV
draw_arrow(5, 4.5, 3, 2.85)

# Analysis -> 图表
draw_arrow(9, 4.5, 11, 2.85)

# 标题
ax.text(7, 9.7, 'K 线分析流水线 - 代码工作流', ha='center', va='center',
        fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('docs/workflow_diagram.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("图表已保存至: docs/workflow_diagram.png")
plt.close()
