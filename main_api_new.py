from models.chatbot_model import ChatbotModel
from utils.helpers import load_all_scene_configs

from fastapi import FastAPI, HTTPException, Request
import uvicorn, json, datetime

app = FastAPI(reload=True)

chatbot_model = ChatbotModel(load_all_scene_configs())

# 定义接收 POST 请求的端点
@app.post("/v1/chat/completions")
async def receive_and_forward(request_data: dict):
    # 从请求数据中提取模型和消息
    messages = request_data.get("messages")
    question = messages[0]['content']
    role = messages[0]['role']
    if not question:
        return {"error": "No question provided"}

    response = chatbot_model.process_multi_question(question)

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7071)





