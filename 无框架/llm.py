import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
# 优先用本目录的 .env，找不到就用上层的（仓库统一放一份）
for _env_path in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
    if _env_path.exists():
        load_dotenv(_env_path)
        break

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    http_client=httpx.Client(trust_env=False, timeout=60),
)

def chat(messages,tools=None,temperature=0.0)-> dict:
    """调用一次模型，返回 assistant 消息字典。"""
    kwargs={
        "model":MODEL,
        "messages":messages,
        "temperature":temperature,
    }
    if tools:
        kwargs["tools"]=tools

    response=_client.chat.completions.create(**kwargs)
    return response.choices[0].message.model_dump(exclude_none=True)
