import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 面试顾问，专注于公司业务和岗位匹配分析。

帮助用户：
1. 快速了解目标公司的核心业务、产品和市场地位
2. 分析用户背景与目标岗位的匹配度
3. 准备"为什么选择这家公司/这个岗位"的问题
4. 预判面试官可能关心的岗位相关问题
5. 提供行业知识和趋势分析（如有）"""


USER_PROMPT_TEMPLATE = """## 用户简历：
{resume}

## 目标公司/岗位 JD：
{company_name}
{job_title}
{jd}

## 请分析：
1. 该公司/岗位的核心业务和关键技能要求
2. 用户背景与岗位的匹配度分析
3. 面试中可能问到的问题
4. 如何展现对公司的了解和热情"""


def call_company_agent(state):
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
            company_name=state.get("company_name", ""),
        )
        response = model.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return {"function_result": str(response.content)}
    except Exception as e:
        return {"function_result": f"Error: {type(e).__name__}: {e}"}
