# encoding=utf-8
import glob
import json
import re
import requests
import config
import spacy
from functools import lru_cache
from utils.send_llm import send_local_qwen_message, send_proxy_qwen_message
from scene_config import scene_prompts
from sentence_transformers import SentenceTransformer, util
# 加载预训练的BERT模型，这里以'MiniLM-L6-v2'为例，也可以选择其他支持句子级别的模型

model = SentenceTransformer('pretrain/all-MiniLM-L6-v2')

# nlp = spacy.load("zh_core_web_sm")

send_llm_req = {
    "Qwen": send_local_qwen_message,
    "Qwen_PROXY": send_proxy_qwen_message,
}

countword = [
    "统筹基金", "大病保险", "大额医疗补助", "公务员补助", "民政补助", "其他基金支付", "现金", "账户支付数",
    "共济账户", "总费用", "费用", "灌南县", "灌云县", "赣榆区", "市本级", "东海县", "职工基本医疗保险",
    "城乡居民基本医疗保险", "一级甲等", "三级甲等", "二级甲等", "无等级", "三级丙等", "三级乙等",
    "省内异地", "省外异地", "本地", "职工退休", "普通居民（成年）", "未成年（未入学）",
    "公务员退休", "灵活就业人员在职", "职工在职", "学龄前儿童", "灵活就业人员退休", "大学生",
    "中小学生", "公务员在职", "南京市江宁区东山街道上坊社区卫生服务中心", "苏州大学附属第二医院",
    "无锡华清医院", "南京市浦口区中心医院", "无锡市人民医院", "南京市江宁区中医院",
    "昆山市第一人民医院", "苏州大学附属儿童医院", "南京建邺集庆中西医结合诊所",
    "北京市朝阳区奥运村社区卫生服务中心", "南京市中西医结合医院", "张家港市第六人民医院",
    "杭州市富阳区第一人民医院", "连云港长寿医院", "连云港市中医院", "南京市第二医院",
    "连云港市赣榆区中医院", "上海交通大学医学院附属新华医院",
    "南京医科大学第二附属医院", "赣榆瑞慈医院", "连云港灌云仁济医院", "常州市第七人民医院",
    "灌云县人民医院", "苏州大学附属第一医院", "连云港市第一人民医院", "启东市城区医院",
    "东海县人民医院", "南通大学附属医院", "常熟市古里卫生院", "江苏省中西医结合医院",
    "江苏省人民医院", "连云港圣安医院", "太仓市第一人民医院", "灌南县人民医院",
    "苏州明基医院", "苏州明基医院互联网医院", "天津市滨海新区大港医院", "浙江省肿瘤医院",
    "连云港市第二人民医院（连云港市临床肿瘤研究所）", "灌云县精神病医院",
    "苏州工业园区星海医院", "淮安市第一人民医院", "镇江市中医院", "连云港市东方医院",
    "灌南县第一人民医院", "连云港市赣榆区人民医院", "东海县精神病医院", "上海儿童医学中心",
    "连云港市传染病医院", "连云港市第四人民医院", "东海仁慈医院",
    "中国人民解放军总医院第五医学中心", "连云港市赣榆区精神病防治院（江苏省赣榆经济开发区社区卫生服务中心）",
    "南京南钢医院", "无锡市仁德（康复）医院", "北京王府中西医结合医院", "灌南县精神病医院",
    "灌云县中医院", "北京大学第一医院(北京大学北大医院）", "东海县中医院",
    "南京军区总医院", "南京明基医院", "南京一民医院", "南京市雨花医院(南京市雨花台区雨花社区卫生服务中心)",
    "连云港市康复医院", "恶性肿瘤（术后康复）", "肿瘤术后放疗", "恶性肿瘤（放疗）", "透析",
    "恶性肿瘤（化疗）", "肿瘤术后化疗", "肿瘤术后辅助治疗", "精神病",
    "慢性肾功衰竭（非透析治疗）", "器官移植抗排异治疗", "再生障碍性贫血", "系统性红斑狼疮",
    "器官移植术后抗排斥药物", "急慢性肾衰腹透", "急慢性肾衰血透", "慢性肾功能衰竭",
    "居民精神病门诊", "躁狂型精神病（门）", "活动性肺结核", "医保基金", "合计", "特殊病", "居民", "基金"
]


def get_forcr_word(sentence):
    words = []

    # 遍历 countword 中的每个词
    for word in countword:
        if word in sentence:
            is_part_of_other_word = False

            # 再次遍历 words 列表，检查是否是其他词的部分
            for other_word in words:
                if word != other_word and word in other_word:
                    is_part_of_other_word = True
                    break

            # 如果该词不是其他词的部分，则添加到 words 列表中
            if not is_part_of_other_word:
                words.append(word)

    return words


def check_and_fill_forcr_word(key_list, user_input):
    # 尽管给模型提醒了forcr_word，但模型结果仍然可能缺失，此时再补充一次
    force_word = get_forcr_word(user_input)
    for word in force_word:
        if word not in key_list:
            key_list.append(word)

    for key_word in key_list:
        if key_word not in user_input:
            key_list.remove(key_word)

    return key_list


def get_clean_text(user_input):
    replacements = {
        "区域": "统筹区",
        "地区": "统筹区",
        "各类人员": "人员类别",
        "特殊疾病": "特殊病",
        "一月": "1月",
        "二月": "2月",
        "三月": "3月",
        "四月": "4月",
        "五月": "5月",
        "六月": "6月",
        "七月": "7月",
        "八月": "8月",
        "九月": "9月",
        "十月": "10月",
        "十一月": "11月",
        "十二月": "12月"
    }
    for old, new in replacements.items():
        user_input = user_input.replace(old, new)

    return user_input


dim_words = ["统筹区", "险种", "医院等级", "就医地", "人员类别", "医院名称", "病种","医疗机构名称","医疗机构简称","联系地址","经营性质","医保办电话","医保办邮箱","机构性质"]  # group分类词
time_word = ["月", "日", "年", "季度", "天", "周"]  # 时间前不带序词也可作为分类词


def contains_find(user_input, word):
    positions = []
    start = 0
    while start < len(user_input):
        position = user_input.find(word, start)
        if position == -1:
            break
        positions.append(position)
        start = position + 1
    return positions


def get_group_word(user_input):
    words = []
    for word in time_word:
        positions = contains_find(user_input, word)
        if positions != -1:
            for position in positions:
                if re.match(r'^[0-9一二三四五六七八九十上个本今昨前当下后明去过去两]', user_input[position - 1]):
                    continue
                else:
                    words.append(word)
                    break
    for word in dim_words:
        if word in user_input:
            words.append(word)
    print("句子中存在且可能的group词：", words)
    return words


def extract_value(text: str, keyword: str, direction: str) -> int:
    # 从关键词后提取数字
    value_str = text.split(keyword)[-1].split(direction)[0].strip()
    return int(value_str) if value_str.isdigit() else 0


def extract_limits(text):
    limits = []

    # 检查是否包含同比下降/上升的关键词
    if "同比下降" in text:
        value = extract_value(text, "同比下降", "下降")
        limits.append({"sign": -1, "value": value})
    elif "同比上升" in text:
        value = extract_value(text, "同比上升", "上升")
        limits.append({"sign": 1, "value": value})

    # 检查是否包含大于/小于关键词
    if "大于" in text:
        value = extract_value(text, "大于", "元")
        limits.append({"sign": 1, "value": value})
    elif "小于" in text:
        value = extract_value(text, "小于", "元")
        limits.append({"sign": -1, "value": value})

    return limits


def extract_compare(text):
    compare = []
    if "同比" in text:
        compare.append("同比")
    if "环比" in text:
        compare.append("环比")
    return compare


def extract_rank(text):
    rank = []
    if "倒序" in text:
        rank.append("-")
    else:
        rank.append("+")
    chinese_numbers = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一"]
    for i in range(1, 10):
        keyword = f"前{i}"
        keyword1 = f"前{chinese_numbers[i]}"
        if keyword1 in text:
            rank.append(i)
        if keyword in text:
            rank.append(i)

    for i in range(1, 10):
        keyword = f"后{i}"
        keyword1 = f"后{chinese_numbers[i]}"
        if keyword1 in text:
            rank = ["-", i]

        if keyword in text:
            rank = ["-", i]

    return rank


def clear_group_and_compare_in_key(key, group, compare):
    for word in group:
        if word in key:
            key.remove(word)

    for word in compare:
        if word in key:
            key.remove(word)

    return key


def check_time(time_list):
    # 如果是一维列表，将其包装成一个二维列表
    try:
        if isinstance(time_list, list):

            if not all(isinstance(sublist, list) for sublist in time_list):
                time_list = [time_list]
    except Exception as e:
        # 处理异常，可以打印错误消息或采取其他措施
        print(f"An error occurred: {e}")
    return time_list


def check_group(group_list, user_input):
    for word in dim_words:  # 如果模型没有识别到分类词，规则强化
        if word not in group_list:
            if ("按照" + word) in user_input or ("按" + word) in user_input or ("各" + word) in user_input:
                group_list.append(word)

    for word in time_word:  # 如果模型没有识别到分类词，规则强化
        if word not in group_list:
            if ("按照" + word) in user_input or ("按" + word) in user_input or ("各" + word) in user_input:
                group_list.append(word)

    if "按照医院" in user_input or "按医院" in user_input and "医院等级" not in user_input:
        if "医院名称" not in group_list:
            group_list.append("医院名称")

    if "医院" in group_list and "医院名称" in group_list:  # 这个功能是在正确情况下删除可能存在的“医院”噪声
        group_list = [item for item in group_list if item != "医院"]
    if "医院" in group_list and "医院等级" in group_list:
        group_list = [item for item in group_list if item != "医院"]

    new_group_list = []
    for group_word in group_list:
        if (group_word not in dim_words and group_word not in time_word) and group_word != "医院":
            # group_list.remove(group_word)
            continue  # 舍弃
        else:
            new_group_list.append(group_word)

    return new_group_list


# 当 key 中出现了分类词（模型识别放到key中的），应放在group中
def check_key_and_group(key_list, group_list):
    for word in dim_words:
        if word in key_list:
            if word in group_list:
                key_list.remove(word)
            else:
                key_list.remove(word)
                group_list.append(word)

    return key_list, group_list


def contains_time(sentence):
    time_word = ["月", "日", "年", "季度", "天", "周"]
    time_flag = False
    positions = []
    for word in time_word:
        positions = contains_find(sentence, word)
        if positions != -1:
            for position in positions:
                if re.match(r'^[0-9一二三四五六七八九十上个本今昨前当下后明去过去两]', sentence[position - 1]):
                    time_flag = True
                    return time_flag
    return time_flag


def filename_to_classname(filename):
    """
    Convert a snake_case filename to a CamelCase class name.

    Args:
    filename (str): The filename in snake_case, without the .py extension.

    Returns:
    str: The converted CamelCase class name.
    """
    parts = filename.split('_')
    class_name = ''.join(part.capitalize() for part in parts)
    return class_name


def load_scene_templates(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


import os


def load_all_scene_configs():
    # 用于存储所有场景配置的字典
    all_scene_configs = {}
    print(os.getcwd())

    # 搜索目录下的所有json文件
    for file_path in glob.glob("scene_config/*.json"):
        current_config = load_scene_templates(file_path)

        for key, value in current_config.items():
            # todo 可以有加载优先级
            # 只有当键不存在时，才添加到all_scene_configs中
            if key not in all_scene_configs:
                all_scene_configs[key] = value

    return all_scene_configs


# @lru_cache(maxsize=100)
def send_message(message):
    """
    请求LLM函数
    """
    return send_local_qwen_message(message)
    # return send_proxy_qwen_message(message)
    # return send_llm_req.get(config.USE_MODEL, send_local_qwen_message)(message)


def get_raw_slot(parameters):
    # 创建新的JSON对象
    output_data = {}
    for k, v in parameters.items():
        output_data[k] = v["value"]
    return output_data


def get_clear_slot(parameters):
    # 创建新的JSON对象
    output_data = {}
    for k, v in parameters.items():
        output_data[k] = []
    return output_data


def get_slot_extract_json(slot):
    # 创建新的JSON对象
    output_data = []
    for item in slot:
        new_item = {"name": item["name"], "desc": item["desc"], "value": item["value"]}
        output_data.append(new_item)
    return output_data


def get_slot_query_user_json(slot, scene_config):
    print("当前scene_config：", scene_config)
    # 创建新的JSON对象
    output_data = []
    for k, v in slot.items():
        if len(v) == 0:
            new_item = {"desc": scene_config["parameters"][k]["desc"], "value": []}
            output_data.append(new_item)
    return output_data


def update_slot(json_data, dict_target, user_input):
    """
    更新槽位slot参数
    """
    if len(json_data) == 0:
        return

    # -----当进入多轮对话，用户输入了一个不带时间的词语，大模型可能会幻觉预测出来新的时间
    if "time" in json_data.keys() and not contains_time(user_input):
        json_data["time"] = []
    # ------

    for k, v in json_data.items():
        # 检查value字段是否为空字符串
        if len(v) > 0 and k in dict_target.keys():
            for sub_v in v:
                if sub_v not in dict_target[k]:
                    dict_target[k].append(sub_v)

    # -----object和measurement这两个槽位不需要模型预测，只用规则
    if "object" in dict_target.keys():  # "object" 在的话 measurement 也在
        dict_target["object"], dict_target["measurement"] = get_object_measurement(dict_target["object"],
                                                                                   dict_target["measurement"],
                                                                                   user_input)

    # -----aggregation槽位不需要模型预测，只用规则
    if "aggregation" in dict_target.keys():  # 预留情况：可能有些场景需要object和measurement，但不需要aggregation
        dict_target["aggregation"] = get_object_aggregation(dict_target["aggregation"], user_input)

    # -----where槽位不需要模型预测，只用规则
    if "where" in dict_target.keys():  # 预留情况：可能有些场景需要object和measurement，但不需要aggregation
        dict_target["where"] = get_where(user_input)


def format_name_value_for_logging(json_data):
    """
    抽取参数名称和value值
    """
    log_strings = []
    for item in json_data:
        name = item.get('name', 'Unknown name')  # 获取name，如果不存在则使用'Unknown name'
        value = item.get('value', 'N/A')  # 获取value，如果不存在则使用'N/A'
        log_string = f"name: {name}, Value: {value}"
        log_strings.append(log_string)
    return '\n'.join(log_strings)


def extract_json_from_string(input_string):
    """
    JSON抽取函数
    返回包含JSON对象的列表
    """
    try:
        # 正则表达式假设JSON对象由花括号括起来
        matches = re.findall(r'\{.*?\}', input_string, re.DOTALL)

        # 验证找到的每个匹配项是否为有效的JSON
        valid_jsons = []
        for match in matches:
            try:
                json_obj = json.loads(match)
                valid_jsons.append(json_obj)
            except json.JSONDecodeError:
                continue  # 如果不是有效的JSON，跳过该匹配项

        return valid_jsons[0]
    except Exception as e:
        print(f"Error occurred，从模型输出提取json失败: {e}")
        return []


def contain_json(input_string):
    """
    判断句子是否包含json
    返回包含true or false
    """
    try:
        # 正则表达式假设JSON对象由花括号括起来
        matches = re.findall(r'\{.*?\}', input_string, re.DOTALL)
        if len(matches) == 0:
            return False
        else:
            return True

    except Exception as e:
        print(f"Error occurred: {e}")
        return []


object_list = ['收支余', '基金结余', '结算信息', '费用明细', '特殊病(医院)', '居民特殊病', '职工特殊病', '特殊病(病种)',
               '参保人数信息']

measurement_list = ['基金类型计数', '其他基金支付', '科室计数', '公务员补助', '治疗费', '住院床日',
                    '化验费', '经营性质计数', '累计基金结余', '单价', '基金支出', '统筹区计数',
                    '明细总额', '挂号费', '大额医疗补助', '医疗机构简称计数', '联系地址计数',
                    '医保办邮箱计数', '费用归并计数', '医院名称计数', '项目名称计数', '数量', '现金',
                    '结算id计数', '姓名计数', '就医地计数', '医保编码计数', '诊察费', '退休人数',
                    '就诊id计数', '机构性质计数', '病种计数', '参保总人数', '人员类别计数', '本年结余',
                    '人员编号计数', '床位费', '险种计数', '护理费', '卫生材料费', '医生计数', '年龄段计数',
                    '在职人数', '大病保险', '民政补助', '身份证号计数', '是否手动报销计数', '经营面积',
                    '一般诊疗费', '备付力', '统计日期计数', '医保办电话计数', '医院等级计数', '共济账户',
                    '账户支付数', '女职工人数', '统筹基金', '结算月份计数', '总费用', '丙类', '乙类自理',
                    '手术费', '检查费', '中药饮片费', '其他费', '结余金额', '基金收入', '数据条数',
                    '按病种收费', '账户支付', '中成药费', '医疗类别计数', '医疗机构名称计数', '西药费',
                    '符合医保内费用']

aggregation_list = ['合计', '平均', '最大值', '最小值']


def get_object_measurement(object_name, measurement_name, user_input):
    for obj in object_list:
        if obj in user_input:
            object_name = [obj]
            break

    for me in measurement_list:
        if me in user_input:
            measurement_name = [me]
            break

    return object_name, measurement_name  # 列表形式


def get_object_aggregation(aggregation_name, user_input):
    for agg in aggregation_list:
        if agg in user_input:
            aggregation_name = [agg]
            break

    return aggregation_name  # 列表形式


fr_where = open("utils/where_type.json", 'r', encoding='utf-8')
json_where = json.load(fr_where)


def get_where(user_input):
    direct_exist_word = []
    llm_exist_word = []

    # ------直接匹配（完全对应匹配）------ #
    for where_word in json_where.keys():
        if where_word in user_input:
            direct_exist_word.append(where_word)

    # ------LLM匹配（同义表达匹配）------ #
    message = scene_prompts.where_word_match_prompt.replace("{user_input}", user_input)
    match_json_result_by_llm = send_message(message)
    match_json_result = extract_json_from_string(match_json_result_by_llm)

    if isinstance(match_json_result, dict):
        for match_key, match_word_list in match_json_result.items():
            if isinstance(match_word_list, list):
                for match_word in match_word_list:
                    if match_word not in llm_exist_word and match_word in json_where.keys() and match_word not in direct_exist_word:
                        llm_exist_word.append(match_word)

    if len(llm_exist_word) > 0:
        llm_exist_word = Similarity_calculation(user_input, llm_exist_word)

    return direct_exist_word + llm_exist_word


def Similarity_calculation(sentence, where_word_list):
    # 设置阈值
    threshold = 0.4
    # 用于存储相似度高于阈值的词
    similar_words = []
    # 计算每个词与sentence的相似度
    print("进行相似度计算")
    print("句子：", sentence)
    print("需要计算词：", where_word_list)
    for word in where_word_list:

        embeddings1 = model.encode(word)
        embeddings2 = model.encode(sentence)
        cosine_similarity = util.cos_sim(embeddings1, embeddings2)
        similarity = cosine_similarity[0][0]

        if similarity > threshold:
            similar_words.append(word)

        print(word, ": ", similarity)
    return similar_words


def get_where_detail(where_word_list):
    where_list = []
    for where_word in where_word_list:
        if where_word in json_where.keys():
            where_list.append({"columnId": json_where[where_word]["columnId"],
                               "columnName": json_where[where_word]["columnName"],
                               "value": where_word})

    return where_list


fr_zhibiao = open("utils/zhibiao.json", 'r', encoding='utf-8')
json_zhibiao = json.load(fr_zhibiao)


def from_target_get_id(targetname):
    if targetname not in json_zhibiao.keys():
        return "-1"

    return json_zhibiao[targetname]["targetId"]


def from_group_get_id(targetname, group_list):

    group_with_id_list = []
    if targetname not in json_zhibiao.keys():
        for group_word in group_list:
            group_with_id_list.append({"columnId": "-1", "columnName": group_word})
        return group_with_id_list

    origin_group = json_zhibiao[targetname]["group"]
    for group_word in group_list:
        if group_word in time_word:
            group_with_id_list.append({"columnId": "-1", "columnName": group_word})
            continue
        elif group_word in origin_group.keys():
            group_with_id_list.append({"columnId": origin_group[group_word]["columnId"], "columnName": group_word})

    return group_with_id_list
