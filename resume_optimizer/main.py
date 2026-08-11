import os
from pydantic import BaseModel,Field
import gradio as gr
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_deepseek import ChatDeepSeek
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_XET"] = "1"
load_dotenv()
tavily = TavilySearchResults(max_results=2, tavily_api_key=os.environ.get("TAVILY_API_KEY"))
class Improvement(BaseModel):
    section: str = Field(description="简历哪一段，比如'项目经验'或'工作描述'")
    before: str = Field(description="原文照抄，让用户知道改什么")
    after: str = Field(description="改完后的版本，要具体可执行")
    reason: str = Field(description="为什么这样改，1句话讲明白")


class ResumeAnalysis(BaseModel):
    overall_score: int = Field(description="简历整体评分：0-100")
    top_strengths: list[str] = Field(description="做得好3-5点")
    critical_weaknesses:list[str] = Field(description="必须改的1-2点")
    improvements: list[Improvement] = Field(description="具体改写建议，每条含原版+改版+原因")
    keywords_to_add: list[str] = Field(description="建议加的关键词，3-4个")
    formatting_tips: list[str] = Field(description="排版/格式建议：1-3条")
    summary:str = Field(description="一句话整体评价")
@tool(
    "search_resume",
    description="从候选人简历中检索相关内容。分析简历时，必须先调用这个工具读简历。",
)
def search_resume(query: str) -> str:
    """从候选人简历中检索内容。"""
    results = vectorstore.similarity_search(query, k=2)
    parts = []
    for i, doc in enumerate(results, 1):
        page = doc.metadata.get("page", "?")
        parts.append(f"[片段 {i}，第 {page} 页]\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)

@tool(
    "web_search",
    description="搜索互联网获取简历优化的最新最佳实践和行业标准。",
)
def web_search(query: str) -> str:
    """Search the web for current best practices."""
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
SYSTEM_PROMPT = """你是一个简历优化师有丰富的经验，读上万份简历，专门帮求职者改简历让HR喜欢
你必须先调用的工具才可以进行下面的内容，输出的格式必须是ResumeAnalysis的结构，找不到改进点也要说明，不可以瞎编"""
def analyze_resume(pdf_file,jd_text,progress=gr.Progress()):
    progress(0.1,"读取简历...")
    if pdf_file is None:
        return None,"请上传pdf简历","","","","",""
    progress(0.3,"建立简历索引...")
    loader = PyMuPDFLoader(pdf_file.name)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,chunk_overlap=100,
        separators=["\n\n","\n","。","?"," ",""],    
        )
    chunks = splitter.split_documents(pages)
    embeddings = FastEmbedEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        
    )
    global vectorstore
    vectorstore = Chroma.from_documents(documents=chunks,embedding=embeddings)

    progress(0.5,"Agent分析 中...")
    global search_resume
    agent = create_agent(
        model=model,
        tools=[search_resume,web_search],
        system_prompt=SYSTEM_PROMPT,
        response_format=ResumeAnalysis,
    )
    progress(0.8,"生成分析中...")
    user_msg = jd_text if jd_text else "请分析这份简历的整体质量"
    result = agent.invoke({
        "messages":[{"role":"user","content":user_msg}] 
              })
    analysis = result["structured_response"]
    progress(1.0,"完成")
    return(
        analysis.overall_score,
        analysis.top_strengths,
        analysis.critical_weaknesses,
        analysis.improvements,
        analysis.keywords_to_add,
        analysis.formatting_tips,
        analysis.summary,

    )
model = ChatOpenAI(
    model="MiniMax-M3",  
    api_key=os.environ.get("MiniMax_API_KEY"),
    base_url=os.environ.get("MiniMax_BASE_URL"),
)
custom_css = """
.score-low { color: #ff4444; font-size: 48px; font-weight: bold; }
.score-mid { color: #ffaa00; font-size: 48px; font-weight: bold; }
.score-high { color: #00aa44; font-size: 48px; font-weight: bold; }
.improvement-card { 
    background: #f5f5f5; 
    border-left: 4px solid #4a90e2; 
    padding: 12px; 
    margin: 8px 0; 
    border-radius: 4px;
}
"""

def format_score(score):
    if score < 60:
        return f'<div class="score-low">{score} / 100</div>'
    elif score < 80:
        return f'<div class="score-mid">{score} / 100</div>'
    else:
        return f'<div class="score-high">{score} / 100</div>'


def format_improvements(improvements):
    if not improvements:
        return "暂无具体改写建议"
    parts = []
    for imp in improvements:
        parts.append(f"""<div class="improvement-card">
<strong>📍 {imp.section}</strong><br>
<strong>原版：</strong><br><blockquote>{imp.before}</blockquote>
<strong>建议：</strong><br><blockquote>{imp.after}</blockquote>
<em>💡 原因：{imp.reason}</em>
</div>""")
    return "<br>".join(parts)

call_count = {"n": 0}

def analyze_with_format(pdf_file, jd_text, progress=gr.Progress()):
    call_count["n"] += 1
    if call_count["n"] > 5:
        return "⚠️ 演示版已用完 5 次，让作者重新启动程序", "", "", "", "", "", ""
    """包装函数：把 analyze_resume 的结果格式化"""
    score, strengths, weaknesses, improvements, keywords, formatting, summary = analyze_resume(
        pdf_file, jd_text, progress
    )
    if isinstance(score, str):
        return score, "", "", "", "", "", ""
    return (
        format_score(score),
        f"## ✅ 你的优势\n\n" + "\n".join(f"- {s}" for s in strengths),
        f"## ⚠️ 必须改的问题\n\n" + "\n".join(f"- {w}" for w in weaknesses),
        f"## 💡 具体改写建议\n\n{format_improvements(improvements)}",
        f"## 🔑 建议加的关键词\n\n" + ", ".join(f"`{k}`" for k in keywords),
        f"## 📐 排版建议\n\n" + "\n".join(f"- {t}" for t in formatting),
        f"## 📝 整体评价\n\n{summary}",
    )


with gr.Blocks(title="📋 简历优化 AI", theme=gr.themes.Soft(), css=custom_css) as demo:
    gr.Markdown("""
# 📋 AI 简历优化师

**5 秒读你的简历，给出 HR 爱看的改写建议**

支持：✅ 简历评分  ✅ 优势分析  ✅ 改写示例  ✅ 关键词  ✅ 排版建议
""")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📥 输入")
            pdf_input = gr.File(label="简历 PDF", file_types=[".pdf"])
            jd_input = gr.Textbox(
                label="目标 JD（可选）",
                lines=4,
                placeholder="粘贴招聘 JD，AI 会针对性优化..."
            )
            analyze_btn = gr.Button("🔍 开始优化", variant="primary", size="lg")
            
            gr.Markdown("### 💡 快速开始（点下方按钮）")
            gr.Examples(
                examples=[[None, "Python 后端工程师，熟悉 Flask、Django、MySQL、Redis，3 年以上经验"]],
                inputs=[pdf_input, jd_input],
            )
        
        with gr.Column(scale=2):
            gr.Markdown("### 📊 分析结果")
            score_md = gr.HTML()
            
            with gr.Tabs():
                with gr.Tab("✅ 优势"):
                    strengths_md = gr.Markdown()
                with gr.Tab("⚠️ 问题"):
                    weaknesses_md = gr.Markdown()
                with gr.Tab("💡 改写示例"):
                    improvements_md = gr.HTML()
                with gr.Tab("🔑 关键词"):
                    keywords_md = gr.Markdown()
                with gr.Tab("📐 排版"):
                    formatting_md = gr.Markdown()
                with gr.Tab("📝 总结"):
                    summary_md = gr.Markdown()
    
    analyze_btn.click(
        analyze_with_format,
        inputs=[pdf_input, jd_input],
        outputs=[score_md, strengths_md, weaknesses_md, improvements_md,
                 keywords_md, formatting_md, summary_md],
    )


if __name__ == "__main__":
    demo.launch()
