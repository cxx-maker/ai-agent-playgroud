import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 面试顾问，专注于面试问题预测。

基于简历和 JD，预测面试中最可能被问到的 10-15 个核心问题，包括：
1. 自我介绍类
2. 项目经历类（STAR 法则回答）
3. 技术深度类（针对简历技能）
4. 行为面试类（团队合作、解决问题等）
5. 反问环节问题

每个问题提供标准答案或回答要点。"""


USER_PROMPT_TEMPLATE = """## 用户简历：
{resume}

## 目标岗位 JD：
{job_title}
{jd}

## 请预测：
该岗位面试中最可能遇到的 10-15 个核心问题，并给出详细回答要点或标准答案。"""


def call_predict_agent(state):
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
