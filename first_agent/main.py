# import sys
# import types

# # 在 langchain 导入之前，先塞一个假的 transformers 模块
# # 防止它去加载真正的 transformers（进而触发 torch、sympy 等重型库）
# # 我们用的是云端 API，不需要 transformers
# _transformers_stub = types.ModuleType("transformers")
# _transformers_stub.GPT2TokenizerFast = None
# sys.modules["transformers"] = _transformers_stub
import os
from datetime import datetime
from typing import Literal
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
load_dotenv()


@tool("get_current_time",description="获取当前系统的日期和时间。")
def  get_current_time() -> str:

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool("calculate",description="对两个数字执行加减乘除运算。")
def calculate(a:float,b:float,operation:Literal["add","subtract","multiply","divide"],) -> str:
    if operation == "add":
        result = a + b
    elif operation == "multiply":
        result = a * b
    elif operation == "subtract":
        result = a - b
    else:
        if b == 0:
            return"错误，除数不可以为0"
        result = a /b
    return f"{result:g}"
@tool("generate_math_problem",description="自动出一道数学计算题给学生做。参数difficulty 可以是'esay'(10以内加减)，‘medium’(100以内加减乘)或'hard'(1000以内加减乘除)。返回字符串里同时包含题目和答案方便老师核对")
def generate_math_problem(difficulty:Literal["easy","medium","hard"]):
    import random
    if difficulty == "easy":
        a = random.randint(1,10)
        b = random.randint(1,10)
        op = random.choice(["add","substract"])
    elif difficulty =='medium':
        a = random.randint(1,100)
        b = random.randint(1,100)
        op = (["add","subtract","multiply"])
    else:
        a = random.randint(1,1000)
        b = random.randint(1,1000)
        op = (["add","subtract","multiply","divide"])
        if op =="divide" and b ==0:
            b =1      
    if op == "add":
        result = a + b
        symbol = "+"
    elif op == "subtract":
        result = a - b
        symbol = "-"
    elif op == "multiply":
        result = a * b
        symbol = "*"
    else:
        result = a / b
        symbol = "/"

    return f"题目：{a} {symbol} {b} = ?，答案：{result:g}"        
# if __name__ =="__main__":
#     current_time = get_current_time.invoke({})
#     calculation_result = calulate.invoke(
#        { "a" :36,
#         "b" : 27,
#         "operation":"multiply",
#         }
#     )
#     print("当前时间：", current_time)
#     print("计算结果:",calculation_result)
# SYSTEM_PROMPT = """你是一个严谨，友好的ai助手
# -当需要真实数据或精确计算时，必须调用工具，不要凭空猜测。
# -回答时要简洁明了，直接给出结论
# -如果工具返回了结果，请基于工具结果回答
# """
# SYSTEM_PROMPT = """你是一个耐心的数学老师，专门给小学生讲题
# -遇到数学计算题，必须调用calculate工具，不能口算
# -回答时先用一两句话讲清楚解题思路，再给出最终答案。
# -语言要温柔，多用‘小盆友’‘我们’这样的称呼
# -不要讲无关的内容，小朋友问到与计算题无关的要告诉她要专心。
# """
SYSTEM_PROMPT = """你是一个耐心的数学老师，专门给小朋友讲题
回答任何数学题时，必须严格按以下三步：
第一步：先用一两句话讲解解题思路。
第二步：调用calculate工具获得准确结果。
第三步：基于工具结果给出最终答案，并温柔的鼓励小朋友。
语气要求：
-多用小朋友，我们这样的称呼
-多保持耐心和鼓励
特殊处理：如果小朋友问的是与数学完全无关的问题（比如天气，你是怎么样），用温柔的方式引导到数学上面。
如果小朋友要求做题，想练习，像被考考可以调用generate_math_problem工具出题给他做，然后再用calculate核对。
"""
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),

)

agent = create_agent(
    model=model,
    tools=[get_current_time,calculate,generate_math_problem],
    system_prompt=SYSTEM_PROMPT,

)
if __name__ =="__main__":
    conversation_history = []
    print("Agent 已启动，输入exit或quit退出。")

    while True:
        user_input = input("\n你：")
        if user_input.strip().lower() in ["exit", "quit"]:
            print("再见")
            break
        if not user_input.strip():
            continue
        conversation_history.append({"role":"user","content":user_input})

        result = agent.invoke({"messages":conversation_history})
        conversation_history = result["messages"]

        print(f"AI: {conversation_history[-1].content}")

    # 调试的过程
    # result = agent.invoke(
    #     {
    #         "messages":[
    #             {
    #                 "role":"user","content":"请帮我计算36乘27是多少？",
    #             }
    #         ]
    #     }
    # )
    # print("---Agent 内部执行过程---")
    # for message in result["messages"]:
    #     print(f"[{type(message).__name__}]:{message.content}")
    # print("\n---最终回答---")
    # print(result["messages"][-1].content)
   