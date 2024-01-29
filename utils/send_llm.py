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
    headers = {
        "Authorization": f"Bearer {config.TONGYI_PROXY_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "qwen-turbo",
        "messages": [
            {"role": "system", "content": "你是个乐于助人的助手."},
            {"role": "user", "content": f"{message}"}
        ]
    }

    try:
        response = requests.post(config.Qwen_URL, headers=headers, json=data, verify=False)
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