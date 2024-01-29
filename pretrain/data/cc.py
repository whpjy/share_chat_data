import csv

# 指定要读取的CSV文件路径
filename = "intent_recognize.csv"

# 使用with语句打开文件，确保在操作完成后自动关闭
with open(filename, 'r') as csvfile:
    # 创建一个csv阅读器对象
    reader = csv.reader(csvfile)

    # 遍历CSV文件的每一行
    for row in reader:
        # 每一行数据在这里以列表形式呈现
        print(row)
