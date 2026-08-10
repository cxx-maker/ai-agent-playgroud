import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_DISABLE_XET"] = "1"
import os 
import gradio as gr
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_deepseek import ChatDeepSeek
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel,Field

load_dotenv()
#=== Pydantic输出模型 ===
class MatchResult(BaseModel):
    """简历与岗位的匹配分析结果"""
    match_score: int = Field(description="整体匹配度，0-100")
    matching_skills: list[str] = Field(description="候选人已具备的，jd里要求的技能")
    missing_skills: list[str] = Field(description="jd要求但候选人未体现的技能")
    recommendations: list[str] = Field(description="给候选人的具体改进建议（3-5条）")
    summary:str = Field(description="一句话整体评价")

#===RAG读简历 ===
def build_resume_vectorstore(pdf_path):
    """读简历，建立向量库"""
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap = 100,
        separators=["\n\n","\n","。",",","?",""],
    )
    chunks = splitter.split_documents(pages)
    embeddings = FastEmbedEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    return Chroma.from_documents(documents=chunks,embedding=embeddings)

def make_retrieval_tool(vectorstore):
    @tool(
        "search_resume",
        description="从候选人简历中检索相关信息，分析匹配度时，必须用这个工具读简历内容",
    )
    def search_resume(query:str) ->str:
        results = vectorstore.similarity_search(query,k=3)
        parts = []
        for i, doc in enumerate(results,1):
            page = doc.metadata.get("page","?")
            parts.append(f"[片段 {i}，第 {page} 页]\n{doc.page_content}")
        return "\n\n---\n\n".join(parts)
    return search_resume
# === System Prompt ===
SYSTEM_PROMPT = """你是候选人求职的匹配度分析助手。

【你的工作流程】
1. 用户会提供：候选人的简历内容和岗位描述 JD
2. 你必须先调用 search_resume 工具读简历
3. 然后对比简历和 JD，给出分析

【评分标准】
- 90+：完美匹配，强烈推荐投递
- 70-89：较匹配，值得投递
- 50-69：一般匹配，有提升空间
- 30-49：匹配度低，建议补充相关经验
- 0-29：不匹配，建议另寻岗位

【你需要输出】（会按 MatchResult 结构自动填充）
- match_score: 整体匹配度（0-100）
- matching_skills: 候选人已具备的技能（JD里要求的）
- missing_skills: 候选人没有的技能（JD里要求的）
- recommendations: 3-5 条具体改进建议
- summary: 一句话整体评价

【特别注意】
- 必须基于简历实际内容，不要凭空编造
- missing_skills 是 JD 要求但简历没体现的，不是 JD 要求但候选人确定没有的
- recommendations 要具体可执行，比如"加一个 Flask 项目到简历"而不是"提升技能"
"""
#=== 模型配置 ===
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),

)
#=== 主分析函数 ===
def analyze_resume(pdf_file,jd_text,progress=gr.Progress()):
    progress(0.1,"读取简历...")
    if pdf_file is None:
        return "请上传PDF简历","","",""
    progress(0.3,"建立简历索引...")
    #把pdf转成vectorstore
    vectorstore = build_resume_vectorstore(pdf_file)
    #包成search_resume tool
    retrieval_tool = make_retrieval_tool(vectorstore)
    #创建带结构输出的agent
    agent = create_agent(
        model=model,
        tools=[retrieval_tool],
        system_prompt=SYSTEM_PROMPT,
        response_format=MatchResult,
    )
    progress(0.5,"agent分析中...")
    #调用agent传入jd
    result = agent.invoke({
        "messages":[{"role":"user","content":jd_text}]
    })
    #取出结构化结果
    match =result["structured_response"]
    progress(1.0,"完成")
    #返回5个字段
    return match.match_score,match.matching_skills,match.missing_skills,match.recommendations,match.summary


# ===：Gradio UI ===
with gr.Blocks(title="📋 简历匹配分析 Agent", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📋 简历匹配分析 Agent\n\n**上传简历 + 粘贴 JD，看匹配度**")

    with gr.Row():
        with gr.Column(scale=1):
            pdf_input = gr.File(
                label="📄 上传简历 PDF",
                file_types=[".pdf"],
            )
            jd_input = gr.Textbox(
                label="📝 粘贴岗位描述（JD）",
                lines=8,
                placeholder="把招聘网站的 JD 粘贴到这里...",
            )
            analyze_btn = gr.Button("🔍 分析匹配度", variant="primary", size="lg")

        with gr.Column(scale=2):
            score_md = gr.Markdown()
            matching_md = gr.Markdown()
            missing_md = gr.Markdown()
            recommendations_md = gr.Markdown()
            summary_md = gr.Markdown()

    analyze_btn.click(
        analyze_resume,
        inputs=[pdf_input, jd_input],
        outputs=[score_md, matching_md, missing_md, recommendations_md, summary_md],
    )


if __name__ == "__main__":
 demo.launch()