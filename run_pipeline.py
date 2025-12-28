"""
run_pipeline.py
驱动整个 K 线分析流水线的入口脚本。

流程:
1. process_tl_cfe.py   - 处理原始 CSV，添加 K 线状态标签
2. kline_merging.py    - 合并包含关系的 K 线
3. filter_fractals.py  - 识别分型并过滤生成有效笔

用法:
    uv run run_pipeline.py
    
输出文件:
    - TL.CFE_processed.csv
    - TL.CFE_merged.csv
    - TL.CFE_strokes.csv
    - output_merged_kline.png
    - output_strokes.png
"""

def main():
    print("=" * 60)
    print("K 线分析流水线 (Bill Williams / Chan Theory)")
    print("=" * 60)
    
    # Step 1: 处理原始数据
    print("\n[Step 1/3] 处理原始 CSV 数据...")
    from process_tl_cfe import process_csv
    process_csv('TL.CFE.csv', 'TL.CFE_processed.csv')
    
    # Step 2: K 线合并
    print("\n[Step 2/3] 合并包含关系的 K 线...")
    from kline_merging import apply_kline_merging
    apply_kline_merging('TL.CFE_processed.csv', 'TL.CFE_merged.csv', 
                        save_plot_path='output_merged_kline.png')
    
    # Step 3: 分型识别与笔过滤
    print("\n[Step 3/3] 识别分型并生成有效笔...")
    from filter_fractals import process_strokes
    process_strokes('TL.CFE_merged.csv', 'TL.CFE_strokes.csv',
                    save_plot_path='output_strokes.png')
    
    print("\n" + "=" * 60)
    print("流水线完成！")
    print("=" * 60)
    print("生成文件:")
    print("  CSV:")
    print("    - TL.CFE_processed.csv  (带状态标签的原始K线)")
    print("    - TL.CFE_merged.csv     (合并后的K线)")
    print("    - TL.CFE_strokes.csv    (带笔端点标记的最终结果)")
    print("  图表:")
    print("    - output_merged_kline.png  (合并后K线图)")
    print("    - output_strokes.png       (笔端点标记图)")

if __name__ == "__main__":
    main()
