import pandas as pd
from kline_logic import classify_k_line_combination

def process_csv(input_path, output_path):
    # 读取数据，处理编码(通常为GBK)
    try:
        df = pd.read_csv(input_path, encoding='gbk')
    except UnicodeDecodeError:
        df = pd.read_csv(input_path, encoding='utf-8')
    
    # 根据索引定位 '最高价' 和 '最低价'
    # 之前检查过数据，最高价在索引4，最低价在索引5
    high_col = df.columns[4]
    low_col = df.columns[5]
    
    print(f"识别到高/低价列: {high_col} / {low_col}")
    
    # 状态列表
    status_list = ["INITIAL"] # 第一根没有对比
    
    for i in range(1, len(df)):
        h1 = df.iloc[i-1][high_col]
        l1 = df.iloc[i-1][low_col]
        h2 = df.iloc[i][high_col]
        l2 = df.iloc[i][low_col]
        
        status = classify_k_line_combination(h1, l1, h2, l2)
        status_list.append(status.name)
        
    df['kline_status'] = status_list
    
    # 保存结果
    df.to_csv(output_path, index=False, encoding='gbk')
    print(f"处理完成，保存至: {output_path}")
    
    # 打印前几行预览
    print("\n结果预览:")
    print(df[['日期', high_col, low_col, 'kline_status']].head(10))

if __name__ == "__main__":
    process_csv('TL.CFE.csv', 'TL.CFE_processed.csv')
