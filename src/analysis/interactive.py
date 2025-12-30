"""
interactive.py
交互式 K 线图表模块 (TradingView Lightweight Charts)

使用 TradingView 的开源 Lightweight Charts 库生成专业级交互式图表，支持：
- K 线蜡烛图 (专业 TradingView 风格)
- 技术指标叠加 (EMA, SMA, etc.)
- 笔连线和分型标注
- 内置 Crosshair、时间轴导航
- 自动 Y 轴缩放
"""

import json
import pandas as pd
from typing import List, Tuple, Optional
from pathlib import Path


# 预定义的指标颜色映射
INDICATOR_COLORS = {
    'ema5': '#FF6B6B',
    'ema10': '#4ECDC4',
    'ema20': '#FFA500',
    'ema50': '#45B7D1',
    'ema200': '#96CEB4',
    'sma5': '#FFEAA7',
    'sma10': '#DFE6E9',
    'sma20': '#74B9FF',
}


class ChartBuilder:
    """
    交互式图表构建器 (TradingView Lightweight Charts)
    
    使用链式调用模式构建图表：
    
    Example:
        chart = ChartBuilder(df)
        chart.add_candlestick()
        chart.add_indicator('EMA20', df['ema20'], '#FFA500')
        chart.add_strokes(stroke_list)
        chart.add_fractal_markers(stroke_list)
        chart.build('output/chart.html')
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化图表构建器
        
        Args:
            df: 包含 datetime, open, high, low, close 的 DataFrame
        """
        self.df = df.copy()
        self.candlestick_data = []
        self.indicators = []  # [(name, data, color), ...]
        self.stroke_lines = []  # 笔的线段数据
        self.markers = []  # 标记点数据
        
        # 确保 datetime 列存在且是 datetime 类型
        if 'datetime' in self.df.columns:
            self.df['datetime'] = pd.to_datetime(self.df['datetime'])
    
    def _timestamp(self, dt) -> int:
        """将 datetime 转换为 Unix 时间戳 (秒)"""
        return int(pd.Timestamp(dt).timestamp())
    
    def add_candlestick(self) -> 'ChartBuilder':
        """
        添加 K 线蜡烛图层
        
        Returns:
            self: 支持链式调用
        """
        for _, row in self.df.iterrows():
            self.candlestick_data.append({
                'time': self._timestamp(row['datetime']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
            })
        return self
    
    def add_indicator(
        self, 
        name: str, 
        series: pd.Series, 
        color: Optional[str] = None,
        line_width: int = 2
    ) -> 'ChartBuilder':
        """
        添加技术指标线
        
        Args:
            name: 指标名称 (如 'EMA20')
            series: 指标数据序列
            color: 线条颜色，None 则自动选择
            line_width: 线条宽度
        
        Returns:
            self: 支持链式调用
        """
        if color is None:
            color = INDICATOR_COLORS.get(name.lower(), '#FFFFFF')
        
        data = []
        for i, (_, row) in enumerate(self.df.iterrows()):
            value = series.iloc[i]
            if pd.notna(value):
                data.append({
                    'time': self._timestamp(row['datetime']),
                    'value': float(value)
                })
        
        self.indicators.append({
            'name': name,
            'data': data,
            'color': color,
            'lineWidth': line_width
        })
        return self
    
    def add_strokes(self, strokes: List[Tuple[int, str]]) -> 'ChartBuilder':
        """
        添加笔连线
        
        Args:
            strokes: 分型标记列表 [(index, 'T'|'B'), ...]
                     注意：只接受纯 'T' 或 'B'，忽略 'Tx', 'Bx' 等
        
        Returns:
            self: 支持链式调用
        """
        if not strokes:
            return self
        
        # 【关键】只筛选有效的 T 和 B (忽略 Tx, Bx 等被替换的分型)
        valid_strokes = [
            (idx, f_type) for idx, f_type in strokes 
            if f_type in ('T', 'B')
        ]
        
        if not valid_strokes:
            return self
        
        # 按索引排序
        sorted_strokes = sorted(valid_strokes, key=lambda x: x[0])
        
        # 构建笔的线段数据
        stroke_data = []
        for idx, f_type in sorted_strokes:
            if idx < 0 or idx >= len(self.df):
                continue
            row = self.df.iloc[idx]
            price = float(row['high']) if f_type == 'T' else float(row['low'])
            stroke_data.append({
                'time': self._timestamp(row['datetime']),
                'value': price
            })
        
        self.stroke_lines = stroke_data
        return self
    
    def add_fractal_markers(self, fractals: List[Tuple[int, str]]) -> 'ChartBuilder':
        """
        添加顶底分型标记
        
        Args:
            fractals: 分型标记列表 [(index, 'T'|'B'), ...]
        
        Returns:
            self: 支持链式调用
        """
        # 【关键】只筛选有效的 T 和 B
        valid_fractals = [
            (idx, f_type) for idx, f_type in fractals 
            if f_type in ('T', 'B')
        ]
        
        for idx, f_type in valid_fractals:
            if idx < 0 or idx >= len(self.df):
                continue
            
            row = self.df.iloc[idx]
            if f_type == 'T':
                price = float(row['high'])
                self.markers.append({
                    'time': self._timestamp(row['datetime']),
                    'position': 'aboveBar',
                    'color': '#ef5350',
                    'shape': 'arrowDown',
                    'text': f'T {price:.2f}'
                })
            elif f_type == 'B':
                price = float(row['low'])
                self.markers.append({
                    'time': self._timestamp(row['datetime']),
                    'position': 'belowBar',
                    'color': '#26a69a',
                    'shape': 'arrowUp',
                    'text': f'B {price:.2f}'
                })
        
        return self
    
    def build(self, save_path: str, title: Optional[str] = None) -> None:
        """
        组装并保存为 HTML
        
        Args:
            save_path: HTML 文件保存路径
            title: 图表标题
        """
        if title is None:
            symbol = self.df['symbol'].iloc[0] if 'symbol' in self.df.columns else ''
            title = f'Fractal Analysis - {symbol}'
        
        # 序列化数据为 JSON
        candlestick_json = json.dumps(self.candlestick_data)
        indicators_json = json.dumps(self.indicators)
        strokes_json = json.dumps(self.stroke_lines)
        markers_json = json.dumps(self.markers)
        
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://unpkg.com/lightweight-charts@4.1.0/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #131722;
            color: #d1d4dc;
        }}
        .container {{
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        .header {{
            padding: 12px 20px;
            background: #1e222d;
            border-bottom: 1px solid #2a2e39;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .header h1 {{
            font-size: 16px;
            font-weight: 500;
            color: #d1d4dc;
        }}
        .legend {{
            display: flex;
            gap: 15px;
            font-size: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .legend-color {{
            width: 12px;
            height: 3px;
            border-radius: 1px;
        }}
        #chart-container {{
            flex: 1;
            width: 100%;
        }}
        .tooltip {{
            position: absolute;
            display: none;
            padding: 8px 12px;
            background: rgba(30, 34, 45, 0.95);
            border: 1px solid #2a2e39;
            border-radius: 4px;
            font-size: 12px;
            z-index: 1000;
            pointer-events: none;
        }}
        .tooltip-row {{
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin: 2px 0;
        }}
        .tooltip-label {{
            color: #787b86;
        }}
        .tooltip-value {{
            font-weight: 500;
        }}
        .tooltip-value.up {{
            color: #26a69a;
        }}
        .tooltip-value.down {{
            color: #ef5350;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="legend" id="legend"></div>
        </div>
        <div id="chart-container"></div>
    </div>
    <div class="tooltip" id="tooltip"></div>

    <script>
        // 数据
        const candlestickData = {candlestick_json};
        const indicators = {indicators_json};
        const strokesData = {strokes_json};
        const markersData = {markers_json};

        // 创建图表
        const container = document.getElementById('chart-container');
        const chart = LightweightCharts.createChart(container, {{
            layout: {{
                background: {{ type: 'solid', color: '#131722' }},
                textColor: '#d1d4dc',
            }},
            grid: {{
                vertLines: {{ color: '#1e222d' }},
                horzLines: {{ color: '#1e222d' }},
            }},
            crosshair: {{
                mode: LightweightCharts.CrosshairMode.Normal,
                vertLine: {{
                    color: '#758696',
                    width: 1,
                    style: LightweightCharts.LineStyle.Dashed,
                    labelBackgroundColor: '#2a2e39',
                }},
                horzLine: {{
                    color: '#758696',
                    width: 1,
                    style: LightweightCharts.LineStyle.Dashed,
                    labelBackgroundColor: '#2a2e39',
                }},
            }},
            rightPriceScale: {{
                borderColor: '#2a2e39',
                scaleMargins: {{
                    top: 0.1,
                    bottom: 0.1,
                }},
            }},
            timeScale: {{
                borderColor: '#2a2e39',
                timeVisible: true,
                secondsVisible: false,
            }},
            handleScroll: {{
                vertTouchDrag: false,
            }},
        }});

        // K 线系列
        const candlestickSeries = chart.addCandlestickSeries({{
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderUpColor: '#26a69a',
            borderDownColor: '#ef5350',
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        }});
        candlestickSeries.setData(candlestickData);

        // 设置标记 (分型点)
        if (markersData.length > 0) {{
            candlestickSeries.setMarkers(markersData);
        }}

        // 笔连线 (使用 Line Series)
        if (strokesData.length > 0) {{
            const strokeSeries = chart.addLineSeries({{
                color: '#9c27b0',
                lineWidth: 2,
                crosshairMarkerVisible: false,
                lastValueVisible: false,
                priceLineVisible: false,
            }});
            strokeSeries.setData(strokesData);
        }}

        // 技术指标线
        const legendContainer = document.getElementById('legend');
        indicators.forEach((indicator, index) => {{
            const lineSeries = chart.addLineSeries({{
                color: indicator.color,
                lineWidth: indicator.lineWidth,
                crosshairMarkerVisible: true,
                lastValueVisible: false,
                priceLineVisible: false,
            }});
            lineSeries.setData(indicator.data);

            // 添加图例
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            legendItem.innerHTML = `
                <div class="legend-color" style="background: ${{indicator.color}}"></div>
                <span>${{indicator.name}}</span>
            `;
            legendContainer.appendChild(legendItem);
        }});

        // 添加笔图例
        if (strokesData.length > 0) {{
            const strokeLegend = document.createElement('div');
            strokeLegend.className = 'legend-item';
            strokeLegend.innerHTML = `
                <div class="legend-color" style="background: #9c27b0"></div>
                <span>笔</span>
            `;
            legendContainer.appendChild(strokeLegend);
        }}

        // Tooltip (悬浮信息)
        const tooltip = document.getElementById('tooltip');
        
        chart.subscribeCrosshairMove((param) => {{
            if (!param.time || !param.point) {{
                tooltip.style.display = 'none';
                return;
            }}

            const data = param.seriesData.get(candlestickSeries);
            if (!data) {{
                tooltip.style.display = 'none';
                return;
            }}

            const date = new Date(param.time * 1000);
            const dateStr = date.toISOString().split('T')[0];
            
            const change = data.close - data.open;
            const changeClass = change >= 0 ? 'up' : 'down';
            
            // 获取指标值
            let indicatorHtml = '';
            indicators.forEach((indicator, index) => {{
                const series = chart.getSeries()[index + 1]; // +1 因为第一个是 candlestick
                // 简化：直接从数据中查找
                const found = indicator.data.find(d => d.time === param.time);
                if (found) {{
                    indicatorHtml += `
                        <div class="tooltip-row">
                            <span class="tooltip-label">${{indicator.name}}</span>
                            <span class="tooltip-value" style="color:${{indicator.color}}">${{found.value.toFixed(4)}}</span>
                        </div>
                    `;
                }}
            }});

            tooltip.innerHTML = `
                <div class="tooltip-row">
                    <span class="tooltip-label">日期</span>
                    <span class="tooltip-value">${{dateStr}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">开</span>
                    <span class="tooltip-value ${{changeClass}}">${{data.open.toFixed(4)}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">高</span>
                    <span class="tooltip-value ${{changeClass}}">${{data.high.toFixed(4)}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">低</span>
                    <span class="tooltip-value ${{changeClass}}">${{data.low.toFixed(4)}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">收</span>
                    <span class="tooltip-value ${{changeClass}}">${{data.close.toFixed(4)}}</span>
                </div>
                ${{indicatorHtml}}
            `;

            // 定位 tooltip
            const x = param.point.x;
            const y = param.point.y;
            const containerRect = container.getBoundingClientRect();
            
            let left = x + 20;
            let top = y + 20;
            
            // 防止超出边界
            if (left + 180 > containerRect.width) {{
                left = x - 180;
            }}
            if (top + 200 > containerRect.height) {{
                top = y - 200;
            }}

            tooltip.style.display = 'block';
            tooltip.style.left = left + 'px';
            tooltip.style.top = (top + containerRect.top) + 'px';
        }});

        // 自适应大小
        const resizeObserver = new ResizeObserver(entries => {{
            for (const entry of entries) {{
                chart.applyOptions({{
                    width: entry.contentRect.width,
                    height: entry.contentRect.height,
                }});
            }}
        }});
        resizeObserver.observe(container);

        // 初始显示最后 120 根 K 线
        if (candlestickData.length > 120) {{
            const from = candlestickData[candlestickData.length - 120].time;
            const to = candlestickData[candlestickData.length - 1].time;
            chart.timeScale().setVisibleRange({{ from, to }});
        }}
    </script>
</body>
</html>
'''
        
        # 保存文件
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"交互式图表已保存至: {save_path}")


# ============================================================
# 向后兼容的函数接口
# ============================================================

def plot_interactive_kline(
    df: pd.DataFrame, 
    strokes: List[Tuple[int, str]], 
    save_path: str = None
) -> None:
    """
    绘制交互式 K 线图 - 向后兼容函数
    
    Args:
        df: 包含 datetime, open, high, low, close 的 DataFrame
        strokes: 分型标记 list of (index, type)，如 [(10, 'T'), (15, 'B')]
        save_path: HTML 保存路径
    
    Note:
        此函数保留以兼容旧代码，新代码建议使用 ChartBuilder 类。
    """
    chart = ChartBuilder(df)
    chart.add_candlestick()
    chart.add_strokes(strokes)
    chart.add_fractal_markers(strokes)
    
    if save_path:
        chart.build(save_path)
