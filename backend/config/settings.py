import os
import chromadb
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAI
from supabase import create_client, Client
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

# Regular OpenAI client for embeddings
client_openai = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Authentication setup
security = HTTPBearer()

def verify_supabase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Supabase JWT token using JWKS and return user info"""
    try:
        token = credentials.credentials
        
        # Use Supabase client to verify token (handles JWKS automatically)
        response = supabase.auth.get_user(token)
        
        if response.user:
            return {
                "user_id": response.user.id,
                "email": response.user.email,
                "user": response.user
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# RapidAPI configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "li-data-scraper.p.rapidapi.com"

# ChromaDB configuration
CHROMA_PERSIST_PATH = "./chroma_data"
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)

# for web deployment, use OpenAI's embedding model for efficiency
def get_embeddings(texts):
    """Get embeddings using OpenAI API"""
    if isinstance(texts, str):
        texts = [texts]
    
    response = client_openai.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [data.embedding for data in response.data]

enrichment_status = {} 
def get_user_enrichment_status(user_id: str):
    if user_id not in enrichment_status:
        enrichment_status[user_id] = {
            "current": 0,
            "total": 0,
            "completed": True,
            "in_progress": False
        }
    return enrichment_status[user_id]