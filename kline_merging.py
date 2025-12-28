import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial'] 
plt.rcParams['axes.unicode_minus'] = False

def get_initial_trend(bars):
    """
    向后扫描直到找到明确的趋势方向
    """
    for i in range(1, len(bars)):
        prev = bars[i-1]
        curr = bars[i]
        
        h_prev, l_prev = prev['最高价(元)'], prev['最低价(元)']
        h_curr, l_curr = curr['最高价(元)'], curr['最低价(元)']
        
        # 排除包含关系
        is_inside = (h_curr <= h_prev) and (l_curr >= l_prev)
        is_outside = (h_curr >= h_prev) and (l_curr <= l_prev)
        
        if not is_inside and not is_outside:
            if h_curr > h_prev and l_curr > l_prev:
                return 1 # UP
            elif h_curr < h_prev and l_curr < l_prev:
                return -1 # DOWN
    return 1 # 默认向上，如果全都是包含关系（极不可能）

def apply_kline_merging(input_path, output_path, save_plot_path=None):
    print(f"开始读取数据: {input_path}")
    df = pd.read_csv(input_path, encoding='gbk')
    
    raw_bars = df.to_dict('records')
    if not raw_bars:
        return

    merged_bars = []
    
    # 预先确定初始趋势，解决开头就是包含关系导致的无法合并问题
    current_trend = get_initial_trend(raw_bars)
    print(f"初始趋势判定为: {'上涨' if current_trend==1 else '下跌'}")
    
    merged_bars.append(raw_bars[0].copy()) # 使用副本以免修改原始数据
    
    merge_count = 0
    
    i = 1
    while i < len(raw_bars):
        curr = raw_bars[i].copy()
        prev = merged_bars[-1] # 这里引用的是列表中的对象，修改它会直接生效
        
        h_curr, l_curr = curr['最高价(元)'], curr['最低价(元)']
        h_prev, l_prev = prev['最高价(元)'], prev['最低价(元)']
        
        is_inside = (h_curr <= h_prev) and (l_curr >= l_prev)
        is_outside = (h_curr >= h_prev) and (l_curr <= l_prev)
        
        # 只要存在包含关系，就根据当前趋势进行合并
        if is_inside or is_outside:
            if current_trend == 1:
                # Up Trend: 取高点中的高点，低点中的高点
                new_high = max(h_prev, h_curr)
                new_low = max(l_prev, l_curr)
            else:
                # Down Trend: 取高点中的低点，低点中的低点
                new_high = min(h_prev, h_curr)
                new_low = min(l_prev, l_curr)
                
            # 原地更新 prev
            prev['最高价(元)'] = new_high
            prev['最低价(元)'] = new_low
            prev['收盘价(元)'] = curr['收盘价(元)']
            prev['日期'] = curr['日期'] 
            prev['kline_status'] = f"MERGED" 
            
            merge_count += 1
            # i 增加，下一轮循环将用新的 prev (即刚刚合并后的结果) 与 raw_bars[i+1] 对比
            # 这就实现了向右的递归合并
            i += 1
        
        else:
            # 无包含关系，更新趋势
            if h_curr > h_prev and l_curr > l_prev:
                current_trend = 1
            elif h_curr < h_prev and l_curr < l_prev:
                current_trend = -1
            
            merged_bars.append(curr)
            i += 1

    # --- 新增步骤：重新计算合并后的 K 线状态 ---
    print("正在重新计算合并后的 K 线状态...")
    merged_bars[0]['kline_status'] = 'INITIAL'
    
    for i in range(1, len(merged_bars)):
        curr = merged_bars[i]
        prev = merged_bars[i-1]
        
        h_curr, l_curr = curr['最高价(元)'], curr['最低价(元)']
        h_prev, l_prev = prev['最高价(元)'], prev['最低价(元)']
        
        if h_curr > h_prev and l_curr > l_prev:
            status = 'TREND_UP'
        elif h_curr < h_prev and l_curr < l_prev:
            status = 'TREND_DOWN'
        else:
            # 理论上合并后不应存在 INSIDE/OUTSIDE，除非极其罕见的完全重合或者是逻辑漏洞
            # 这里统一标记为 MIXED 以示区别，或者通过上下影线判断
            status = 'MIXED'
        
        # 保留合并标记
        if "MERGED" in curr.get('kline_status', ''):
            curr['kline_status'] = status + "_(M)"
        else:
            curr['kline_status'] = status

    # 输出结果
    result_df = pd.DataFrame(merged_bars)
    result_df.to_csv(output_path, index=False, encoding='gbk')
    print(f"合并完成。次数: {merge_count}")
    
    plot_merged_kline(result_df, save_plot_path)

def plot_merged_kline(df, save_path=None):
    print("\n开始绘制合并后的 K 线图...")
    df['日期'] = pd.to_datetime(df['日期'])
    
    num_bars = 60
    plot_df = df.tail(num_bars).copy().reset_index(drop=True)
    
    dates = plot_df['日期']
    opens = plot_df['开盘价(元)']
    closes = plot_df['收盘价(元)']
    highs = plot_df['最高价(元)']
    lows = plot_df['最低价(元)']
    status_list = plot_df['kline_status']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    width = 0.6
    width2 = 0.05
    
    up = closes >= opens
    down = closes < opens
    
    col_up = 'red'
    col_down = 'green'
    
    ax.bar(plot_df.index[up], highs[up]-lows[up], width2, bottom=lows[up], color=col_up)
    ax.bar(plot_df.index[down], highs[down]-lows[down], width2, bottom=lows[down], color=col_down)
    
    heights = (closes - opens).abs()
    bottoms = plot_df[['开盘价(元)', '收盘价(元)']].min(axis=1)
    
    ax.bar(plot_df.index[up], heights[up], width, bottom=bottoms[up], color=col_up)
    ax.bar(plot_df.index[down], heights[down], width, bottom=bottoms[down], color=col_down)
    
    step = 5
    ax.set_xticks(range(0, len(plot_df), step))
    ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates[::step]], rotation=45, fontsize=8)
    
    for i in range(len(plot_df)):
        status = str(status_list[i])
        if "(M)" in status:
             ax.text(i, highs[i] * 1.0005, "M", 
                ha='center', va='bottom',
                rotation=0, fontsize=8, color='purple', fontweight='bold')
    
    ax.set_title('Merged K-line Visualization (Recursive)', fontsize=14)
    ax.set_ylabel('Price (元)')
    ax.text(0.02, 0.98, "标注说明:\nM = 合并K线", transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"图表已保存至: {save_path}")
        plt.close()
    else:
        plt.show()

if __name__ == "__main__":
    apply_kline_merging('TL.CFE_processed.csv', 'TL.CFE_merged.csv')
