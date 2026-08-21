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
        return "请先上传简历"
    file_path = file.name if hasattr(file, "name") else file
    text = read_resume_file(file_path)
    db.save_session_state(SESSION, resume=text)
    return f"简历已加载（{len(text)} 字符）"


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
            return "请先上传简历"
        if not jd:
            return "请先发 JD 文本"
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
            assistant_msg = f"{type(e).__name__}: {e}"
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
            return f"JD 已收到（{len(m)} 字）\n\n请选择功能（1-8）"
        return "简历收到\n\n请发 JD 文本（含岗位要求）"
    if resume and jd:
        try:
            history_msgs = history[-5:] if history else []
            messages_text = "\n".join([
                f"{msg['role']}: {msg['content'][:200]}" for msg in history_msgs
            ])
            prompt = f"""用户最近对话：
{messages_text}

当前简历：
{resume[:500]}

当前 JD：
{jd[:300]}

用户问题：{m}

请简洁回答。"""
            from langchain_deepseek import ChatDeepSeek
            model = ChatDeepSeek(
                model="deepseek-chat",
                api_key=os.environ.get("DEEPSEEK_API_KEY"),
                timeout=60,
            )
            response = model.invoke(prompt)
            assistant_msg = str(response.content)
        except Exception as e:
            assistant_msg = f"{type(e).__name__}: {e}"
        db.save_message(SESSION, "assistant", assistant_msg)
        return assistant_msg
    
    if not resume:
        return "请先上传简历"

    return "发 JD 或选功能（1-8）"


def show_status():
    state = db.load_session_state(SESSION)
    return (
        f"简历：{len(state.get('resume') or '')} 字",
        f"JD：{len(state.get('jd') or '')} 字",
        f"公司：{state.get('company') or '-'}",
        f"岗位：{state.get('job_title') or '-'}",
    )


def reset_session():
    db.save_session_state(SESSION, resume="", jd="", company="", job_title="")
    return [], "已重置"


def load_history():
    messages = db.load_session_messages(SESSION, limit=50)
    history = []
    for m in reversed(messages):
        history.append({"role": m["role"], "content": m["content"]})
    return history


with gr.Blocks(title="面试辅助系统") as demo:
    gr.Markdown("# 多 Agent 面试辅助系统")

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="上传简历", file_types=[".pdf", ".docx"])
            upload_btn = gr.Button("上传", variant="primary")
            upload_status = gr.Markdown("未上传")

            reset_btn = gr.Button("重置", variant="stop")

            gr.Markdown("### 状态")
            status_resume = gr.Markdown("简历：0")
            status_jd = gr.Markdown("JD：0")
            status_company = gr.Markdown("公司：-")
            status_job = gr.Markdown("岗位：-")
            refresh_btn = gr.Button("刷新", size="sm")

        with gr.Column(scale=2):
            gr.Markdown("""
### 📋 8 大功能（输入数字 1-8 选择）

| 编号 | 功能 | 说明 |
|---|---|---|
| 1 | 简历针对性改写 | 针对 JD 优化你的简历 |
| 2 | 简历深度复盘 | 梳理项目/实习细节 |
| 3 | 面试问题预测 | 25-35 道题 + 参考答案 |
| 4 | 风险排查 | 找出简历漏洞 |
| 5 | 自我介绍 | 1分钟/3分钟版 |
| 6 | 公司速答 | 岗位匹配分析 |
| 7 | 面试复盘 | 失败面试分析 |
| 8 | 反问谈薪 | 话术大全 |

**使用流程**：贴 JD → 输入数字 → 选功能
""")

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
