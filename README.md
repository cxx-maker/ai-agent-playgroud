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
### 4. [interview_agent](./interview_agent) - 面试题生成 Agent
- 上传招聘 JD，一键生成结构化面试题
- 联网搜索该岗位的真实面试题（基于真实资料，不是凭空生成）
- Gradio 网页界面，预设5 个岗位、一键导出 Markdown、进度条提示
- 技术栈：LangChain、Tavily Search API、DeepSeek、Gradio
- **核心技能**：联网搜索（替代被反爬的搜索引擎）、Gradio 高级 UI（预设按钮、文件上传、进度条、历史记录、下载文件）

### 5. [resume_matcher](./resume_matcher) - 简历匹配分析 Agent ⭐ 最新
- 上传简历 PDF + 粘贴 JD，自动分析匹配度
- 输出**结构化数据**：匹配分数、匹配技能、缺失技能、改进建议、整体评价
- Gradio 网页界面，分模块清晰展示
- 技术栈：LangChain、DeepSeek、Gradio、Pydantic、Chroma、FastEmbed、PyMuPDF
- **核心技能**：**结构化输出（Structured Output）** —— 让 Agent 返回的对象而不是字符串，可直接用代码访问字段## 技术栈总览

## 技术栈
- Python 3.11
- LangChain / LangGraph
- DeepSeek API