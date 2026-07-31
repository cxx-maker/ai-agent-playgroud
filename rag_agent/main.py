import os

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_chroma import Chroma
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek

load_dotenv()

def build_vertorstore():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resume_path = os.path.join(current_dir,"resume.pdf")
    #1.加载pdf
    loader = PyPDFLoader(resume_path)
    pages = loader.load()


    #2.切分
    splitter =RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n","\n","。",",","?"," ",""],
        )
    chunks = splitter.split_documents(pages)

    #3.创建embedding模型(中文专用)
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    vectorstore = Chroma.from_documents(documents=chunks,embedding=embeddings)
    return vectorstore


def make_retrieval_tool(vectorstore):
    @tool(
        "search_resume",
        description="从用户的简历中检索相关内容，当用户询问用户个人信息，项目经历，技能技能、教育背景、工作经历等任何与简历相关的问题时，必须使用这个工具。",
    )
    def search_resume(query:str) -> str:
        results = vectorstore.similarity_search(query,k=3)
        context_parts = []
        for i, doc in enumerate(results,1):
            page = doc.metadata.get("page","?")
            context_parts.append(
                f"[片段 {i}, 来源页{page}]\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(context_parts)
    return search_resume

SYSTEM_PROMPY ="""你是用户的简历助手，帮用户基于简历内容回答问题。
- 任何问题都必须先调用search_resume 工具获取相关信息。
- 只能根据检索到的内容回答，不要编造简历没有的信息。
- 回答时用自然口语化的中文，不要机械地复述原文
- 如果检索到的内容完全不包含答案，告诉用户“简历里没有相关信息”
"""
            
def  main():
    print("正在加载简历并建立索引...")
    vectorstore = build_vertorstore()
    print(f"简历索引完成，共{vectorstore._collection.count()}条\n")

    search_resume = make_retrieval_tool(vectorstore)

    model = ChatDeepSeek(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
    )

    agent = create_agent(
        model=model,
        tools=[search_resume],
        system_prompt=SYSTEM_PROMPY,
    )
    print("简历回答 Agent 已启动，输入exit退出")

    conversation_history =[]
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

        print(f"AI:{conversation_history[-1].content}")
    # #1.加载pdf
    # loader = PyPDFLoader(resume_path)
    # pages = loader.load()
    #训练写的内容
    # print(f"原始页数：{len(pages)}")
    # print(f"原始总字符数：{sum(len(p.page_content) for p in pages)}")
    # print("=" * 50)
    #训练写的内容
    
    # print(f"准备嵌入{len(chunks)}个块...")
    # print("首次运行下载embedding模型（~100MB）请稍等...")
    #训练内容
    # print(f"切分后块数：{len(chunks)}")
    # print(f"切分后总字符数：{sum(len(c.page_content) for c in chunks)}")
    # print("=" * 50)

    # print("/n---第一块内容 ---")
    # print(chunks[0].page_content)
    # print(f"\n第一块元数据：{chunks[0].metadata}")

    # print("\n --- 第二块内容---")
    # print(chunks[1].page_content)
    #训练内容   
    
    #4.把所有块转成向量，存入chroma(内存模式)
    # vectorstore = Chroma.from_documents(
    #     documents=chunks,
    #     embedding=embeddings,
    # )

    # print(f"向量库建立完成，共{vectorstore._collection.count()}条")
    # print("=" * 50)

    #5.测试相似度搜索
    # queries = [
    #     "你做了什么深度学习的项目",
    #     "你会哪些python后端技能",
    #     "你的教学背景是什么",
    # ]
    # for query in queries:
    #     print(f"\n查询：{query}")
    #     results = vectorstore.similarity_search(query,k=2)

    #     for i, doc in enumerate(results,1):
    #         print(f"/n--- 结果{i} (来源页{doc.metadata.get('page','?')}) ---")
    #         print(doc.page_content[:200].replace("\n"," "))
    #     print("-" * 50)

if __name__ == "__main__":
    main( )