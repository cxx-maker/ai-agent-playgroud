import os 
import uuid
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import OpenAI,ChatOpenAI

import sqlite3
load_dotenv()
#第二步:memory 函数
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"memory.db")

def init_db():
    """建表"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions(
        id TEXT primary key,
        created_at TEXT NOT NULL
        )
    """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
        )
        """)
def save_message(session_id,role,content):
    """存一条消息"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES(?,?,?,?)",
            (session_id, role,content, datetime.now().isoformat())
        )

   
def load_history(session_id, limit=10):
    """读历史"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT role ,content FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT?",
            (session_id, limit)  

        )
        rows = cursor.fetchall()
        return [{"role":r[0],"content":r[1]} for r in rows]
@tool("web_search",description="搜索网络获取信息")
def web_search(query:str) -> str:
    """search the web for current information"""
    results = tavily.invoke(query)
    if isinstance(results,list):
        parts = []
        for i,r in enumerate(results,1):
            parts.append(
                f"[{i}] {r.get('title','')}\n"
                f"链接： {r.get('url','')}\n"
                f"摘要： {r.get('content','')}\n"
            )
        return "\n\n---\n\n".join(parts)
    return str(results)
 
#第三步Agent设置
tavily = TavilySearchResults(max_results=2, tavily_api_key=os.environ.get("TAVILY_API_KEY"))
SYSTEM_PROMPT = """
你是一个有记忆的 AI 助手，帮用户解决问题、记住重要的事,户会问"上次聊了什么"，你要从对话历史里找出来；用户问新问题时也要结合历史给连贯答案,
简洁实用，引用历史时说"你之前提过..."让对话自然,必要时可以调 web_search 查新信息"""
# model = ChatOpenAI(
#     model="MiniMax-M3",
#     api_key=os.environ.get("MiniMax_API_KEY"),
#     base_url=os.environ.get("MinMax_BASE_URL"),
# )
from langchain_deepseek import ChatDeepSeek

model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    timeout=60,
    max_retries=2,
)
agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=SYSTEM_PROMPT,
)
def chat_with_memory(user_message, history, session_id="user_001"):
    # 1. 加载历史
    past = load_history(session_id, limit=5)
    
    # 2. 构造 messages
    messages = []
    for msg in reversed(past):
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})
    
    # 3. 调 Agent
    result = agent.invoke({"messages": messages})
    assistant_message = result["messages"][-1].content
    
    # 4. 保存到 DB
    save_message(session_id, "user", user_message)
    save_message(session_id, "assistant", assistant_message)
    
    # 5. 只返回 Agent 的回复（Gradio 会自动追加到 history）
    return assistant_message

def chat_fn(message, history):
    """包装函数，给 Gradio 用"""
    return chat_with_memory(message, history, session_id="user_001")


demo = gr.ChatInterface(
    fn=chat_fn,
    title="🧠 有记忆的 AI 助手",
    description="**有长期记忆的 AI**——它会记住你们之前聊过什么。试试问它：你知道我上次问什么吗？",
    examples=[
        "你好，我叫小白",
        "我最喜欢 Python",
        "你还记得我叫什么吗？",
        "我最喜欢什么编程语言？",
    ],
)


if __name__ == "__main__":
    init_db()
    demo.launch()