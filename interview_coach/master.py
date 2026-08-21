"""Master - 简单处理"""
import re


FUNCTION_MENU = """
请选择功能（输入数字 1-8）：

1. 简历针对性改写（匹配目标岗位）
2. 简历深度复盘（项目/实习细节梳理）
3. 面试问题预测（带标准答案）
4. 简历风险排查与应答预案
5. 定制化自我介绍（1分钟/3分钟版）
6. 公司业务速答与岗位匹配
7. 面试复盘优化（输入面试回忆）
8. 反问问题与谈薪话术
"""


def read_resume_file(file_path):
    from docx import Document
    from langchain_community.document_loaders import PyMuPDFLoader

    if file_path.lower().endswith(".pdf"):
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
    elif file_path.lower().endswith(".docx"):
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        docs = [type("D", (), {"page_content": text, "metadata": {}})()]
    else:
        return ""
    return "\n\n".join(d.page_content for d in docs)


def extract_job_title(jd_text):
    if not jd_text:
        return "目标岗位"
    match = re.search(r"([一-龥]{2,15}(?:工程师|开发|经理|专员|架构师|分析师))", jd_text)
    if match:
        return match.group(1)
    return "目标岗位"
