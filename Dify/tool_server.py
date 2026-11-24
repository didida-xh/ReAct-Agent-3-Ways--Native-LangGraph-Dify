"""把 无框架/tools.py 的三个工具暴露成 HTTP 接口，供 Dify 自定义工具调用。"""

import importlib.util
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Query

# 按绝对路径加载原生工具，避免和 langgraph/tools.py 重名冲突
BASE = Path(__file__).resolve().parent
NATIVE_TOOLS = BASE.parent / "无框架" / "tools.py"

_spec = importlib.util.spec_from_file_location("native_tools", NATIVE_TOOLS)
native_tools = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(native_tools)

app = FastAPI(title="ReAct Tools API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/weather")
def weather(city: str = Query(..., description="城市名，如：北京、New York")):
    return native_tools.get_weather(city)

@app.get("/calculate")
def calculate(expression: str = Query(..., description="数学表达式，如：(23*4+10)/2")):
    return native_tools.calculate(expression)

@app.get("/kb")
def kb(
    query: str = Query(..., description="检索问题或关键词"),
    top_k: int = Query(3, ge=1, le=10, description="返回条数"),
):
    return native_tools.search_knowledge_base(query, top_k)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)