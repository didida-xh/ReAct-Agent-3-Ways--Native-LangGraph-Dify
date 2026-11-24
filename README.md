# ReAct 单智能体工具调用：三种实现

同一个智能体、同一组工具，用三种技术栈各实现一遍，用来对比「手写循环 → 框架编排 → 平台配置」在控制力、代码量和调试成本上的差异。

## 三种实现

| 目录 | 技术栈 | 循环由谁控制 | 工具接入方式 |
| --- | --- | --- | --- |
| `无框架/` | Python + OpenAI SDK | 自己写的 `for` 循环 | 直接调用 Python 函数 |
| `langgraph/` | LangGraph + langchain-openai | 图的边（`agent → tools → agent`） | `@tool` 包装 |
| `Dify/` | Dify + FastAPI | 平台内置 Agent 循环 | HTTP 接口 + OpenAPI 描述 |

三版的工具名、参数、描述完全一致，便于横向对比。

## 目录结构

```text
.
├── 无框架/                  # 纯原生 ReAct 循环实现
│   ├── llm.py               # OpenAI 兼容客户端
│   ├── tools.py             # 三个工具 + Schema + 注册表
│   ├── agent.py             # ReAct 主循环
│   ├── main.py              # CLI 入口（--demo / 单问 / 交互）
│   ├── requirements.txt
│   ├── .env.example
│   └── 知识库/              # 检索用文档（中英两版）
├── langgraph/               # LangGraph 实现
│   ├── llm.py
│   ├── tools.py
│   ├── agent.py             # StateGraph 定义
│   ├── main.py
│   └── requirements.txt
├── Dify/                    # Dify 平台版
│   ├── tool_server.py       # 把三个工具暴露成 HTTP 接口
│   ├── tools_openapi.json   # Dify 自定义工具的 OpenAPI 描述
│   └── README.md
└── 计划表.md
```

## 快速开始

### 1. 安装依赖

```bash
cd 无框架
python3 -m venv ../.venv
../.venv/bin/pip install -r requirements.txt

cd ../langgraph
../.venv/bin/pip install -r requirements.txt
```

Dify 版的工具服务还需要 FastAPI 和 uvicorn：

```bash
../.venv/bin/pip install fastapi uvicorn
```

### 2. 配置环境变量

复制模板并填入自己的 Key：

```bash
cp 无框架/.env.example 无框架/.env
```

| 变量 | 用途 |
| --- | --- |
| `DEEPSEEK_API_KEY` | 对话模型 Key |
| `DEEPSEEK_BASE_URL` | 默认 `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 默认 `deepseek-chat` |
| `DASHSCOPE_API_KEY` | 向量模型 Key（百炼） |
| `EMBEDDING_BASE_URL` | 默认 DashScope 兼容模式地址 |
| `EMBEDDING_MODEL` | 默认 `qwen3.7-text-embedding-flash` |

`.env` 已被 `.gitignore` 忽略，不会进仓库。

### 3. 运行

```bash
# 原生版
cd 无框架 && ../.venv/bin/python main.py --demo

# LangGraph 版
cd langgraph && ../.venv/bin/python main.py --demo

# Dify 版：先起工具服务，再到 Dify 里创建自定义工具和应用
cd .. && .venv/bin/python Dify/tool_server.py
```

单问一句：`python main.py "北京天气怎么样"`；不带参数则进入交互模式。

## 三个工具

| 工具名 | 参数 | 说明 |
| --- | --- | --- |
| `get_weather` | `city` | Open-Meteo 地理编码 + 实时天气，国外城市用英文名 |
| `calculate` | `expression` | AST 白名单求值，仅支持 `+ - * / % ( )` 和数字 |
| `search_knowledge_base` | `query`, `top_k` | 文档切块 + 向量化 + 余弦相似度检索 |

检索流程：读取 `知识库/llm-agents-survey-zh.md` → 固定长度切块 → 调用 embedding 接口生成向量 → 启动时缓存 → 提问时只对 query 编码一次，按点积排序取 Top-K。

## 设计要点

手写循环里最容易错的三件事，也是后面两个框架替你做的事：

1. 模型返回的 `tool_calls` 要**原样**回填进消息列表；
2. 工具结果的 `tool_call_id` 必须与调用请求一一对应；
3. 循环结束条件是**模型不再请求工具**，另设 `max_steps` 兜底防止死循环。

Dify 版的特殊性在于：平台不执行你的代码，只认 HTTP 接口，所以需要额外的 `tool_server.py` 与 OpenAPI 描述，详见 [Dify/README.md](Dify/README.md)。

## 常见问题

**天气查询报 `SSL_ERROR_SYSCALL` / 连接超时**
系统代理拦截了 Open-Meteo。`tools.py` 中使用 `httpx.Client(trust_env=False)` 直连解决。

**Dify 测试工具时报 SSRF 拦截**
默认禁止访问私有网段。需在 `dify/docker/.env` 中添加：

```dotenv
SSRF_PROXY_ALLOW_PRIVATE_DOMAINS=host.docker.internal
```

然后 `docker compose up -d ssrf_proxy` 重建代理容器。

**LangGraph 版报 `'AIMessage' object is not subscriptable`**
`graph.invoke()` 返回的是消息对象，取最终答案要用 `result["messages"][-1].content`，不能用 `["content"]`。

**检索结果不相关**
当前是固定 1000 字切块 + 纯向量检索，长文档容易语义稀释。改进方向是按段落/300 字切块，并对关键词命中做加权。

## 验收标准

同一组问题在三个版本中的结论应保持一致：

| 问题 | 预期 |
| --- | --- |
| 北京现在天气怎么样？ | 返回带小数的实时温度，非模型编造 |
| 帮我算 (23*4+10)/2 | 51 |
| 什么是 ReAct？ | 内容来自本地知识库文档 |
| 金华天气怎么样，顺便算 37*1.8+32 | 连续调用两个工具后汇总回答 |
