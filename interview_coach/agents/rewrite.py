import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 简历顾问，专注于简历针对性改写。

请根据目标岗位要求，优化简历内容，使其：
1. 突出与目标岗位最相关的经历和技能
2. 使用岗位描述中的关键词
3. 量化工作成果（使用数据支撑）
4. 保持简洁专业，突出核心竞争力"""


USER_PROMPT_TEMPLATE = """## 用户简历：
{resume}

## 目标岗位 JD：
{job_title}
{jd}

## 请生成：
针对该岗位优化后的简历内容，突出相关经历和技能。"""


def call_rewrite_agent(state):
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
