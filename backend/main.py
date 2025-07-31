from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import logging

from config.models import MissionRequest, MessageRequest
from api.upload import get_enrichment_progress, upload_csv
from api.suggestions import get_suggestions
from api.messages import generate_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LinkedIn AI Chatbot API with Incremental Profile Enrichment"}

@app.get("/enrichment-progress")
async def enrichment_progress():
    return await get_enrichment_progress()

@app.post("/upload-csv")
async def upload_csv_endpoint(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    return await upload_csv(file, background_tasks)

@app.post("/get-suggestions")
async def get_suggestions_endpoint(request: MissionRequest):
    return await get_suggestions(request)

@app.post("/generate-message")
async def generate_message_endpoint(request: MessageRequest):
    return await generate_message(request)