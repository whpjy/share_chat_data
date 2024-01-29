import json

filename = "zhibiao.txt"

# 使用with语句打开文件，确保在操作完成后自动关闭
with open(filename, 'r', encoding='utf-8') as f:

    json_data = json.load(f)

print(len(json_data))

target2id = {}
for single_data in json_data:
    for group_word in single_data['group']:
        print(group_word)
