from scene_config import scene_prompts
from utils.date_utils import get_current_date
from utils.helpers import (get_forcr_word, get_clean_text, get_group_word,
                           extract_limits, extract_compare, extract_rank,
                           check_and_fill_forcr_word, check_time,
                           check_group, contains_time, clear_group_and_compare_in_key,
                           get_clear_slot)


def final_extract_result(universal_processors, data):
    awards_name = data["奖项名称"][-1]
    awards_count = data["中奖人数"][-1]
    result = {
        "type": '2',
        "value": [{"奖项名称": awards_name, "中奖人数": awards_count}],
        "context": str({"奖项名称": awards_name, "中奖人数": awards_count}),
    }
    get_clear_slot(universal_processors.slot) # 完整返回后清空槽位

    return result


def ask_for_user_result(context):
    return {
        "type": "2",
        "value": {"key": []},
        "context": context,
        "history": []
    }

def chou_jiang(universal_processors, user_input, last_llm_answer):
    if len(universal_processors.slot["奖项名称"]) > 0 or len(universal_processors.slot["中奖人数"]) > 0:
        user_input = last_llm_answer+' -> '+user_input + ''

    messsge = scene_prompts.choujiang_prompt.replace("{user_input}", user_input)

    result = universal_processors.process(messsge, user_input)
    if result['type'] == "extract_json":
        return final_extract_result(universal_processors, result['data'])
    elif result['type'] == "ask_user_for_missing_data":
        return ask_for_user_result(result['data'])
