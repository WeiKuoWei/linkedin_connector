import logging
import time

from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

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
    start_time = time.time()
    csv_files = await upload_csv(file, background_tasks)
    logger.info(f"CSV upload processed in {time.time()-start_time:.2f} seconds")
    return csv_files

@app.post("/get-suggestions")
async def get_suggestions_endpoint(request: MissionRequest):
    start_time = time.time()
    suggestions = await get_suggestions(request)
    logger.info(f"Processed mission request in {time.time()-start_time:.2f} seconds")
    return suggestions

@app.post("/generate-message")
async def generate_message_endpoint(request: MessageRequest):
    start_time = time.time()
    response = await generate_message(request)
    logger.info(f"Processed message request in {time.time()-start_time:.2f} seconds")
    return response