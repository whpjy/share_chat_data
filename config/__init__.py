print("Config package initialized.")

DEBUG = True

# MODEL ------------------------------------------------------------------------

USE_MODEL = 'Qwen_PROXY'  # 「Qwen, Qwen_PROXY」

# OpenAI https://api.openai.com/v1/chat/completions
GPT_URL = 'api.openai.com/v1/chat/completions'
API_KEY = 'sk-xxxxxx'

# Qwen
Qwen_URL = 'http://192.168.110.160:8080/v1/chat/completions'

Qwen_PROXY_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
TONGYI_PROXY_API_KEY = 'sk-80975e8b9fba4035934888ca454e6c75'
# MODEL ------------------------------------------------------------------------

# CONFIGURATION ------------------------------------------------------------------------

# 意图相关性判断阈值0-1
RELATED_INTENT_THRESHOLD = 0.5

# CONFIGURATION ------------------------------------------------------------------------
