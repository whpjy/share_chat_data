# encoding=utf-8
import json
import logging
from config import RELATED_INTENT_THRESHOLD
from scene_processor.impl.common_processor import CommonProcessor
from utils.data_format_utils import extract_continuous_digits, extract_float
from utils.helpers import send_message, contain_json, get_clear_slot
from scene_processor_detail.deal_three_figures_and_one_table import three_figures_and_one_table
from scene_processor_detail.deal_fluctuation_analysis import fluctuation_analysis
from scene_processor_detail.deal_trend_chart import trend_chart
from scene_processor_detail.deal_histogram_chart import histogram_chart
from scene_processor_detail.deal_pie_chart import pie_chart
from scene_processor_detail.deal_product_percent import product_percent
from scene_processor_detail.deal_query_main_data import query_main_data
import time


class ChatbotModel:
    def __init__(self, scene_templates: dict):
        self.scene_templates: dict = scene_templates
        self.current_purpose: str = ''
        self.processors = {}
        self.last_llm_answer = ''

    @staticmethod
    def load_scene_processor(self, scene_config):
        try:
            return CommonProcessor(scene_config)
        except (ImportError, AttributeError, KeyError):
            raise ImportError(f"未找到场景处理器 scene_config: {scene_config}")

    def is_related_to_last_intent(self, user_input):
        """
        判断当前输入是否与上一次意图场景相关
        """
        if not self.last_llm_answer:
            return False
        prompt = (f"您将收到一个句子A和句子B。"
                  f"句子A: {self.last_llm_answer}。"
                  f"句子B: {user_input}。"
                  f"确定句子B是对句子A提出的问题的回答。"
                  f"请以0.0到1.0的得分来表示您的确定程度。"
                  f"如果你无法确定或判断，请返回0.0")
        time1 = time.time()
        result = send_message(prompt)
        time2 = time.time()
        print("用时", time2 - time1, "秒: 基于LLM判断当前输入是否是补充回答")
        print(extract_float(result))
        return extract_float(result) > RELATED_INTENT_THRESHOLD

    def recognize_intent(self, user_input):

        # 根据场景模板生成选项
        purpose_options = {}
        purpose_description = {}
        index = 0
        for template_key, template_info in self.scene_templates.items():
            purpose_options[str(index)] = template_key
            purpose_description[str(index)] = template_info["description"]
            index += 1
        options_prompt = "\n".join([f"{key}. {value} - 请回复{key}" for key, value in purpose_description.items()])

        # 发送选项给用户
        time1 = time.time()

        user_choice = send_message(
            f"有下面多种场景，需要你根据用户输入选择最合适的一个，只答选项\n{options_prompt}\n用户输入：{user_input}\n请回复序号：")

        time2 = time.time()
        print("用时", time2 - time1, "秒: 基于LLM意图识别")

        user_choices = extract_continuous_digits(user_choice)

        if "对比" in user_input or "比较" in user_input:
            print("LLM意图识别错误！启用规则识别")
            user_choices = ['6']

        if user_choices[0] in ['2', '3', '8', '9']:
            user_choices = ['1']

        # 根据用户选择获取对应场景
        if user_choices:
            self.current_purpose = purpose_options[user_choices[0]]

        if self.current_purpose:
            print(f"模型匹配了场景：{self.scene_templates[self.current_purpose]['name']}")
            # 这里可以继续处理其他逻辑
        else:
            # 用户输入的选项无效的情况，可以进行相应的处理
            print("意图分析失败")

    def get_processor_for_scene(self, scene_name):
        if scene_name in self.processors:
            return self.processors[scene_name]

        scene_config = self.scene_templates.get(scene_name)
        if not scene_config:
            raise ValueError(f"未找到名为{scene_name}的场景配置")

        processor_class = self.load_scene_processor(self, scene_config)
        self.processors[scene_name] = processor_class
        return self.processors[scene_name]

    def is_thematic_analysis(self, user_input):
        if "特殊病" in user_input:
            return {
                "type": '3',
                "value": {"key": ["特殊病"]},
                "context": "",
                "history": []
            }
        if "统筹基金" in user_input:
            return {
                "type": '3',
                "value": {"key": ["统筹基金"]},
                "context": "",
                "history": []
            }

    def process_multi_question(self, user_input):

        if "见解" in user_input or "洞察" in user_input:
            if "特殊病" in user_input or "统筹基金" in user_input:
                return self.is_thematic_analysis(user_input)

        is_MultiQA = False
        time_all_1 = time.time()
        if self.last_llm_answer == '':  # 如果LLM上次回答包含json，那么就不是在询问用户问题，则本次用户输入是新问题
            # 不相关时，重置self.processors，重新识别意图
            if self.current_purpose:
                self.processors[self.current_purpose].slot = get_clear_slot(
                    self.scene_templates.get(self.current_purpose)["parameters"])
            self.recognize_intent(user_input)  # 更新 self.current_purpose
        else:
            # 检查LLM是否在询问问题和当前用户输入是否是在回答该问题，也时唯一进入多轮的条件
            if self.is_related_to_last_intent(user_input):
                print('***用户在回答LLM提出的问题，进入多轮')
                is_MultiQA = True

            else:
                # 用户没有回答问题也要重新识别意图
                print(user_input, "-------------****-----")
                if self.current_purpose:
                    self.processors[self.current_purpose].slot = get_clear_slot(
                        self.scene_templates.get(self.current_purpose)["parameters"])
                self.recognize_intent(user_input)  # 更新 self.current_purpose

        if self.current_purpose == 'invalid_scene':
            self.current_purpose = ''
            return {
                "type": "2",
                "value": {"key": []},
                "context": '''这个问题小助手还在学习中，您可以这样问，示例：查询今年1月到7月职工特殊病统筹基金合计按医院等级分析''',
                "history": []
            }

        if self.current_purpose in self.scene_templates:
            # 根据场景模板调用相应场景的处理逻辑
            self.get_processor_for_scene(self.current_purpose)  # 更新 self.processors[self.current_purpose]
        else:
            return '意图分析失败'

        universal_processors = self.processors[self.current_purpose]
        # 三图一表
        if self.current_purpose == 'three_figures_and_one_table':
            result = three_figures_and_one_table(universal_processors, user_input, is_MultiQA)
            print("result: ", result)
            self.last_llm_answer = result["context"]
            time_all_2 = time.time()
            time_all = ' (共用时：' + str(time_all_2 - time_all_1) + "s)"
            return result

        # 波动分析
        elif self.current_purpose == 'fluctuation_analysis':
            result = fluctuation_analysis(universal_processors, user_input, is_MultiQA)
            print("result: ", result)
            self.last_llm_answer = result["context"]
            time_all_2 = time.time()
            time_all = ' (共用时：' + str(time_all_2 - time_all_1) + "s)"
            return result

        # 趋势图
        elif self.current_purpose == 'trend_chart':
            result = trend_chart(universal_processors, user_input, is_MultiQA)
            print("result: ", result)
            self.last_llm_answer = result["context"]
            time_all_2 = time.time()
            time_all = ' (共用时：' + str(time_all_2 - time_all_1) + "s)"
            return result

        # 柱状图
        elif self.current_purpose == 'histogram_chart':
            result = histogram_chart(universal_processors, user_input, is_MultiQA)
            print("result: ", result)
            self.last_llm_answer = result["context"]
            time_all_2 = time.time()
            time_all = ' (共用时：' + str(time_all_2 - time_all_1) + "s)"
            return result

        # 饼图
        elif self.current_purpose == 'pie_chart':
            result = pie_chart(universal_processors, user_input, is_MultiQA)
            print("result: ", result)
            self.last_llm_answer = result["context"]
            time_all_2 = time.time()
            time_all = ' (共用时：' + str(time_all_2 - time_all_1) + "s)"
            return result

        # 主数据查询
        elif self.current_purpose == 'query_main_data':
            result = query_main_data(universal_processors, user_input, is_MultiQA)
            print("result: ", result)
            self.last_llm_answer = result["context"]
            time_all_2 = time.time()
            time_all = ' (共用时：' + str(time_all_2 - time_all_1) + "s)"
            # return result
            return self.last_llm_answer

        # 产品合格率
        elif self.current_purpose == 'product_percent':
            result = product_percent(universal_processors, user_input, is_MultiQA)
            print("result: ", result)
            self.last_llm_answer = result["context"]
            time_all_2 = time.time()
            time_all = ' (共用时：' + str(time_all_2 - time_all_1) + "s)"
            return result

        elif self.current_purpose == 'invalid_scene':
            return '这个问题不在我的知识范围内'
