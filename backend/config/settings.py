import os
import chromadb
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI

from .constants import (
    TOKENIZERS_PARALLELISM, 
    CHROMA_PERSIST_PATH, 
    AZURE_API_VERSION,
    EMBEDDING_MODEL
)

load_dotenv()

# Disable tokenizers parallelism to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = TOKENIZERS_PARALLELISM

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=AZURE_API_VERSION
)

# Regular OpenAI client for embeddings
client_openai = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# RapidAPI configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# ChromaDB configuration
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)

def get_embeddings(texts):
    """Get embeddings using OpenAI API"""
    if isinstance(texts, str):
        texts = [texts]
    
    response = client_openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [data.embedding for data in response.data]

# User-specific progress tracking
user_enrichment_status = {}

def get_user_enrichment_status(user_id: str):
    if user_id not in user_enrichment_status:
        user_enrichment_status[user_id] = {
            "current": 0,
            "total": 0,
            "completed": True
        }
    return user_enrichment_status[user_id]

def update_user_progress(user_id: str, current: int, total: int, completed: bool = False):
    user_enrichment_status[user_id] = {
        "current": current,
        "total": total,
        "completed": completed
    }