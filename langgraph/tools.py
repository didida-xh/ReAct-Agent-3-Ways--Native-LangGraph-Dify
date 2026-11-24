import importlib.util
import json
from pathlib import Path

from langchain_core.tools import tool


_NATIVE_PATH = Path(__file__).resolve().parent.parent / "无框架" / "tools.py"
_spec = importlib.util.spec_from_file_location("native_tools", _NATIVE_PATH)
_native = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_native)

@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气。国外城市请使用英文名。"""
    return json.dumps(_native.get_weather(city), ensure_ascii=False)

@tool
def calculate(expression: str) -> str:
    """计算数学表达式。涉及数字运算时必须使用本工具。"""
    return json.dumps(_native.calculate(expression), ensure_ascii=False)

@tool
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """检索本地综述中关于智能体、ReAct、RAG、工具调用的资料。"""
    return json.dumps(
        _native.search_knowledge_base(query, top_k),
        ensure_ascii=False,
    )