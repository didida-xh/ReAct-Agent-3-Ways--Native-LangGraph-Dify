import json

from llm import chat
from tools import TOOL_REGISTRY, TOOL_SCHEMAS

SYSTEM_PROMPT = """你是一个会使用工具的助手。
规则：
1. 查询天气必须调用 get_weather；
2. 涉及数字计算必须调用 calculate，不要心算；
3. 涉及 ReAct、RAG、智能体、工具调用等概念时，调用 search_knowledge_base；
4. 工具返回 error 时，先根据错误信息修正参数再试；
5. 资料不足时直接说明，不要编造。
"""

def _execute_tool(tool_call: dict)->str:
    name=tool_call["function"]["name"]
    raw_args=tool_call["function"].get("arguments") or "{}"

    tool=TOOL_REGISTRY.get(name)
    if not callable(tool):
        return json.dumps({"error": f"未知工具：{name}"}, ensure_ascii=False)

    try:
        args=json.loads(raw_args)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"参数不是合法 JSON：{exc}"}, ensure_ascii=False)

    if not isinstance(args, dict):
        return json.dumps({"error": "参数必须是 JSON 对象"}, ensure_ascii=False)

    try:
        result=tool(**args)
    except TypeError as exc:
        return json.dumps({"error": f"参数不匹配：{exc}"}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": f"工具执行失败：{exc}"}, ensure_ascii=False)

    return json.dumps(result, ensure_ascii=False)

def run_agent(user_input: str,max_steps: int=5,verbose:bool=True) -> str:
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for step in range(1,max_steps+1):
        response=chat(messages,tools=TOOL_SCHEMAS)
        messages.append(response)

        tool_calls=response.get("tool_calls") or []
        if not tool_calls:
            return response.get("content") or ""

        for call in tool_calls:
            name=call["function"]["name"]
            args=call["function"].get("arguments","")
            if verbose:
                print(f"[第 {step} 轮] 调用 {name}({args})")

            result=_execute_tool(call)
            if verbose:
                print(f"[观察] {result[:200]}")

            messages.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": result,
            })
    return "工具调用次数超过上限，已停止。"


















