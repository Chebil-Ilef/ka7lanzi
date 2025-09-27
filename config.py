from pathlib import Path
import os
from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from core.llm import LLM

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "uploads"
DATA_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json", ".parquet"}

MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "qwen2.5-7b-instruct-q3_k_m.gguf"
# LLMODEL = LLM().get_llm()

EMBEDDING_MODEL_NAME = str(os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-base-en-v1.5"))
EMBEDDING_MODEL = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME) # téléchargé une fois puis stocké dans ~/.cache/huggingface
EMBEDDINGS_PATH = BASE_DIR / "embeddings"

FEEDBACKS_PATH = BASE_DIR / "feedback/feedback.jsonl"