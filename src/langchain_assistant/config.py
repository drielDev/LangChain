from dotenv import load_dotenv
import os

load_dotenv()

# API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# MODEL
MODEL_NAME = "llama-3.1-8b-instant"

# CHAT
TEMPERATURE = 0.3
MAX_HISTORY = 10