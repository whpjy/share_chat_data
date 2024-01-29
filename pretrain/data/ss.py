import json

filename = "zhibiao.txt"

# 使用with语句打开文件，确保在操作完成后自动关闭
with open(filename, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

print(len(json_data))

new_json_all = {}

for single_data in json_data:

    new_group = []
    for group_word in single_data['group']:
        new_group.append({group_word["columnName"]: group_word})

    single_data['group'] = new_group
    new_json_all[single_data["targetName"]] = single_data

filename_json = "zhibiao.json"
fr = open(filename_json, 'w', encoding='utf-8')
json.dump(new_json_all, fr, ensure_ascii=False, indent=4)