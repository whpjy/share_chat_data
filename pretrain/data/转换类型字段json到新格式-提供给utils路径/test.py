import json

filename = "类型字段.txt"

# 使用with语句打开文件，确保在操作完成后自动关闭
with open(filename, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

print(len(json_data))

new_json_all = {}

for single_data in json_data:

    columnId = single_data["columnId"]
    columnName = single_data["columnName"]
    values_list = single_data["values"]
    for v in values_list:
        new_json_all[v["targetValue"]] = {"columnId": columnId, "columnName": columnName}


filename_json = "where_type.json"
fr = open(filename_json, 'w', encoding='utf-8')
json.dump(new_json_all, fr, ensure_ascii=False, indent=4)