from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import httpx
import asyncio
import logging
import time
import io

# fixed number of enrichments for testing
NUMBER_OF_ENRICHMENTS = 10

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

# RapidAPI configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "li-data-scraper.p.rapidapi.com"

class MissionRequest(BaseModel):
    mission: str

async def enrich_profile(url: str):
    """Fetch detailed profile data from LinkedIn URL using RapidAPI"""
    if not url or not url.startswith("https://www.linkedin.com/in/"):
        return None
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        async with httpx.AsyncClient() as http_client:
            start_time = time.time()
            response = await http_client.get(
                f"https://{RAPIDAPI_HOST}/get-profile-data-by-url",
                headers=headers,
                params={"url": url},
                timeout=30.0
            )

            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"LinkedIn API call duration for {url}: {duration:.2f} seconds")

            if response.status_code == 200:
                return response.json()
            else:
                logger.info(f"LinkedIn API error for {url}: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error enriching profile {url}: {str(e)}")
        return None

def format_enriched_connection(connection, enriched_data):
    """Format connection with enriched data"""
    if not enriched_data:
        return connection
    
    # Extract key information from enriched data
    summary = enriched_data.get("summary", "")
    headline = enriched_data.get("headline", connection.get("position", ""))
    
    # Get most recent position
    positions = enriched_data.get("position", [])
    current_position = positions[0] if positions else {}
    
    # Get location
    geo = enriched_data.get("geo", {})
    location = geo.get("full", "")
    
    # Get education
    educations = enriched_data.get("educations", [])
    education_summary = []
    for edu in educations[:2]:  # Top 2 schools
        school = edu.get("schoolName", "")
        if school:
            education_summary.append(school)
    
    return {
        **connection,
        "enriched": True,
        "summary": summary,
        "headline": headline,
        "current_company": current_position.get("companyName", connection.get("company", "")),
        "current_title": current_position.get("title", connection.get("position", "")),
        "location": location,
        "education": ", ".join(education_summary),
        "industry": current_position.get("companyIndustry", ""),
        "company_size": current_position.get("companyStaffCountRange", "")
    }

def load_enriched_cache():
    """Load existing enriched connections cache (URL-keyed dictionary)"""
    cache_path = "data/connections_enriched.json"
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    return {}

def save_enriched_cache(cache):
    """Save enriched connections cache"""
    os.makedirs("data", exist_ok=True)
    with open("data/connections_enriched.json", "w") as f:
        json.dump(cache, f, indent=2)

@app.get("/")
async def root():
    return {"message": "LinkedIn AI Chatbot API with Incremental Profile Enrichment"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and parse LinkedIn connections CSV file with incremental enrichment"""
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        # Read file content
        content = await file.read()
        
        # Parse CSV (skip first 3 rows like LinkedIn export format)
        df = pd.read_csv(io.StringIO(content.decode('utf-8')), skiprows=3)
        
        # Validate required columns
        required_columns = ["First Name", "Last Name", "URL", "Company", "Position"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {missing_columns}"
            )
        
        # Process connections from CSV
        new_connections = []
        for _, row in df.iterrows():
            connection = {
                "first_name": str(row.get("First Name", "")).strip(),
                "last_name": str(row.get("Last Name", "")).strip(),
                "url": str(row.get("URL", "")).strip(),
                "email": str(row.get("Email Address", "")).strip(),
                "company": str(row.get("Company", "")).strip(),
                "position": str(row.get("Position", "")).strip(),
                "connected_on": str(row.get("Connected On", "")).strip(),
                "enriched": False
            }
            # Only add if has name and valid URL
            if connection["first_name"] and connection["last_name"] and connection["url"]:
                new_connections.append(connection)
        
        # Load existing enriched cache (URL-keyed)
        enriched_cache = load_enriched_cache()
        
        # Identify new connections that need enrichment
        new_urls_to_enrich = []
        for conn in new_connections:
            if conn["url"] not in enriched_cache:
                new_urls_to_enrich.append(conn)
        
        logger.info(f"Found {len(new_urls_to_enrich)} new connections to enrich out of {len(new_connections)} total connections")
        
        # Enrich only new connections with progress logging
        enrichment_count = 0
        max_to_enrich = min(NUMBER_OF_ENRICHMENTS, len(new_urls_to_enrich))  # Limit to NUMBER_OF_ENRICHMENTS for API costs
        
        for i, connection in enumerate(new_urls_to_enrich[:max_to_enrich]):
            logger.info(f"Enriching new connection {i+1}/{max_to_enrich}: {connection['first_name']} {connection['last_name']}")
            
            enriched_data = await enrich_profile(connection["url"])
            enriched_connection = format_enriched_connection(connection, enriched_data)
            
            # Add to cache with URL as key
            enriched_cache[connection["url"]] = enriched_connection
            enrichment_count += 1
            
            # Respect rate limits
            await asyncio.sleep(1)
        
        # Add remaining new connections (not enriched due to limit) to cache
        for connection in new_urls_to_enrich[max_to_enrich:]:
            connection["enriched"] = False
            enriched_cache[connection["url"]] = connection
        
        # Update existing connections with any new basic info
        for connection in new_connections:
            if connection["url"] in enriched_cache:
                cached_conn = enriched_cache[connection["url"]]
                # Update basic info but preserve enriched data
                cached_conn.update({
                    "first_name": connection["first_name"],
                    "last_name": connection["last_name"],
                    "email": connection["email"],
                    "company": connection["company"] or cached_conn.get("company", ""),
                    "position": connection["position"] or cached_conn.get("position", ""),
                    "connected_on": connection["connected_on"]
                })
        
        # Save updated cache
        save_enriched_cache(enriched_cache)
        
        # Save current connections list for compatibility
        os.makedirs("data", exist_ok=True)
        with open("data/connections.json", "w") as f:
            json.dump(new_connections, f, indent=2)
        
        total_enriched = sum(1 for conn in enriched_cache.values() if conn.get("enriched", False))
        
        return {
            "message": f"Successfully processed {len(new_connections)} connections",
            "count": len(new_connections),
            "total_in_cache": len(enriched_cache),
            "newly_enriched": enrichment_count,
            "total_enriched": total_enriched,
            "new_connections_found": len(new_urls_to_enrich),
            "filename": file.filename
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/get-suggestions")
async def get_suggestions(request: MissionRequest):
    try:
        # Load enriched cache
        enriched_cache = load_enriched_cache()
        
        if not enriched_cache:
            raise HTTPException(
                status_code=400, 
                detail="No connections found. Please upload a CSV file first."
            )
        
        # Convert cache to list and filter for enriched connections
        all_connections = list(enriched_cache.values())
        enriched_only = [conn for conn in all_connections if conn.get("enriched", False)]
        
        if not enriched_only:
            raise HTTPException(
                status_code=400, 
                detail="No enriched profiles available. Please ensure connections have valid LinkedIn URLs."
            )
        
        # Create enhanced prompt with enriched data
        connections_text = []
        for conn in enriched_only[:NUMBER_OF_ENRICHMENTS]:  # Use top NUMBER_OF_ENRICHMENTS enriched connections
            name = f"{conn['first_name']} {conn['last_name']}"
            info = f"{name}: {conn.get('headline', 'N/A')}"
            
            if conn.get("summary"):
                info += f" | Summary: {conn['summary'][:150]}..."
            if conn.get("location"):
                info += f" | Location: {conn['location']}"
            if conn.get("industry"):
                info += f" | Industry: {conn['industry']}"
            if conn.get("company_size"):
                info += f" | Company Size: {conn['company_size']}"
            
            connections_text.append(info)
        
        prompt = f"""
Mission: {request.mission}

LinkedIn Connections (enriched profiles with detailed information):
{chr(10).join(connections_text)}

Based on the mission above and the detailed profile information provided, suggest the top 4 most relevant connections who could help. Use the enriched profile data (summary, location, industry, company info) to make intelligent matches.

For each suggestion, provide:
1. Name and current role/headline
2. Why they're relevant (specific reasoning based on their enriched profile data)
3. How they could specifically help with this mission
4. What makes them a strong connection for this goal

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "name": "Full Name",
    "role": "Current Role/Headline", 
    "company": "Current Company",
    "reasoning": "Why they're relevant based on their profile",
    "how_they_help": "Specific ways they can help with the mission"
  }}
]
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to raw text if needed
        try:
            import json as json_parser
            suggestions_json = json_parser.loads(ai_response)
        except:
            # If JSON parsing fails, return raw response
            suggestions_json = ai_response
        
        return {
            "mission": request.mission,
            "suggestions": suggestions_json,
            "total_connections": len(all_connections),
            "enriched_connections": len(enriched_only),
            "using_enriched_data": True
        }
    
    except Exception as e:
        logger.error(f"Error in get_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))