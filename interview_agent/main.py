# import os
# from dotenv import load_dotenv
# from langchain.tools import tool
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_deepseek import ChatDeepSeek
# from langchain.agents import create_agent


# load_dotenv()
# #===工具:联网搜索===
# tavily = TavilySearchResults(max_results=5,tavily_api_key=os.environ.get("TAVILY_API_KEY"))
# @tool(
#     "web_search",
#     description="搜索网络获取最新面试题和考察重点，当用户让你出面试题时，必须先用这个工具搜索该岗位的真实面试题，比如‘AI算法工程师 面试题2026’。返回前5条结果的标题，连接和摘要")
# def web_search(query: str) -> str:
#     """Search the web using Tavily"""
#     results =tavily.invoke(query)
#     if isinstance(results,list):
#         parts = []
#         for i ,r in enumerate(results,1):
#             title = r.get("title","")
#             url = r.get("url","")
#             content = r.get("content","")
#             parts.append(f"[{i}] {title}\n链接： {url}\n摘要： {content}")
#             return "\n\n---\n\n".join(parts)
#         return str(results)
# #===系统提示词===
# SYSTEM_PROMPT = """你是一个资深的互联网公司技术面试官，专门根据岗位描述（JD）生成结构化的面试题。
    
# 【工作流程】
# 1. 仔细阅读用户提供的 JD，提取：岗位名称、核心技术栈、经验要求
# 2. 必须先调用 web_search 搜索该岗位的真实面试题（如"AI算法工程师 面试题 2026"）
# 3. 基于 JD + 搜索结果，生成 10 道面试题

# 【题目分类】
# - 基础题（30%）：核心概念、基础知识
# - 项目题（40%）：实际项目经验、解决问题
# - 算法题（30%）：编程、算法、逻辑

# 【每题格式】
# ### [题号]. [题干]
# **参考答案**：[详细专业的答案]
# **难度**：⭐ 简单 / ⭐⭐ 中等 / ⭐⭐⭐ 困难

# 【输出要求】
# - Markdown 格式，分类清晰
# - 题目要紧贴 JD 提到的技术栈
# - 必须基于真实资料，不能凭空编造"""


# #===模型 + agent===
# model = ChatDeepSeek(
#     model="deepseek-chat",
#     api_key=os.environ.get("DEEPSEEK_API_KEY"),
# )
# agent = create_agent(
#     model = model,
#     tools=[web_search],
#     system_prompt=SYSTEM_PROMPT,
# )
#     #尝试的过程"
#     # tool = TavilySearchResults(max_results=5)
#     # return str(tool.invoke(query))
#     # """search bing china for current information."""
#     # try:
#     #     headers =  {
#     #     "User-Agent":'Mozilla/5.0(Window NT 10.0;Win64; x64) AppleWebKit/537.36 (KHTML.like Gecko) Chrome/120.0.0.0Safari/537.36',
#     #     "Accept-Language":"zh-CH,zh;q={query}",
#     #     }
#     #     url =f"https://cn.bing.com/search?1={quote(query)}"
#     #     resp = httpx.get(url,headers=headers,timeout=10,follow_redirects=True)
#     #     resp.raise_for_status()

#     #     soup = BeautifulSoup(resp.text,"html.parser")

#     #     results = []

#     #     for algo in soup.select(".b_algo")[:5]:
#     #         title_elem = algo.select_one("h2 a")
#     #         snippet_elem = algo.select_one("p")
#     #         if title_elem:
               
#     #            title = title_elem.get_text(strip=True)
#     #            link = title.get("href","")
#     #            snippet =snippet_elem.get(strip=True) if snippet_elem else "无摘要"
#     #            results.append(
                   
#     #               f"[{len(results) + 1}] {title}\n"
#     #               f"链接：{link}\n"
#     #               f"摘要：{snippet}"
#     #        )
#     #     if not results:
#     #             return "未找到搜索结果"
#     #     return "\n\n--\n\n".join(results)
#     # except Exception as e :
#     #      return f"搜索出错：{type(e)/__name__}: {e}"
# #==聊天循环===
# if __name__ =="__main__":
#     print("面试题生成 Agent 已启动")
#     print("输入 JD 文本，Agent 会自动搜索并出题")
#     print("输入 exit 退出")
#     print("=" * 50)

#     history = []
#     while True:
#         user_input = input("\n你: ").strip()
#         if user_input.lower() in ["exit", "quit"]:
#             break
#         if not user_input:
#             continue

#         # 自动加上出题指令
#         if "出题" not in user_input and "面试" not in user_input:
#             user_input = f"请根据以下 JD 生成 10 道面试题：\n\n{user_input}"

#         history.append({"role": "user", "content": user_input})
#         result = agent.invoke({"messages": history})
#         history = result["messages"]

#         print("\n" + "=" * 50)
#         print(history[-1].content)
import os
import json
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_deepseek import ChatDeepSeek

load_dotenv()

# === 预设 JD 库（一键模式用） ===
PRESET_JDS = {
    "AI算法工程师": """岗位职责：
1. 负责计算机视觉/深度学习算法的研发与优化
2. 使用 PyTorch 训练和部署目标检测、图像分类等模型

任职要求：
1. 硕士及以上学历，计算机/数学/电子相关专业
2. 熟练掌握 Python、PyTorch、NumPy
3. 有 YOLO、Transformer实战经验""",

    "Python后端": """岗位职责：
1. 负责后端服务的设计、开发和维护
2. 使用 Flask/Django/FastAPI 构建 RESTful API
3. 数据库设计与优化

任职要求：
1. 本科及以上，3年以上 Python 开发经验
2. 熟悉主流 Web框架
3. 熟悉 MySQL、Redis、消息队列""",

    "数据分析师": """岗位职责：
1. 业务数据的统计分析与可视化
2. 构建和维护核心业务指标体系
3. 输出业务分析报告

任职要求：
1. 本科及以上
2. 熟练 SQL、Python（Pandas）
3. 熟悉 Tableau/PowerBI""",
}

# === 工具 ===
tavily = TavilySearchResults(max_results=5, tavily_api_key=os.environ.get("TAVILY_API_KEY"))


@tool(
    "web_search",
    description="搜索网络获取最新面试题和考察重点。必须先调用这个工具搜索岗位的真实面试题。",
)
def web_search(query: str) -> str:
    """Search the web using Tavily."""
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


# === Agent ===
SYSTEM_PROMPT = """你是一个资深的互联网公司技术面试官，专门根据岗位描述（JD）生成结构化的面试题。

【工作流程】
1. 仔细阅读用户提供的 JD，提取：岗位名称、核心技术栈、经验要求
2. 必须先调用 web_search 搜索该岗位的真实面试题
3. 基于 JD + 搜索结果，生成指定数量的面试题

【题目分类】
- 基础题（30%）：核心概念、基础知识
- 项目题（40%）：实际项目经验、解决问题
- 算法题（30%）：编程、算法、逻辑

【每题格式】
### [题号]. [题干]
**参考答案**：[详细专业的答案]
**难度**：⭐ 简单 / ⭐⭐ 中等 / ⭐⭐⭐ 困难

【输出要求】
- Markdown 格式，分类清晰
- 题目要紧贴 JD 提到的技术栈
- 必须基于真实资料，不能凭空编造"""
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
)

agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt=SYSTEM_PROMPT,
)


# === 历史记录 +导出 ===
current_dir = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(current_dir, "history", "sessions.json")
OUTPUTS_DIR = os.path.join(current_dir, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history_entry(role, questions):
    history = load_history()
    history.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "role": role,
        "preview": questions[:80],
    })
    history = history[:20]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def render_history():
    history = load_history()
    if not history:
        return "暂无历史记录"
    md = "## 📚 最近生成\n\n"
    for i, h in enumerate(history[:10], 1):
        md += f"**{i}. {h['role']}** - {h['time']}\n\n"
    return md


def export_questions(role, questions):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{role}_{timestamp}.md"
    filepath = os.path.join(OUTPUTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {role} 面试题\n\n{questions}")
    return filepath


# === Gradio 主函数 ===
def fill_preset(preset_role):
    """选预设岗位时，自动填 JD文本"""
    if preset_role == "自定义":
        return ""
    return PRESET_JDS.get(preset_role, "")


def generate_questions(preset_role, jd_text, jd_file, num_questions, progress=gr.Progress()):
    progress(0.1, "📄 读取 JD...")

    if jd_file is not None:
        jd_text = read_file(jd_file)
    elif preset_role != "自定义":
        jd_text = PRESET_JDS.get(preset_role, "")

    if not jd_text or not jd_text.strip():
        return "⚠️ 请提供 JD 文本（粘贴或选择预设岗位）", None, render_history()

    progress(0.3, "🌐 联网搜索真实面试题...")

    try:
        result = agent.invoke({"messages": [
            {"role": "user", "content": f"请根据以下 JD 生成 {num_questions} 道面试题：\n\n{jd_text}"}
        ]})
        questions = result["messages"][-1].content
    except Exception as e:
        return f"❌ 生成出错: {type(e).__name__}: {e}", None, render_history()

    progress(0.9, "💾 保存到本地...")

    save_history_entry(preset_role, questions)
    filepath = export_questions(preset_role, questions)

    progress(1.0, "✅ 生成完成！")

    download_update = gr.File(value=filepath, visible=True, label="📥 下载 Markdown")
    return questions, download_update, render_history()


def read_file(file_obj):
    """读上传的文件"""
    if isinstance(file_obj, str):
        with open(file_obj, "r", encoding="utf-8") as f:
            return f.read()
    elif  hasattr(file_obj, "name"):
        with open(file_obj.name, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# === Gradio 界面 ===
with gr.Blocks(title="📋 面试题生成 Agent", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📋 面试题生成 Agent\n\n**输入 JD，一键生成结构化面试题**")

    with gr.Row():
        # 左侧输入区
        with gr.Column(scale=1):
            preset = gr.Radio(
                choices=["AI算法工程师", "Python后端", "数据分析师", "全栈工程师", "测试开发", "自定义"],
                value="自定义",
                label="📌 选择岗位（点预设可一键生成）",
            )

            with gr.Tab("📝 粘贴 JD"):
                jd_text_input = gr.Textbox(
 label="JD 内容",
                    placeholder="把岗位描述粘贴到这里...",
                    lines=8,
                )

            with gr.Tab("📎 上传文件"):
                jd_file_input = gr.File(
                    label="上传 JD 文件（.txt / .md）",
                    file_types=[".txt", ".md"],
                )

            num_q = gr.Slider(
 minimum=5, maximum=20, value=10, step=1,
                label="题目数量",
            )

            generate_btn = gr.Button("🚀 生成面试题", variant="primary", size="lg")

        # 右侧输出区
        with gr.Column(scale=2):
            output_md = gr.Markdown(label="📄 生成结果")
            download_file = gr.File(label="📥 下载 Markdown", visible=False)

    # 历史记录
    with gr.Accordion("📚 历史记录", open=False):
        history_md = gr.Markdown(render_history())
        refresh_btn = gr.Button("🔄 刷新历史")
        refresh_btn.click(render_history, outputs=history_md)

    # 事件绑定
    preset.change(fill_preset, inputs=preset, outputs=jd_text_input)
    generate_btn.click(
        generate_questions,
        inputs=[preset, jd_text_input, jd_file_input, num_q],
        outputs=[output_md, download_file, history_md],
    )


if __name__ == "__main__":
    print("启动 Gradio 界面...")
    print(f"已加载 {len(PRESET_JDS)} 个预设岗位")
    demo.launch()   

