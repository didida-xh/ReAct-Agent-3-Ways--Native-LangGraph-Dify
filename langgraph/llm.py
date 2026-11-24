import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")

llm = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    temperature=0,
    http_client=httpx.Client(trust_env=False, timeout=60),
)