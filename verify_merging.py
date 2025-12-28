import pandas as pd

def verify_merging_result(merged_path):
    print(f"开始验证合并结果: {merged_path}")
    df = pd.read_csv(merged_path, encoding='gbk')
    
    bars = df.to_dict('records')
    total_bars = len(bars)
    
    issues_found = 0
    
    print(f"共检测到 {total_bars} 根K线")
    
    for i in range(1, total_bars):
        curr = bars[i]
        prev = bars[i-1]
        
        h_curr, l_curr = curr['最高价(元)'], curr['最低价(元)']
        h_prev, l_prev = prev['最高价(元)'], prev['最低价(元)']
        
        # 检查是否仍存在包含关系
        is_inside = (h_curr <= h_prev) and (l_curr >= l_prev)
        is_outside = (h_curr >= h_prev) and (l_curr <= l_prev)
        
        if is_inside:
            print(f"[发现问题] 第 {i} 根与第 {i-1} 根仍存在 INSIDE 关系！")
            print(f"  Prev: {prev['日期']} H:{h_prev} L:{l_prev}")
            print(f"  Curr: {curr['日期']} H:{h_curr} L:{l_curr}")
            issues_found += 1
            
        elif is_outside:
            print(f"[发现问题] 第 {i} 根与第 {i-1} 根仍存在 OUTSIDE 关系！")
            print(f"  Prev: {prev['日期']} H:{h_prev} L:{l_prev}")
            print(f"  Curr: {curr['日期']} H:{h_curr} L:{l_curr}")
            issues_found += 1
            
    if issues_found == 0:
        print("\n✅ 验证通过：合并后的数据中不存在任何 Inside 或 Outside 关系。")
    else:
        print(f"\n❌ 验证失败：发现 {issues_found} 处残留的包含关系。")
        print("建议：合并逻辑需要改为递归检查，即合并后的新K线需要立即与下一根比较，或者反复扫描直到无包含。")

if __name__ == "__main__":
    verify_merging_result('TL.CFE_merged.csv')
