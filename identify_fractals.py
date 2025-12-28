import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial'] 
plt.rcParams['axes.unicode_minus'] = False

def identify_and_plot_fractals(input_path, output_path):
    print(f"开始读取已合并的数据: {input_path}")
    df = pd.read_csv(input_path, encoding='gbk')
    
    # 转换为列表字典方便处理
    bars = df.to_dict('records')
    
    if len(bars) < 3:
        print("数据量太少，无法识别分型")
        return

    # 初始化分型列
    fractal_types = [''] * len(bars)
    
    # 遍历每三根相邻 K 线
    # 从第 2 根 (索引1) 开始，到倒数第 2 根 (索引 len-2) 结束
    # 实际上分型判断是对中间那根 (i) 进行判断，需要用到 i-1 和 i+1
    
    fractal_count = 0
    
    for i in range(1, len(bars) - 1):
        prev = bars[i-1]
        curr = bars[i]
        next_bar = bars[i+1]
        
        h_prev, l_prev = prev['最高价(元)'], prev['最低价(元)']
        h_curr, l_curr = curr['最高价(元)'], curr['最低价(元)']
        h_next, l_next = next_bar['最高价(元)'], next_bar['最低价(元)']
        
        # 顶分型: 中间高点最高，且中间低点最高（相对两侧）
        # 注意：经过合并处理后，不应该存在包含关系，所以单纯比较 High 即可
        # 但为了严谨，我们通常要求 High 是凸出的
        is_top_fractal = (h_curr > h_prev) and (h_curr > h_next)
        
        # 底分型: 中间低点最低，且中间高点最低（相对两侧）
        is_bottom_fractal = (l_curr < l_prev) and (l_curr < l_next)
        
        if is_top_fractal:
            fractal_types[i] = 'TOP'
            fractal_count += 1
        elif is_bottom_fractal:
            fractal_types[i] = 'BOTTOM'
            fractal_count += 1
        
        # 思考: 是否存在既是顶分型又是底分型的情况？
        # H > H_prev, H > H_next (凸)
        # L < L_prev, L < L_next (凹)
        # 这种情况通常就是 Outside Bar，但在合并步骤中应该已经被处理掉了。
        # 如果还出现，说明合并逻辑有残留。这里优先标记为 TOP_BOTTOM? 或者 Outside?
        # 我们的合并逻辑已经消灭了包含，所以理论上不会出现这种情况。
            
    df['fractal_type'] = fractal_types
    
    # 保存结果
    df.to_csv(output_path, index=False, encoding='gbk')
    print(f"分型识别完成。共发现 {fractal_count} 个分型点。")
    print(f"结果已保存至: {output_path}")
    
    plot_fractals(df)

def plot_fractals(df):
    print("\n开始绘制带分型的 K 线图...")
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 只取最后 60 根展示
    num_bars = 60
    plot_df = df.tail(num_bars).copy().reset_index(drop=True)
    
    dates = plot_df['日期']
    opens = plot_df['开盘价(元)']
    closes = plot_df['收盘价(元)']
    highs = plot_df['最高价(元)']
    lows = plot_df['最低价(元)']
    fractals = plot_df['fractal_type']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    width = 0.6
    width2 = 0.05
    
    up = closes >= opens
    down = closes < opens
    
    col_up = 'red'
    col_down = 'green'
    
    # 绘制 K 线
    ax.bar(plot_df.index[up], highs[up]-lows[up], width2, bottom=lows[up], color=col_up)
    ax.bar(plot_df.index[down], highs[down]-lows[down], width2, bottom=lows[down], color=col_down)
    ax.bar(plot_df.index[up], (closes[up]-opens[up]).abs(), width, bottom=opens[up], color=col_up)
    ax.bar(plot_df.index[down], (closes[down]-opens[down]).abs(), width, bottom=closes[down], color=col_down)
    
    # 标注分型
    for i in range(len(plot_df)):
        f_type = fractals[i]
        if f_type == 'TOP':
            # 在最高价上方画向下箭头 v
            ax.annotate('Top', 
                        xy=(i, highs[i]), 
                        xytext=(i, highs[i] * 1.0015),
                        arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                        ha='center', fontsize=8)
        elif f_type == 'BOTTOM':
            # 在最低价下方画向上箭头 ^
            ax.annotate('Bot', 
                        xy=(i, lows[i]), 
                        xytext=(i, lows[i] * 0.9985),
                        arrowprops=dict(facecolor='blue', shrink=0.05, width=1, headwidth=5),
                        ha='center', va='top', fontsize=8, color='blue')
    
    # 设置 X 轴
    step = 5
    ax.set_xticks(range(0, len(plot_df), step))
    ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates[::step]], rotation=45, fontsize=8)
    
    ax.set_title('Fractal Identification (Based on Merged Bars)', fontsize=14)
    ax.set_ylabel('Price (元)')
    
    legend_text = "标注说明:\nTop (黑箭头) = 顶分型\nBot (蓝箭头) = 底分型"
    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    identify_and_plot_fractals('TL.CFE_merged.csv', 'TL.CFE_fractals.csv')
