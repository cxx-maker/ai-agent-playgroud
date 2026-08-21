import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 面试顾问，专注于简历深度复盘。

请深入分析用户简历中的每个项目/实习经历，帮助用户：
1. 梳理项目的背景、目标、技术栈
2. 挖掘项目的难点和亮点
3. 准备可能被问到的深度问题
4. 提供回答思路和 STAR 法则指导"""


USER_PROMPT_TEMPLATE = """## 用户简历：
{resume}

## 目标岗位 JD：
{job_title}
{jd}

## 请生成：
对简历中每个主要项目/实习进行深度复盘，包括：项目概述、技术栈、核心贡献、可能的面试问题及回答要点。"""


def call_review_agent(state):
    try:
        model = ChatDeepSeek(
            model="deepseek-chat",
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            timeout=60,
        )
        prompt = USER_PROMPT_TEMPLATE.format(
            resume=state.get("resume_text", ""),
            jd=state.get("jd_text", ""),
            job_title=state.get("job_title", "目标岗位"),
        )
        response = model.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return {"function_result": str(response.content)}
    except Exception as e:
        return {"function_result": f"Error: {type(e).__name__}: {e}"}
