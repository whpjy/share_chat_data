from scene_config import scene_prompts
from utils.helpers import send_message, extract_json_from_string


def ask_for_user_result(context):
    return {
        "type": "2",
        "value": {"key": []},
        "context": context,
        "history": []
    }


def query_main_data(universal_processors, user_input, is_MultiQA):

    messsge = scene_prompts.shijian_prompt.replace("{user_input}", user_input)
    result = send_message(messsge)
    result = extract_json_from_string(result)
    if len(result) == 0:
        ask_for_user_result("生成sql失败")

    if isinstance(result, dict):
        if 'result' in result.keys():
            return ask_for_user_result(result['result'])

    return ask_for_user_result("生成sql失败")

