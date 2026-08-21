import os
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage
from state import InterviewState


SYSTEM_PROMPT = """你是资深 AI 面试顾问，专注于自我介绍优化。

根据用户的简历和目标岗位，生成简洁有力、突出亮点的自我介绍：
1. 简洁版（30秒/1分钟）- 适用于现场面试开场
2. 完整版（2-3分钟）- 适用于视频面试或电话面试

自我介绍要点：
- 开场问候 + 基本背景（学历、目前工作）
- 核心技能和经验（与目标岗位相关）
- 代表性项目或成就（量化数据）
- 应聘动机和职业规划"""


USER_PROMPT_TEMPLATE = """## 用户简历：
{resume}

## 目标岗位 JD：
{job_title}
{jd}

## 请生成：
两个版本的自我介绍：简洁版（1分钟）和完整版（3分钟）。"""


def call_intro_agent(state):
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
