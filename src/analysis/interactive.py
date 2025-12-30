import plotly.graph_objects as go
import pandas as pd
from typing import List, Tuple

def plot_interactive_kline(df: pd.DataFrame, 
                         strokes: List[Tuple[int, str]], 
                         save_path: str = None):
    """
    绘制交互式 K 线图 (Plotly)
    
    Args:
        df: 包含 datetime, open, high, low, close 的 DataFrame
        strokes: 分型标记 list of (index, type)，如 [(10, 'T'), (15, 'B')]
        save_path: HTML 保存路径
    """
    
    #构造 Hover Text
    hover_text = [
        f"时间: {d.strftime('%Y-%m-%d')}<br>O: {o:.2f}<br>H: {h:.2f}<br>L: {l:.2f}<br>C: {c:.2f}"
        for d, o, h, l, c in zip(df['datetime'], df['open'], df['high'], df['low'], df['close'])
    ]
    
    # 1. 创建 K 线图 Traces
    candlestick = go.Candlestick(
        x=df['datetime'],  # 使用 datetime 作为 X 轴
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='K线',
        text=hover_text,
        hoverinfo='text',
        increasing_line_color='#26a69a',  # 上涨颜色
        decreasing_line_color='#ef5350'   # 下跌颜色
    )
    
    # 3. 收集分型和笔的数据
    annotations = []
    
    # 仅收集确认的分型用于连线
    stroke_x = []
    stroke_y = []
    
    # 按索引排序
    sorted_strokes = sorted(strokes, key=lambda x: x[0])
    
    # 遍历分型，根据用户需求：只连接 B -> T (上涨笔)
    # 不连接 T -> B
    for i in range(len(sorted_strokes) - 1):
        curr_idx, curr_type = sorted_strokes[i]
        next_idx, next_type = sorted_strokes[i+1]
        
        # 仅当当前是底(B)且下一个是顶(T)时，画线
        if curr_type == 'B' and next_type == 'T':
            # 获取价格
            curr_price = df['low'].iloc[curr_idx]
            next_price = df['high'].iloc[next_idx]
            
            # 获取对应的 datetime
            curr_datetime = df['datetime'].iloc[curr_idx]
            next_datetime = df['datetime'].iloc[next_idx]
            
            # 添加线段起点(B)
            stroke_x.append(curr_datetime)
            stroke_y.append(curr_price)
            
            # 添加线段终点(T)
            stroke_x.append(next_datetime)
            stroke_y.append(next_price)
            
            # 添加断点(None)，使每条 B->T 独立
            stroke_x.append(None)
            stroke_y.append(None)
    
    # 重置遍历用于添加 Annotations，避免遗漏孤立点
    for idx, f_type in sorted_strokes:
        if idx < 0 or idx >= len(df):
            continue
            
        if f_type == 'T':
            price = df['high'].iloc[idx]
            datetime_val = df['datetime'].iloc[idx]
            # 添加顶分型标注
            annotations.append(dict(
                x=datetime_val, y=price,
                text=f"T {price:.2f}",
                showarrow=False,
                yshift=10,
                font=dict(color='#ef5350', size=10, family='Arial Black')
            ))
            
        elif f_type == 'B':
            price = df['low'].iloc[idx]
            datetime_val = df['datetime'].iloc[idx]
            # 添加底分型标注
            annotations.append(dict(
                x=datetime_val, y=price,
                text=f"B {price:.2f}",
                showarrow=False,
                yshift=-10,
                font=dict(color='#26a69a', size=10, family='Arial Black')
            ))
    
    # 5. 创建笔连线 Trace
    stroke_trace = go.Scatter(
        x=stroke_x,
        y=stroke_y,
        mode='lines',
        line=dict(color='#9c27b0', width=1.5),
        name='笔',
        hoverinfo='skip'
    )
    
    # 6. 组装 Figure
    # 注意：不包含文字 Trace，因为它们会弄乱 RangeSlider
    fig = go.Figure(data=[candlestick, stroke_trace])
    
    # 7. 配置 Layout
    fig.update_layout(
        title=f'Fractal Analysis - {df.iloc[0]["symbol"] if "symbol" in df.columns else ""}',
        yaxis_title='Price',
        xaxis_title='Date',
        dragmode='zoom', # 默认缩放模式
        hovermode='x unified',
        template='plotly_dark',  # 使用深色模板，rangeslider 对比度更好
        height=700,
        margin=dict(l=50, r=50, t=80, b=50),
        
        # 将文字标注作为布局的一部分添加到图中
        annotations=annotations,

        # Y 轴自适应与交互设置
        yaxis=dict(
            autorange=True,      # 自动缩放
            fixedrange=False,    # 允许手动缩放（在价格轴上拖拽）
            side='right',        # 价格显示在右侧
            gridcolor='#2A2A2A',
            zeroline=False,
            exponentformat='none',
            # 增加一个微小的 rangemode，防止 K 线贴着上下边缘
            rangemode='normal'
        ),
        
        # X 轴设置
        xaxis=dict(
            type='date',  # 使用 date 类型，自动处理日期格式
            gridcolor='#2A2A2A',
            
            # 滑块设置
            # 注意：Plotly 的 rangeslider 默认行为是未选中区域显示为浅色，选中区域显示为深色
            # 这与用户期望相反，但 Plotly 不支持反转此行为
            # 使用深色模板可以改善对比度，但仍建议使用鼠标滚轮缩放和拖拽来导航
            rangeslider=dict(
                visible=True,
                thickness=0.08,
                bordercolor='#444444',
                borderwidth=1,
                yaxis=dict(rangemode='match')
            ),
            # 默认显示最后120根K线
            range=[df['datetime'].iloc[max(0, len(df)-120)], df['datetime'].iloc[-1]]
        )
    )
    
    # 启用鼠标滚轮缩放，并清理工具栏
    config = dict({
        'scrollZoom': True,           # 允许滚轮缩放
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
        'displaylogo': False,
        'doubleClick': 'reset+autosize', # 双击重置
        'responsive': True
    })


    if save_path:
        # 强制更新所有 trace 不在 slider 中重复（虽然 plotly 对 scatter 较难完全控制）
        # 但我们之前改用 annotations 已经解决了最大的文字乱入问题
        fig.write_html(save_path, config=config)
        print(f"交互式图表已保存至: {save_path}")
