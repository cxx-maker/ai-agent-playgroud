import pandas as pd
import os
import io
import sys
import re
import matplotlib
matplotlib.use("Agg")#不弹窗
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]  # 新增
plt.rcParams["axes.unicode_minus"] = False  
from datetime import datetime
from langchain.tools import tool
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek
import gradio as gr
load_dotenv()
#程序启动时加载一次csv
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir,"recruitment_data.csv")
df = pd.read_csv(csv_path)

charts_dir = os.path.join(current_dir,"charts")
os.makedirs(charts_dir,exist_ok=True)
print(f"已加载数据：{len(df)}行")

@tool("execute_python",description="执行python代码分析招聘数据，环境已预加载df（招聘数据DataFrame）,pd（pandas）、plt（matplotlib.pyplot）。print() 的输出会被捕获返回；matplotlib 图表会自动保存到 charts/ 文件夹并返回路径。")

def execute_python(code:str) ->str:
    """执行python代码，df,pd,plt已经预加载"""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    output_parts = []

    try:
        exec(code,{"df":df,"pd":pd, "plt":plt})
        text_output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        if text_output:
            output_parts.append(text_output.rstrip())
        if plt.get_fignums():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            chart_path = os.path.join(charts_dir,f"chart_{timestamp}.png")
            plt.savefig(chart_path,dpi=100,bbox_inches="tight")
            plt.close("all")
            output_parts.append(f"[图表已保存：{chart_path}]")
        if not output_parts:
            return "代码执行成功，但没有输出"
        return "\n".join(output_parts)
    except Exception as e:
        sys.stdout = old_stdout
        plt.close("all")
        return f"执行错误：{type(e).__name__}: {e}"
SYSTEM_PROMPT = """你是招聘数据分析助手，专门回答用户关于recruitment_data.csv的问题
工作规则：
- 所有数据问题都必须先调用execute_python工具来获取真是计算结果
- 绝对不要凭空编造数字，统计结果或图表。
- 工具返回什么就说什么，不要加工和臆测。
- 回答时用清晰的中文必要时给出关键数字。
-如果工具报错，尝试用更简单的代码重试
"""
model = ChatDeepSeek(
    model="deepseek-chat",
    api_key= os.environ.get("DEEPSEEK_API_KEY"),
)

agent = create_agent(
    model=model,
    tools=[execute_python],
    system_prompt=SYSTEM_PROMPT,
)
#聊天循环
def respond(message,chat_history):
    #处理用户信息，返回文字回复+最新图表路径
    messages =[]
    for msg in chat_history:
        role = msg.get("role")
        content = msg.get("content") or""
        if role in ("user","assistant") and content:
            messages.append({"role": role, "content":content})
        
    messages.append({"role":"user","content":message})

    result = agent.invoke({"messages":messages})
    response = result["messages"][-1].content
    #从工具消息里抓最新的图表路径
    chart_path = None
    for msg in result["messages"]:
        if "图表已保存" in msg.content:
            match = re.search(r"\[图表已保存：、s*(.+?)\]",msg.content)
            if match:
                chart_path = match.group(1).strip()
        return response,chart_path
#启动gradio界面
demo = gr.ChatInterface(
    respond,
    additional_outputs=[gr.Image(label="最新图表",type="filepath")],
    title="照片数据分析Agent",
    description="问我任何关于招聘数据的问题，列如哪些岗位热门？哪个城市AI岗位i工资高",

)
if __name__ =="__main__":
    print(f"已加载数据：{len(df)}行")
    print("=" * 50)
    print("启动gradio界面...")
    demo.launch()
# if __name__ =="__main__":
#     print("=" * 50)
#     print("照片数据分析Agent已启动，输入exit或者quit退出")
#     print("=" * 50)

#     conversation_history = []
#     while True:
#         user_input = input("\n你:").strip()
#         if user_input.lower() in ["exit","quit"]:
#             print("再见")
#             break
#         if not user_input:
#             continue
#         conversation_history.append({"role":"user","content":user_input})
#         result = agent.invoke({"messages":conversation_history})
#         conversation_history = result["messages"]

#         print(f"\nAI:{conversation_history[-1].content}")

# if __name__ == "__main__":
#     print("=" * 50)
#     print("手动测试 execute_python Tool")
#     print("=" * 50)

#     #测试1：print输出
#     print("\n测试1：打印数据形状")
#     result1 = execute_python.invoke({"code":"print(df.shape)"})
#     print(f"返回：{result1}")
#     #测试2：返回数据
#     print("\n测试2：看每个城市的岗位数")
#     result2 = execute_python.invoke({"code":"print(df['城市'].value_counts().head(3))"})

#     print(f"返回：{result2}")
#    # 测试3：画图
#     print("\n测试 3: 画一个柱状图")
#     result3 = execute_python.invoke({
#         "code": (
#             "df.城市.value_counts().head(5).plot(kind='bar')\n"
#             "plt.title('Top 5 Cities')\n"
#             "plt.tight_layout()"
#         )
#     })
#     print(f"返回: {result3}")

#     print(f"\n请去 charts/ 文件夹里看刚生成的图: {charts_dir}")