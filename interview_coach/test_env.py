import os
from dotenv import load_dotenv

load_dotenv()

print("MiniMax_API_KEY:", os.environ.get("MiniMax_API_KEY", "❌ 未设置")[:15] + "...")
print("MiniMax_BASE_URL:", os.environ.get("MiniMax_BASE_URL", "❌ 未设置"))