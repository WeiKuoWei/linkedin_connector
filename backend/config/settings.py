import os
import chromadb
import logging
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Configuration constants
NUMBER_OF_ENRICHMENTS = 10
RATE_LIMIT_SLEEP_SECONDS = 3.5
MAX_CONCURRENT_REQUESTS = 5 
N_RESULTS = 10

# Disable tokenizers parallelism to avoid warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

# RapidAPI configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "li-data-scraper.p.rapidapi.com"

# ChromaDB configuration
CHROMA_PERSIST_PATH = "./chroma_data"
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
# embedding_model = SentenceTransformer('all-mpnet-base-v2')
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Global progress tracking
enrichment_status = {
    "current": 0,
    "total": 0,
    "completed": True,
    "in_progress": False
}