import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial'] 
plt.rcParams['axes.unicode_minus'] = False

def plot_kline_with_status_matplotlib(csv_path):
    print(f"开始读取数据: {csv_path}")
    df = pd.read_csv(csv_path, encoding='gbk')
    
    # 转换日期
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 颜色映射
    color_map = {
        'TREND_UP': 'red',
        'TREND_DOWN': 'green',
        'INSIDE': 'blue',
        'OUTSIDE': 'orange',
        'INITIAL': 'gray'
    }
    
    # 只取最后 60 根
    num_bars = 60
    plot_df = df.tail(num_bars).copy().reset_index(drop=True)
    
    # 准备绘图数据
    dates = plot_df['日期']
    opens = plot_df['开盘价(元)']
    closes = plot_df['收盘价(元)']
    highs = plot_df['最高价(元)']
    lows = plot_df['最低价(元)']
    status_list = plot_df['kline_status']
    
    # 创建画布
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 绘制 K 线 (手动绘制)
    width = 0.6  # 柱状图宽度
    width2 = 0.05 # 影线宽度
    
    # 区分涨跌颜色 (这里指单根K线的涨跌，不是 trend 状态)
    up = closes >= opens
    down = closes < opens
    
    # 上涨 红柱 (空心或实心，这里用实心便于观看)
    col_up = 'red'
    col_down = 'green'
    
    # 绘制影线
    ax.bar(plot_df.index[up], highs[up]-lows[up], width2, bottom=lows[up], color=col_up)
    ax.bar(plot_df.index[down], highs[down]-lows[down], width2, bottom=lows[down], color=col_down)
    
    # 绘制实体
    # 也就是 open 到 close 的矩形
    # 高度 = abs(close - open)
    # 底部 = min(open, close)
    heights = (closes - opens).abs()
    bottoms = plot_df[['开盘价(元)', '收盘价(元)']].min(axis=1)
    
    ax.bar(plot_df.index[up], heights[up], width, bottom=bottoms[up], color=col_up)
    ax.bar(plot_df.index[down], heights[down], width, bottom=bottoms[down], color=col_down)
    
    # 设置 X 轴为日期
    # 由于使用 range(len) 作为索引来均匀排列 K 线，我们需要手动设置 tick labels
    # 每隔 5 天显示一个刻度
    step = 5
    ax.set_xticks(range(0, len(plot_df), step))
    ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates[::step]], rotation=45, fontsize=8)
    
    # 添加状态文字
    print("正在标注状态...")
    for i in range(len(plot_df)):
        status = status_list[i]
        high_price = highs[i]
        
        # 颜色
        txt_color = color_map.get(status, 'black')
        
        # 在最高价上方标注
        ax.text(i, high_price * 1.0005, status,
                ha='center', va='bottom',
                rotation=45, fontsize=7, color=txt_color)

    ax.set_title('TL.CFE K-line Status Visualization', fontsize=14)
    ax.set_ylabel('Price (元)')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # 添加图例说明
    legend_text = "状态文字颜色说明:\nTREND_UP(红)=上涨趋势\nTREND_DOWN(绿)=下跌趋势\nINSIDE(蓝)=内含线\nOUTSIDE(橙)=外包线"
    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray'))

    plt.tight_layout()
    plt.show()
    print("图表绘制完成。")

if __name__ == "__main__":
    plot_kline_with_status_matplotlib('TL.CFE_processed.csv')
