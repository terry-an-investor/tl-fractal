# K 线分析流水线 - 代码工作流

## 整体架构

```mermaid
graph TB
    subgraph "📂 data/raw/"
        RAW[("原始数据<br/>TL.CFE.xlsx")]
    end
    
    subgraph "📦 src/io/"
        ADAPTER["adapters/<br/>WindCFEAdapter"]
        SCHEMA["schema.py<br/>OHLCData"]
        LOADER["loader.py<br/>load_ohlc()"]
        
        RAW --> ADAPTER
        ADAPTER --> SCHEMA
        SCHEMA --> LOADER
    end
    
    subgraph "📊 src/analysis/"
        PROCESS["process_ohlc.py<br/>add_kline_status()"]
        MERGE["merging.py<br/>apply_kline_merging()"]
        FRACTAL["fractals.py<br/>process_strokes()"]
        KLINE["kline_logic.py<br/>classify_k_line_combination()"]
        
        LOADER --> PROCESS
        KLINE -.-> PROCESS
        PROCESS --> MERGE
        MERGE --> FRACTAL
    end
    
    subgraph "📂 data/processed/"
        CSV1[("*_processed.csv")]
        CSV2[("*_merged.csv")]
        CSV3[("*_strokes.csv")]
        
        PROCESS --> CSV1
        MERGE --> CSV2
        FRACTAL --> CSV3
    end
    
    subgraph "📂 output/"
        PNG1[("*_merged_kline.png")]
        PNG2[("*_strokes.png")]
        
        MERGE --> PNG1
        FRACTAL --> PNG2
    end
    
    PIPELINE["🚀 run_pipeline.py"] --> LOADER
    
    style RAW fill:#e1f5fe
    style PIPELINE fill:#fff3e0
    style CSV1 fill:#e8f5e9
    style CSV2 fill:#e8f5e9
    style CSV3 fill:#e8f5e9
    style PNG1 fill:#fce4ec
    style PNG2 fill:#fce4ec
```

## Pipeline 执行流程

```mermaid
sequenceDiagram
    participant User
    participant Pipeline as run_pipeline.py
    participant IO as src/io/
    participant Analysis as src/analysis/
    participant Output as data/processed/<br/>output/
    
    User->>Pipeline: uv run run_pipeline.py
    
    Note over Pipeline: Step 1: 加载数据
    Pipeline->>IO: load_ohlc("data/raw/TL.CFE.xlsx")
    IO->>IO: WindCFEAdapter.load()
    IO->>IO: 过滤无效行 + 列名映射
    IO-->>Pipeline: OHLCData 对象
    
    Note over Pipeline: Step 2: 添加K线状态
    Pipeline->>Analysis: process_and_save(data)
    Analysis->>Analysis: classify_k_line_combination()
    Analysis-->>Output: *_processed.csv
    
    Note over Pipeline: Step 3: K线合并
    Pipeline->>Analysis: apply_kline_merging()
    Analysis->>Analysis: 处理包含关系
    Analysis-->>Output: *_merged.csv + *.png
    
    Note over Pipeline: Step 4: 分型识别
    Pipeline->>Analysis: process_strokes()
    Analysis->>Analysis: 识别顶底分型 + 过滤成笔
    Analysis-->>Output: *_strokes.csv + *.png
    
    Pipeline-->>User: ✅ 流水线完成
```

## 模块依赖关系

```mermaid
graph LR
    subgraph "src/io/"
        A1[schema.py]
        A2[loader.py]
        A3[adapters/base.py]
        A4[adapters/wind_cfe_adapter.py]
        
        A3 --> A1
        A4 --> A3
        A4 --> A1
        A2 --> A1
        A2 --> A4
    end
    
    subgraph "src/analysis/"
        B1[kline_logic.py]
        B2[process_ohlc.py]
        B3[merging.py]
        B4[fractals.py]
        
        B2 --> B1
        B2 --> A1
        B3 --> A1
        B4 --> A1
    end
    
    subgraph "入口"
        C1[run_pipeline.py]
        C1 --> A2
        C1 --> B2
        C1 --> B3
        C1 --> B4
    end
```

## 数据转换流程

| 阶段 | 输入 | 处理 | 输出 |
|------|------|------|------|
| **加载** | xlsx/csv (Wind格式) | 过滤脏数据 + 列名标准化 | `OHLCData` 对象 |
| **状态标记** | `OHLCData` | 分类相邻K线关系 | `*_processed.csv` |
| **合并** | processed.csv | 处理包含关系 | `*_merged.csv` + 图 |
| **分型** | merged.csv | 识别顶底 + 笔过滤 | `*_strokes.csv` + 图 |
