import logging
import time
import os

from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware

from config.models import MissionRequest, MessageRequest
from config.settings import verify_supabase_token
from api.upload import get_enrichment_progress, upload_csv
from api.suggestions import get_suggestions
from api.messages import generate_message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="LinkedIn AI Chatbot with Authentication")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://linkedin-connector.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LinkedIn AI Chatbot API with Supabase Authentication"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "linkedin-ai-backend"}

# Public endpoint - no auth required
@app.get("/enrichment-progress")
async def enrichment_progress(user: dict = Depends(verify_supabase_token)):
    return await get_enrichment_progress(user)

# Protected endpoints - authentication required
@app.post("/upload-csv") 
async def upload_csv_endpoint(
    file: UploadFile = File(...), background_tasks: BackgroundTasks = None, user: dict = Depends(verify_supabase_token)):
    start_time = time.time()
    csv_files = await upload_csv(file, background_tasks, user)
    logger.info(f"CSV upload processed in {time.time()-start_time:.2f} seconds for user {csv_files.get('user_id')}")
    return csv_files

@app.post("/get-suggestions")
async def get_suggestions_endpoint(request: MissionRequest, user: dict = Depends(verify_supabase_token)):
    start_time = time.time()
    suggestions = await get_suggestions(request, user)
    logger.info(f"Processed mission request in {time.time()-start_time:.2f} seconds for user {suggestions.get('user_id')}")
    return suggestions

@app.post("/generate-message") 
async def generate_message_endpoint(request: MessageRequest, user: dict = Depends(verify_supabase_token)):
    start_time = time.time()
    response = await generate_message(request, user)
    logger.info(f"Processed message request in {time.time()-start_time:.2f} seconds for user {response.get('user_id')}")
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)