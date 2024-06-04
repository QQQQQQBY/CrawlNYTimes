import pandas as pd
import os
def filter_csv_by_keyword(input_csv, output_csv, keywords, date_column, cutoff_date, begin_date):
    # 读取CSV文件
    df = pd.read_csv(input_csv)
    # 转换日期列为datetime类型
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

     # 筛选同时包含所有关键词的行（不区分大小写）并且日期早于指定日期
    filtered_df = df[
        df.apply(lambda row: all(keyword.lower() in row.astype(str).str.lower().str.cat(sep=' ') for keyword in keywords), axis=1) &
        ((df[date_column] > begin_date) & (df[date_column] < cutoff_date)) & (df['rating'] == True)
    ]
    # 检查输出文件是否存在
    file_exists = os.path.isfile(output_csv)

    # 将筛选结果写入新的CSV文件，如果文件不存在则写入列名，如果文件存在则追加不写列名
    filtered_df.to_csv(output_csv, mode='a', header=not file_exists, index=False)

# 示例使用
input_csv = 'C:/Users/lenovo/Desktop/reddit_new/AgentReddit/snopes/data/bbc-bbc-bbc.csv'  # 输入的CSV文件路径
output_csv = 'C:/Users/lenovo/Desktop/reddit_new/AgentReddit/snopes/data/us_politics.csv'  # 输出的CSV文件路径
keyword = ["Biden"]  # 要筛选的关键词
date_column = 'date'  # 日期列的名称
cutoff_date = pd.Timestamp('2024-04-01T00:00:01.000Z')  # 截止日期
begin_date = pd.Timestamp('2024-01-01T00:00:01.000Z')  # 截止日期
filter_csv_by_keyword(input_csv, output_csv, keyword, date_column, cutoff_date, begin_date)
