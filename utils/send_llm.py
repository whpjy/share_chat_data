# encoding=utf-8
import requests
import config

def send_local_qwen_message(message):
    """
    请求chatGPT函数
    """
    print('--------------------------------------------------------------------')
    if config.DEBUG:
        print('请求LLM的完整问题:', message)
    print('----------------------------------')

    data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "system", "content": "你是个乐于助人的助手."},
            {"role": "user", "content": f"{message}"}
        ],
        "stream" : False
    }

    try:
        response = requests.post(config.Qwen_URL,json=data, verify=False)
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]['content']
            print('LLM输出:', answer)
            print('--------------------------------------------------------------------')
            return answer
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None


# def send_local_qwen_message(message):
#
#     print('--------------------------------------------------------------------')
#     if config.DEBUG:
#         print('请求LLM的完整问题:', message)
#     print('----------------------------------')
#
#     data = {
#         "model": "Qwen1.5-14B-Chat-GPTQ-Int4",
#         "messages": [{"role": "user", "content": message, "temperature": 0}],
#         "top_p": 0.95,
#         'stream': False
#     }
#     try:
#         response = requests.post(config.Qwen_URL, json=data)
#         if response.status_code == 200:
#             answer = response.json()['response']
#
#             if len(answer) == 1:
#
#                 print('LLM输出:', answer[0])
#                 print('--------------------------------------------------------------------')
#                 return answer[0]
#             return answer
#
#         else:
#             print(f"Error: {response.status_code}")
#             return None
#
#     except requests.RequestException as e:
#         print(f"Request error: {e}")
#         return None


def send_proxy_qwen_message(message):
    """
    请求chatGPT函数
    """
    print('--------------------------------------------------------------------')
    if config.DEBUG:
        print('请求LLM的完整问题:', message)
    print('----------------------------------')
    headers = {
        "Authorization": f"Bearer {config.TONGYI_PROXY_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "qwen-turbo",
        "input":{
            "messages": [
            {"role": "system", "content": "你是个乐于助人的助手."},
            {"role": "user", "content": f"{message}"}
           ]
         },
         "parameters": {
             "result_format":"message",
         },
    }

    try:
        response = requests.post(config.Qwen_PROXY_URL, headers=headers, json=data, verify=False)
        if response.status_code == 200:
            answer = response.json()["output"]["choices"][0]["message"]['content']
            print('LLM输出:', answer)
            print('--------------------------------------------------------------------')
            return answer
        else:
            print(f"Error: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None