$dir = "D:\anaconda3\envs\langchain1.2\agent\ai-agent-playgroud\interview_coach"
$utf8 = New-Object System.Text.UTF8Encoding $false

# 删除 agent 下的损坏文件
Remove-Item "$dir\agents\__pycache__" -Recurse -ErrorAction SilentlyContinue

# === main.py ===
@'
"""项目入口"""
import db
import ui


if __name__ == "__main__":
    db.init_db()
    ui.demo.launch()
'@ | Out-File -FilePath "$dir\main.py" -Encoding utf8

# === db.py ===
@'
"""SQLite 状态管理"""
import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                resume TEXT DEFAULT '',
                jd TEXT DEFAULT '',
                company TEXT DEFAULT '',
                job_title TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def save_session_state(session_id, resume="", jd="", company="", job_title=""):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO sessions
            (id, resume, jd, company, job_title, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, resume, jd, company, job_title,
              datetime.now().isoformat()))


def load_session_state(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT resume, jd, company, job_title FROM sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
    if row:
        return {"resume": row[0], "jd": row[1], "company": row[2], "job_title": row[3]}
    return {"resume": "", "jd": "", "company": "", "job_title": ""}


def save_message(session_id, role, content):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now().isoformat())
        )


def load_session_messages(session_id, limit=20):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? "
            "ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(list(rows))]
'@ | Out-File -FilePath "$dir\db.py" -Encoding utf8

# === master.py ===
@'
"""Master - 简单处理"""
import re


FUNCTION_MENU = """
📋 请选择功能（输入数字 1-8）：

1. 简历针对性改写（匹配目标岗位）
2. 简历深度复盘（项目/实习细节梳理）
3. 面试问题预测（带标准答案）
4. 简历风险排查与应答预案
5. 定制化自我介绍（1分钟/3分钟版）
6. 公司业务速答与岗位匹配
7. 面试复盘优化（输入面试回忆）
8. 反问问题与谈薪话术
"""


def read_resume_file(file_path):
    from docx import Document
    from langchain_community.document_loaders import PyMuPDFLoader

    if file_path.lower().endswith(".pdf"):
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
    elif file_path.lower().endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        docs = [type("D", (), {"page_content": text, "metadata": {}})()]
    else:
        return ""
    return "\n\n".join(d.page_content for d in docs)


def extract_job_title(jd_text):
    if not jd_text:
        return "目标岗位"
    match = re.search(r"([\u4e00-\u9fa5]{2,15}(?:工程师|开发|经理|专员|架构师|分析师))", jd_text)
    if match:
        return match.group(1)
    return "目标岗位"
'@ | Out-File -FilePath "$dir\master.py" -Encoding utf8

# === ui.py ===
@'
"""UI - 不用 graph"""
import os
from dotenv import load_dotenv
load_dotenv()

import gradio as gr
import db
from master import read_resume_file, extract_job_title, FUNCTION_MENU


SESSION = "default"


def upload_resume(file):
    if file is None:
        return "⚠️ 请先上传简历"
    file_path = file.name if hasattr(file, "name") else file
    text = read_resume_file(file_path)
    db.save_session_state(SESSION, resume=text)
    return f"✅ 简历已加载（{len(text)} 字符）"


def chat_fn(message, history):
    if not message.strip():
        return ""

    m = message.strip()
    state = db.load_session_state(SESSION)
    resume = state.get("resume") or ""
    jd = state.get("jd") or ""

    db.save_message(SESSION, "user", m)

    if m in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        if not resume:
            return "❌ 请先上传简历"
        if not jd:
            return "❌ 请先发 JD 文本"
        name_map = {
            "1": "rewrite", "2": "review", "3": "predict",
            "4": "risk", "5": "intro", "6": "company",
            "7": "post", "8": "negotiation",
        }
        name = name_map[m]
        try:
            mod = __import__(f"agents.{name}", fromlist=[f"call_{name}_agent"])
            func = getattr(mod, f"call_{name}_agent")
            result = func({
                "messages": [],
                "resume_text": resume,
                "jd_text": jd,
                "company_name": state.get("company") or "",
                "job_title": state.get("job_title") or "目标岗位",
                "selected_function": None,
                "function_result": "",
            })
            assistant_msg = str(result.get("function_result", ""))
        except Exception as e:
            assistant_msg = f"❌ {type(e).__name__}: {e}"
        db.save_message(SESSION, "assistant", assistant_msg)
        return assistant_msg

    if resume and not jd:
        if len(m) > 15 or any(kw in m for kw in ["岗位", "要求", "职责", "JD", "招聘", "公司"]):
            job_title = extract_job_title(m)
            import re
            company = ""
            match = re.search(r"(\w+公司)", m)
            if match:
                company = match.group(1)
            db.save_session_state(SESSION, resume=resume, jd=m, company=company, job_title=job_title)
            return f"✅ JD 已收到（{len(m)} 字）\n\n请选择功能（1-8）"
        return "📄 简历收到\n\n请发 JD 文本（含岗位要求）"

    if not resume:
        return "❌ 请先上传简历"

    return "❓ 发 JD 或选功能（1-8）"


def show_status():
    state = db.load_session_state(SESSION)
    return (
        f"📄 简历：{len(state.get('resume') or '')} 字",
        f"💼 JD：{len(state.get('jd') or '')} 字",
        f"🏢 公司：{state.get('company') or '-'}",
        f"🎯 岗位：{state.get('job_title') or '-'}",
    )


def reset_session():
    db.save_session_state(SESSION, resume="", jd="", company="", job_title="")
    return [], "🔄 已重置"


def load_history():
    messages = db.load_session_messages(SESSION, limit=50)
    history = []
    for m in reversed(messages):
        history.append({"role": m["role"], "content": m["content"]})
    return history


with gr.Blocks(title="💼 面试辅助系统") as demo:
    gr.Markdown("# 💼 多 Agent 面试辅助系统")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="📄 上传简历", file_types=[".pdf", ".docx"])
            upload_btn = gr.Button("📥 上传", variant="primary")
            upload_status = gr.Markdown("⚠️ 未上传")

            reset_btn = gr.Button("🔄 重置", variant="stop")

            gr.Markdown("### 📊 状态")
            status_resume = gr.Markdown("📄 简历：0")
            status_jd = gr.Markdown("💼 JD：0")
            status_company = gr.Markdown("🏢 公司：-")
            status_job = gr.Markdown("🎯 岗位：-")
            refresh_btn = gr.Button("🔄 刷新", size="sm")

        with gr.Column(scale=2):
            chatbot = gr.ChatInterface(
                fn=chat_fn,
                title="",
                examples=[
                    "拼多多算法工程师岗位要求 PyTorch",
                    "1",
                ],
            )

    upload_btn.click(upload_resume, inputs=[file_input], outputs=[upload_status])
    reset_btn.click(reset_session, outputs=[chatbot.chatbot, upload_status, status_resume])
    refresh_btn.click(show_status, outputs=[status_resume, status_jd, status_company, status_job])


if __name__ == "__main__":
    demo.launch()
'@ | Out-File -FilePath "$dir\ui.py" -Encoding utf8

# === agents/__init__.py ===
'' | Out-File -FilePath "$dir\agents\__init__.py" -Encoding utf8

# === 8 个 agent 文件（用 DeepSeek）===
foreach ($name in @('rewrite', 'review', 'predict', 'risk', 'intro', 'company', 'post', 'negotiation')) {
    $content = @"
import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 顾问，能给出专业、结构化的回答。"""

USER_PROMPT_TEMPLATE = """用户简历：{resume}
目标 JD：{job_title} - {jd}
用户问题：{message}"""


def call_${name}_agent(state):
    try:
        model = ChatDeepSeek(
            model="deepseek-chat",
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            timeout=60,
        )
        prompt = USER_PROMPT_TEMPLATE.format(
            resume=state.get("resume_text", ""),
            jd=state.get("jd_text", ""),
            job_title=state.get("job_title", "目标岗位"),
            message=state.get("last_user_message", ""),
        )
        response = model.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return {"function_result": str(response.content)}
    except Exception as e:
        return {"function_result": f"❌ {type(e).__name__}: {e}"}
"@
    $content = $content -replace "call_${name}_agent", "call_$name`_agent"
    $content = $content -replace "rewrite", "rewrite"
    $content = $content -replace 'call_${name}_agent', "call_$name`_agent"
    $content = $content -replace 'USER_PROMPT_TEMPLATE = """用户简历：{resume}`n目标 JD：{job_title} - {jd}`n用户问题：{message}"""', "USER_PROMPT_TEMPLATE = `"用户简历：{resume}`n目标 JD：{job_title} - {jd}`n用户问题：{message}`""
    Out-File -FilePath "$dir\agents\$name.py" -Encoding utf8 -InputObject $content
}

# === state.py ===
@'
from typing import TypedDict, List, Optional


class InterviewState(TypedDict):
    messages: List[dict]
    resume_text: str
    jd_text: str
    company_name: str
    job_title: str
    selected_function: Optional[str]
    function_result: str
'@ | Out-File -FilePath "$dir\state.py" -Encoding utf8

# 删除旧 DB（重新跑）
Remove-Item "$dir\session.db" -ErrorAction SilentlyContinue

Write-Host "Done. Run python main.py"