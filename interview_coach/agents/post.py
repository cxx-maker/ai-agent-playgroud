import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 面试顾问，专注于面试复盘优化。

帮助用户复盘面试表现，识别不足并提供改进建议：
1. 分析面试回忆（用户提供）
2. 识别回答中的优点和不足
3. 提供更好的回答思路
4. 评估面试表现和录用可能性
5. 制定后续改进计划"""


USER_PROMPT_TEMPLATE = """## 用户简历：
{resume}

## 目标岗位 JD：
{job_title}
{jd}

## 用户面试回忆：
请提供面试中遇到的问题和你的回答，我来帮你复盘优化。"""


def call_post_agent(state):
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
