from scene_config import scene_prompts
from utils.date_utils import get_current_date
from knowledge_graph.kg_api import get_target_node, get_target_aggregation
from utils.helpers import (get_forcr_word, get_clean_text, get_group_word,
                           extract_limits, extract_compare, extract_rank,
                           check_and_fill_forcr_word, check_time,
                           check_group, contains_time, clear_group_and_compare_in_key,
                           check_key_and_group, from_target_get_id, from_group_get_id, get_where_detail)


def final_extract_result(universal_processors, data, user_input, is_MultiQA):
    key_list = data['key']
    key_list = check_and_fill_forcr_word(key_list, user_input)
    time_list = data['time']
    time_list = check_time(time_list)
    group_list = data['group']
    group_list = check_group(group_list, user_input)
    key_list, group_list = check_key_and_group(key_list, group_list)
    limits = extract_limits(user_input)
    compare = extract_compare(user_input)
    rank = extract_rank(user_input)
    key_list = clear_group_and_compare_in_key(key_list, group_list, compare)

    print("*****  where", data['where'])
    where_list = get_where_detail(data['where'])

    # -----------------基于知识图谱的多轮-------------------#
    object_name = data['object']
    measurement_name = data['measurement']
    aggregation_name = data["aggregation"]
    targetName = ''

    if len(object_name) == 0 and len(measurement_name) == 0:
        context = '''这个问题小助手还在学习中，您可以这样问，示例：查询今年1月到7月职工特殊病统筹基金合计按医院等级分析''',
        return ask_for_user_result(context)

    if len(object_name) > 0 and len(measurement_name) == 0:
        target_list = get_target_node(object_name[0])
        str_target_list = "，".join(target_list)
        context = '你想查询哪些指标呢？例如 ' + str_target_list
        return ask_for_user_result(context)

    if len(object_name) == 0 and len(measurement_name) > 0:
        target_list = get_target_node(measurement_name[0])
        if len(target_list) == 1:  # 虽然缺少查询对象，但此时关联的对象只有一个，因此不需要再问，直接返回
            universal_processors.slot["measurement"] = target_list[0]
            object_name = target_list[0]
        else:
            str_target_list = "，".join(target_list)
            context = '你想查询哪个对象呢？例如 ' + str_target_list
            return ask_for_user_result(context)

    if len(aggregation_name) == 0:  # 此时没有聚合方式，但是度量槽位必有值，检查该度量是否需要聚合
        aggregation_list = get_target_aggregation(measurement_name[0])
        if len(aggregation_list) != 0:  # 不为0说明需要聚合
            str_aggregation_list = "，".join(aggregation_list)
            context = '你想查询哪个聚合方式呢？例如 ' + str_aggregation_list
            return ask_for_user_result(context)

    if len(object_name) > 0:
        targetName = targetName + object_name[0] + '-'

    if len(measurement_name) > 0:
        targetName += measurement_name[0]

    if len(aggregation_name) > 0:
        targetName += aggregation_name[0]
    # -----------------基于知识图谱的多轮-------------------#

    time_flag = contains_time(user_input)
    if len(time_list) > 0 and is_MultiQA:
        time_flag = True

    if time_flag:  # 问题是否包含时间词
        return {
            "type": "1",
            "value": {
                "意图": "查询",
                "key": key_list,
                "time": time_list,
                "group": from_group_get_id(targetName, group_list),
                "target": {
                    "targetId": from_target_get_id(targetName),
                    "targetName": targetName
                },
                "where": where_list,
                "compare": compare,
                "rank": rank,
                "limits": limits
            },
            "context": "",
            "history": []
        }
    else:
        return ask_for_user_result(
            '请问您想要什么时间(如：今年1月到3月)的数据。')


def ask_for_user_result(context):
    return {
        "type": "2",
        "value": {"key": []},
        "context": context,
        "history": []
    }


def three_figures_and_one_table(universal_processors, user_input, is_MultiQA):

    user_input = get_clean_text(user_input)  # 将一些口语词转换成标准词，如 区域->统筹区
    messsge = scene_prompts.prompt_extract.replace("{current_data}", get_current_date())
    messsge = messsge.replace("{force_word}", str(get_forcr_word(user_input)))
    messsge = messsge.replace("{group_word}", str(get_group_word(user_input)))
    messsge = messsge.replace("{user_input}", user_input)

    result = universal_processors.process(messsge, user_input)
    if result['type'] == "extract_json":
        return final_extract_result(universal_processors, result['data'], user_input, is_MultiQA)

