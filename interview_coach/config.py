"""全局配置"""
import os
from dotenv import load_dotenv
load_dotenv()
# 模型配置（MiniMax）
MODEL_NAME = os.environ.get("MODEL_NAME", "MiniMax-M3")
API_KEY = os.environ.get("MiniMax_API_KEY")
API_KEY = (
    os.environ.get("MiniMax_API_KEY")
    or os.environ.get("OPENAI_API_KEY")
    or os.environ.get("DEEPSEEK_API_KEY")
)
BASE_URL = os.environ.get("MiniMax_BASE_URL")
TIMEOUT = int(os.environ.get("AGENT_TIMEOUT", "60"))
MAX_RETRIES = int(os.environ.get("AGENT_MAX_RETRIES", "2"))
TEMPERATURE = float(os.environ.get("AGENT_TEMPERATURE", "0.7"))

# === Agent 配置 ===
MAX_FUNCTION_RESULT_LEN = int(os.environ.get("MAX_RESULT_LEN", "4000"))

# === UI 配置 ===
MAX_HISTORY_MESSAGES = 20
DEFAULT_SESSION_ID = "default"