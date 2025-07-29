import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Configuration constants
NUMBER_OF_ENRICHMENTS = 10
RATE_LIMIT_SLEEP_SECONDS = 1

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

# RapidAPI configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "li-data-scraper.p.rapidapi.com"

# Global progress tracking
enrichment_status = {
    "current": 0,
    "total": 0,
    "completed": True,
    "in_progress": False
}