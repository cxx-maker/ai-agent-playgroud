# AI Agent Playground

我的 AI Agent 练习项目集，基于 LangChain + DeepSeek 构建。

## 项目列表

### 1. [first_agent](./first_agent) - 命令行工具调用 Agent
- 多轮对话，自动决定是否调用工具
- 工具：获取时间、数学计算、自动出题
- 技术栈：LangChain 1.x、DeepSeek Chat

### 2. [rag_agent](./rag_agent) - 简历问答 RAG Agent
- 上传 PDF 简历，问任何关于简历内容的问题
- 流程：文档加载 → 切分 → Embedding → 向量库 → 检索 Tool → Agent
- 技术栈：LangChain 1.x、Chroma、FastEmbed、BAAI/bge-small-zh、DeepSeek

### 3. [data_analysis_agent](./data_analysis_agent) - 招聘数据分析 Agent
- 上传 CSV 招聘数据，问任何数据分析问题
- Agent 自动写 pandas/matplotlib 代码并执行
- Gradio 网页界面，支持图表可视化
- 技术栈：LangChain、DeepSeek、Gradio、Pandas、Matplotlib

## 技术栈
- Python 3.11
- LangChain / LangGraph
- DeepSeek API