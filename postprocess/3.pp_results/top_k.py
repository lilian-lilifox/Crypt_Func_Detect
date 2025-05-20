import pandas as pd
import argparse
import os

# 设置命令行参数解析
parser = argparse.ArgumentParser(
    description="Select top k rows by sim column from a CSV file."
)
parser.add_argument("input_file", type=str, help="Path to the input CSV file")
parser.add_argument("k", type=int, help="Number of top rows to select")
args = parser.parse_args()

# 获取输入文件的目录和文件名
input_dir = os.path.dirname(args.input_file) or "."  # 如果没有目录，使用当前目录
input_filename = os.path.basename(args.input_file)
filename_without_ext = os.path.splitext(input_filename)[0]  # 去掉扩展名
output_filename = f"{filename_without_ext}_top_{args.k}.csv"
output_path = os.path.join(input_dir, output_filename)

try:
    # 读取 CSV 文件
    df = pd.read_csv(args.input_file)
    # 检查 sim 列是否存在
    if "sim" not in df.columns:
        raise ValueError("Column 'sim' not found in the CSV file")
    # 按 sim 列降序排序并取前 k 行
    top_k = df.sort_values(by="sim", ascending=False).head(args.k)
    # 输出结果到终端
    print(top_k)
    # 保存结果到文件
    top_k.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
except FileNotFoundError:
    print(f"Error: File '{args.input_file}' not found")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
