import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 面试顾问，专注于反问环节和薪资谈判。

提供以下指导：
1. 反问环节 - 推荐问面试官的优质问题
   - 岗位相关（团队、技术栈、工作流程）
   - 发展相关（晋升通道、培训机会）
   - 文化相关（团队氛围、公司价值观）
   - 避免问的问题（薪资福利初轮勿问）

2. 薪资谈判 - 提供谈薪话术和策略
   - 如何了解薪资范围
   - 如何基于市场定价谈薪资
   - 如何谈股票期权福利
   - 谈判话术和应对压价技巧"""


USER_PROMPT_TEMPLATE = """## 用户简历：
{resume}

## 目标岗位 JD：
{job_title}
{jd}

## 请提供：
1. 反问环节的优质问题清单（分类型）
2. 薪资谈判的话术和策略指南
3. 注意事项和常见陷阱"""


def call_negotiation_agent(state):
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
