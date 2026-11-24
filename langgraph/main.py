import argparse
import sys

from agent import run_agent

import warnings

warnings.filterwarnings("ignore", message=".*allowed_objects.*")

DEMO_QUESTIONS = [
    "金华天气怎么样？",
    "金华现在多少华氏度？",
    "帮我算一下 (23*4+10)/2",
    "什么是 ReAct？",
]

def ask(question: str) -> None:
    print(f"\n用户：{question}")
    try:
        answer = run_agent(question)
    except Exception as exc:
        print(f"助手：调用失败（{type(exc).__name__}: {exc}）", file=sys.stderr)
        return
    print(f"助手：{answer}")

def run_interactive() -> None:
    print("输入问题开始对话；/exit 退出。每次提问独立，不保留上下文。")
    while True:
        try:
            question = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            return

        if not question:
            continue
        if question in {"/exit", "/quit"}:
            print("已退出。")
            return
        if question == "/reset":
            print("当前每次提问都是独立会话，没有需要清空的上下文。")
            continue

        ask(question)

def main() -> None:
    parser = argparse.ArgumentParser(description="LangGraph 版 ReAct 单智能体")
    parser.add_argument("question", nargs="?", help="只问一次，然后退出")
    parser.add_argument("--demo", action="store_true", help="运行内置示例问题")
    args = parser.parse_args()

    if args.demo:
        for question in DEMO_QUESTIONS:
            ask(question)
    elif args.question:
        ask(args.question)
    else:
        run_interactive()

if __name__ == "__main__":
    main()