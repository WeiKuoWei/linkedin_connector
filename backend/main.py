from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import logging
import io

from config import client, enrichment_status, NUMBER_OF_ENRICHMENTS, MAX_CONCURRENT_REQUESTS
from storage import load_enriched_cache, save_enriched_cache, save_connections_list
from enrichment import background_enrichment, vectorization_catchup
from models import MissionRequest, MessageRequest
from prompt import get_instructions, get_linkedin_message_prompt
from semantic_search import ConnectionSemanticSearch

# Initialize semantic search
semantic_search = ConnectionSemanticSearch()

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
async def get_enrichment_progress():
    """Get current enrichment progress"""
    return enrichment_status

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Upload and parse LinkedIn connections CSV file with background enrichment"""
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
            if conn["url"] not in enriched_cache or enriched_cache[conn["url"]].get("enriched", False) == False:
                new_urls_to_enrich.append(conn)
        
        logger.info(f"Found {len(new_urls_to_enrich)} new connections to enrich out of {len(new_connections)} total connections")
        
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
            else:
                # Add new connection to cache (not yet enriched)
                enriched_cache[connection["url"]] = connection
        
        # Save updated cache and connections list
        save_enriched_cache(enriched_cache)
        save_connections_list(new_connections)
        
        # Check vectorization status for all enriched connections
        all_enriched = [conn for conn in enriched_cache.values() if conn.get("enriched", False)]
        unvectorized_connections = semantic_search.get_unvectorized_connections(enriched_cache)
        
        total_enriched = len(all_enriched)
        needs_vectorization = len(unvectorized_connections)
        
        logger.info(f"Vectorization status: {total_enriched} enriched, {needs_vectorization} need vectorization")
        
        # Start background tasks
        will_enrich = len(new_urls_to_enrich)
        if new_urls_to_enrich and background_tasks:
            background_tasks.add_task(background_enrichment, new_urls_to_enrich)
        
        # Start vectorization catch-up if needed
        if unvectorized_connections and background_tasks:
            background_tasks.add_task(vectorization_catchup, unvectorized_connections)
        
        return {
            "message": f"Successfully processed {len(new_connections)} connections",
            "count": len(new_connections),
            "total_in_cache": len(enriched_cache),
            "total_enriched": total_enriched,
            "needs_vectorization": needs_vectorization,
            "new_connections_found": len(new_urls_to_enrich),
            "will_enrich": will_enrich,
            "enrichment_started": len(new_urls_to_enrich) > 0,
            "vectorization_started": needs_vectorization > 0,
            "filename": file.filename
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

        

@app.post("/generate-message")
async def generate_message(request: MessageRequest):
    """Generate a personalized LinkedIn message for reconnection"""
    try:
        prompt = get_linkedin_message_prompt(
            name=request.name,
            company=request.company,
            role=request.role,
            mission=request.mission,
            profile_summary=request.profile_summary,
            location=request.location
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        message_text = response.choices[0].message.content.strip()
        
        return {
            "message": message_text,
            "recipient": request.name,
            "company": request.company
        }
    
    except Exception as e:
        logger.error(f"Error generating message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating message: {str(e)}")

# Replace the existing get_suggestions function with:
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
        
        # Extract mission attributes using LLM
        mission_attributes = semantic_search.extract_mission_attributes(request.mission)
        logger.info(f"Extracted mission attributes: {mission_attributes}")
        
        # Get top connections using semantic search
        top_connections = semantic_search.search_top_connections(mission_attributes, n_results=15)
        
        if not top_connections:
            raise HTTPException(
                status_code=400, 
                detail="No relevant connections found for your mission."
            )
        
        # Get full connection data for top matches
        matched_connections = []
        for conn in top_connections:
            full_conn = enriched_cache.get(conn['url'])
            if full_conn:
                matched_connections.append(full_conn)
        
        # Create simplified prompt for LLM with only top matches
        connections_text = []
        for conn in matched_connections[:10]:  # Limit to top 10 for LLM
            name = f"{conn['first_name']} {conn['last_name']}"
            info = f"{name}: {conn.get('headline', 'N/A')}"
            
            if conn.get("summary"):
                info += f" | Summary: {conn['summary'][:100]}..."
            if conn.get("location"):
                info += f" | Location: {conn['location']}"
            if conn.get("industry"):
                info += f" | Industry: {conn['industry']}"
            
            connections_text.append(info)

        prompt = get_instructions(request.mission, connections_text)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        ai_response = response.choices[0].message.content

        # Parse AI response
        try:
            import json as json_parser
            suggestions_json = json_parser.loads(ai_response)
        except:
            try:
                import re  
                json_pattern = r'```(?:json)?\s*(.*?)\s*```'
                match = re.search(json_pattern, ai_response, re.DOTALL)
                if match:
                    json_content = match.group(1).strip()
                    suggestions_json = json_parser.loads(json_content)
                else:
                    suggestions_json = ai_response
            except:
                suggestions_json = ai_response

        # Enhance suggestions with connection data
        enhanced_suggestions = []
        if isinstance(suggestions_json, list):
            for suggestion in suggestions_json:
                matching_conn = None
                for conn in matched_connections:
                    conn_name = f"{conn['first_name']} {conn['last_name']}"
                    if suggestion.get("name", "").lower() in conn_name.lower():
                        matching_conn = conn
                        break
                
                enhanced_suggestion = {
                    **suggestion,
                    "linkedin_url": matching_conn.get("url", "") if matching_conn else "",
                    "profile_summary": matching_conn.get("summary", "") if matching_conn else "",
                    "location": matching_conn.get("location", "") if matching_conn else "",
                    "connection_strength": "Medium"
                }
                enhanced_suggestions.append(enhanced_suggestion)
        
        return {
            "mission": request.mission,
            "mission_attributes": mission_attributes,
            "suggestions": enhanced_suggestions if enhanced_suggestions else suggestions_json,
            "semantic_matches_found": len(top_connections),
            "using_semantic_search": True
        }
    
    except Exception as e:
        logger.error(f"Error in get_suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))