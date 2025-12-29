import pandas as pd
import os

processed_path = 'data/processed/TL.CFE_processed.csv'
merged_path = 'data/processed/TL.CFE_merged.csv'
strokes_path = 'data/processed/TL.CFE_strokes.csv'

def check_file(path):
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"{path}: {len(df)} rows, Date range: {df['datetime'].iloc[0]} to {df['datetime'].iloc[-1]}")
    else:
        print(f"{path}: Does not exist")

check_file(processed_path)
check_file(merged_path)
check_file(strokes_path)

svg_path = 'output/TL.CFE_strokes.svg'
if os.path.exists(svg_path):
    with open(svg_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"\nSVG stats:")
    print(f"File size: {len(content) / 1024:.2f} KB")
    # Count rects (K-line bodies/wicks are bars)
    # Matplotlib usually uses <rect> or <path> for bars.
    print(f"Count of '<rect': {content.count('<rect')}")
    print(f"Count of '<path': {content.count('<path')}")
