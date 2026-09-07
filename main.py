# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import uuid

app = FastAPI()

# Разрешаем запросы с любых сайтов (для теста)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AUTH_KEY = os.environ["GIGACHAT_AUTH_KEY"]

@app.post("/ask")
async def ask(request: dict):
    user_message = request.get("message", "")
    
    token_res = requests.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {AUTH_KEY}"
        },
        data="scope=GIGACHAT_API_PERS"
    )
    if token_res.status_code != 200:
        return {"reply": "Ошибка авторизации"}

    access_token = token_res.json()["access_token"]

    chat_res = requests.post(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": "Ты — ЭлектроМишка 🐻⚡. Отвечай кратко и дружелюбно."},
                {"role": "user", "content": user_message}
            ]
        }
    )
    if chat_res.status_code != 200:
        return {"reply": "Ошибка GigaChat"}

    reply = chat_res.json()["choices"][0]["message"]["content"]
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
