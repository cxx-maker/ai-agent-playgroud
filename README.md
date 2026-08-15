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

### 6. [resume_optimizer](./resume_optimizer) - AI 简历优化师 ⭐ 最新
- 上传简历 + 粘贴 JD（可选），给出 HR 爱看的改写建议
- **多工具协同**：RAG 读简历 + Tavily 搜行业标准
- **结构化输出**：评分、优势、问题、改写示例、关键词、排版建议
- 高级 UI：分数染色、Tabs 分组、Examples 快捷按钮
- 技术栈：LangChain、MiniMax API、Gradio、Pydantic、FastEmbed、Tavily

### 7. [memory_agent](./memory_agent) - 有记忆的 AI 助手 ⭐ 最新
- 跨对话记住用户信息（名字、偏好、历史问题）
- 技术：SQLite 长期记忆 + LangChain Agent + Gradio
- 核心技能：长期记忆管理、SQLite、上下文拼接
- **演示效果**：开 Gradio → 聊几轮 → 关掉 → 重开 → 问"我叫什么？" → 答得出来

### 8. [pdd_agent](./pdd_agent) - 拼多多客服助手⭐ 最新
- 内置 60+ 条 Pinduoduo 规则（退款/卖家/物流/违规/买家保护/话术）
- RAG 向量库 + Tavily 联网搜
- Gradio 网页界面，支持买家/卖家两种身份
- 技术栈：LangChain、DeepSeek、Chroma、FastEmbed、Gradio、Tavily
- **核心技能**：RAG 文档加载 + 文本切分 + 向量检索 + 多工具协同

## 技术栈总览

| 类别 | 技术 | 项目 |
|---|---|---|
| Agent 框架 | LangChain 1.x | 全部 |
| 大模型 | DeepSeek / MiniMax | 全部 |
| 向量数据库 | Chroma | rag_agent、resume_matcher、resume_optimizer |
| Embedding | FastEmbed | rag_agent、resume_matcher、resume_optimizer |
| 联网搜索 | Tavily API | interview_agent、resume_optimizer |
| 网页界面 | Gradio | data_analysis_agent、interview_agent、resume_matcher、resume_optimizer |
| 数据分析 | Pandas、Matplotlib | data_analysis_agent |
| 数据校验 | Pydantic | resume_matcher、resume_optimizer |
| PDF 读取 | PyMuPDF | resume_matcher、resume_optimizer |

## 技术栈
- Python 3.11
- LangChain / LangGraph
- DeepSeek API
 LangChain 1.x
- DeepSeek / MiniMax（兼容 OpenAI 接口）
- SQLite（Python 自带）
- Tavily Search API
- Gradio