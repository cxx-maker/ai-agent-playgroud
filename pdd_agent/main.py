import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_XET"] = "1"
import os
import gradio as gr
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_deepseek import ChatDeepSeek
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

load_dotenv()


# === RAG 知识库（从 .md 文件加载）===
current_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(current_dir, "pdd_knowledge.md")

loader = TextLoader(md_path, encoding="utf-8")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(docs)
embeddings = FastEmbedEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)


@tool(
    "search_pdd_rules",
    description="查询拼多多平台规则手册。问任何 Pinduoduo 退款/卖家/物流/违规/买家保护/话术问题，必须调用此工具。",
)
def search_pdd_rules(query: str) -> str:
    """Search Pinduoduo platform rules."""
    results = vectorstore.similarity_search(query, k=3)
    parts = []
    for i, doc in enumerate(results, 1):
        parts.append(f"[片段 {i}]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


# === Web Search ===
tavily = TavilySearchResults(max_results=2, tavily_api_key=os.environ.get("TAVILY_API_KEY"))


@tool("web_search", description="搜索网络获取最新信息。问最新政策类问题（如'2026 新规'）时调用此工具。")
def web_search(query: str) -> str:
    """Search the web for current information."""
    results = tavily.invoke(query)
    if isinstance(results, list):
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(
                f"[{i}] {r.get('title', '')}\n"
                f"链接: {r.get('url', '')}\n"
                f"摘要: {r.get('content', '')}"
            )
        return "\n\n---\n\n".join(parts)
    return str(results)


# === System Prompt ===
SYSTEM_PROMPT = """你是拼多多客服助手，帮买家和卖家解决 Pinduoduo 相关问题。

工作方式：
- 用户问具体规则（怎么退款/运费/卖家义务等）→ 必须调 search_pdd_rules
- 用户问最新政策（2026 新规/最近变化）→ 调 web_search
- 用户问怎么回复买家 → search_pdd_rules 查话术部分

回答要简洁、有礼貌、专业。引用规则时可以说"根据 Pinduoduo 规则..."。"""


# === Agent ===
# model = ChatDeepSeek(
#     model="deepseek-chat",
#     api_key=os.environ.get("DEEPSEEK_API_KEY"),
#     timeout=60,
#     max_retries=2,
# )



model = ChatOpenAI(
    model="MiniMax-M3",
    api_key=os.environ.get("MiniMax_API_KEY"),
    base_url=os.environ.get("MiniMax_BASE_URL"),
    timeout=60,
)
agent = create_agent(
    model=model,
    tools=[search_pdd_rules, web_search],
    system_prompt=SYSTEM_PROMPT,
)


# === Chat Function ===
def chat_fn(message, history):
    """Gradio 聊天函数"""
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content


# === Gradio UI ===
demo = gr.ChatInterface(
    fn=chat_fn,
    title="🛒 拼多多客服助手",
    description="**智能客服**——内置 60+ 条 Pinduoduo 规则，能联网搜最新政策。",
    examples=[
        "我收到货不满意想退款怎么办？",
        "卖家 48 小时不回复我怎么办？",
        "拼多多 2026 最新退款政策是什么？",
        "我作为卖家，买家要退款我该怎么回复？",
    ],
)


if __name__ == "__main__":
    demo.launch()