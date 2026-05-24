import os
from dotenv import load_dotenv

load_dotenv()
print("FROM DOTENV:", os.getenv("ANTHROPIC_API_KEY"))
print("ALL ENV KEYS:", [k for k in os.environ.keys() if "ANTHRO" in k])