# encoding=utf-8
import logging
import json
import time

from scene_processor.scene_processor import SceneProcessor
from utils.helpers import get_raw_slot, update_slot, format_name_value_for_logging, is_slot_fully_filled_choujiang, send_message, \
    extract_json_from_string, check_current_values
from utils.helpers import get_slot_query_user_json
from scene_config import scene_prompts


class CommonProcessor(SceneProcessor):
    def __init__(self, scene_config):
        parameters = scene_config["parameters"]
        self.scene_config = scene_config
        self.scene_name = scene_config["name"]
        self.slot_template = get_raw_slot(parameters)
        self.slot = get_raw_slot(parameters)

    def process(self, message, user_input):
        # 处理用户输入，更新槽位，检查完整性，以及与用户交互
        # 先检查本次用户输入是否有信息补充，保存补充后的结果   编写程序进行字符串value值diff对比，判断是否有更新
        time1 = time.time()
        new_info_json_raw = send_message(message)
        time2 = time.time()
        print("用时", time2 - time1, "秒: 基于LLM信息抽取")
        current_values = extract_json_from_string(new_info_json_raw)
        if self.scene_name == "抽奖" and len(current_values) > 0:
            current_values = check_current_values(current_values, user_input)
        update_slot(current_values, self.slot, user_input)
        if self.scene_name == "抽奖":
            # 判断参数是否已经全部补全
            print("当前slot: ", self.slot)
            if is_slot_fully_filled_choujiang(self.slot):
                return self.respond_with_complete_data()
            else:
                return self.ask_user_for_missing_data(scene_prompts.prompt_query_user, self.scene_name)

        return self.respond_with_complete_data()

    def respond_with_complete_data(self):
        # 当所有数据都准备好后的响应
        json_data = {"type": 'extract_json', "data": self.slot}
        return json_data

    def ask_user_for_missing_data(self, prompt_query_user, scene_name):
        message = prompt_query_user.format(scene_name,
                                           json.dumps(get_slot_query_user_json(self.slot, self.scene_config), ensure_ascii=False))
        # 请求用户填写缺失的数据
        time1 = time.time()
        result = send_message(message)
        time2 = time.time()
        print("用时", time2 - time1, "秒: 基于LLM询问缺失信息")
        return {"type": 'ask_user_for_missing_data', "data": result}
