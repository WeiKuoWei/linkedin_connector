from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import httpx
import asyncio

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
            response = await http_client.get(
                f"https://{RAPIDAPI_HOST}/get-profile-data-by-url",
                headers=headers,
                params={"url": url},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"LinkedIn API error for {url}: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"Error enriching profile {url}: {str(e)}")
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

@app.get("/")
async def root():
    return {"message": "LinkedIn AI Chatbot API with Profile Enrichment"}

@app.post("/parse-connections")
async def parse_connections():
    try:
        # Read CSV from data directory
        df = pd.read_csv("../data/Connections.csv", skiprows=3)
        
        # Clean and process data
        connections = []
        for _, row in df.iterrows():
            connection = {
                "first_name": row.get("First Name", ""),
                "last_name": row.get("Last Name", ""),
                "url": row.get("URL", ""),
                "email": row.get("Email Address", ""),
                "company": row.get("Company", ""),
                "position": row.get("Position", ""),
                "connected_on": row.get("Connected On", ""),
                "enriched": False
            }
            connections.append(connection)
        
        # Save basic connections first
        with open("data/connections.json", "w") as f:
            json.dump(connections, f, indent=2)
        
        return {"message": f"Parsed {len(connections)} connections", "count": len(connections)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enrich-connections")
async def enrich_connections():
    """Enrich connections with detailed LinkedIn profile data"""
    try:
        # Load existing connections
        with open("data/connections.json", "r") as f:
            connections = json.load(f)
        
        enriched_connections = []
        
        # Process connections in batches to avoid rate limits
        for i, connection in enumerate(connections[:10]):  # Limit to first 10 for testing
            print(f"Enriching {i+1}/{min(10, len(connections))}: {connection['first_name']} {connection['last_name']}")
            
            if connection.get("url"):
                enriched_data = await enrich_profile(connection["url"])
                enriched_connection = format_enriched_connection(connection, enriched_data)
                enriched_connections.append(enriched_connection)
                
                # Small delay to respect rate limits
                await asyncio.sleep(1)
            else:
                enriched_connections.append(connection)
        
        # Add remaining connections without enrichment
        enriched_connections.extend(connections[10:])
        
        # Save enriched connections
        with open("data/connections_enriched.json", "w") as f:
            json.dump(enriched_connections, f, indent=2)
        
        enriched_count = sum(1 for conn in enriched_connections if conn.get("enriched"))
        
        return {
            "message": f"Enriched {enriched_count} connections",
            "total": len(enriched_connections),
            "enriched": enriched_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-suggestions")
async def get_suggestions(request: MissionRequest):
    try:
        # Try to load enriched connections first, fallback to basic
        try:
            with open("data/connections_enriched.json", "r") as f:
                connections = json.load(f)
        except FileNotFoundError:
            with open("data/connections.json", "r") as f:
                connections = json.load(f)
        
        # Create enhanced prompt with enriched data
        connections_text = []
        for conn in connections[:50]:  # Limit for token efficiency
            name = f"{conn['first_name']} {conn['last_name']}"
            
            if conn.get("enriched"):
                # Use enriched data for better context
                info = f"{name}: {conn.get('headline', 'N/A')}"
                if conn.get("summary"):
                    info += f" | Summary: {conn['summary'][:100]}..."
                if conn.get("location"):
                    info += f" | Location: {conn['location']}"
                if conn.get("industry"):
                    info += f" | Industry: {conn['industry']}"
            else:
                # Fallback to basic data
                info = f"{name}: {conn.get('position', 'N/A')} at {conn.get('company', 'N/A')}"
            
            connections_text.append(info)
        
        prompt = f"""
Mission: {request.mission}

LinkedIn Connections (with enriched profiles where available):
{chr(10).join(connections_text)}

Based on the mission above, suggest the top 4 most relevant connections who could help. 
For each suggestion, provide:
1. Name and current role
2. Why they're relevant (specific reasoning based on their background)
3. How they could help with this mission

Format as JSON array with fields: name, role, company, reasoning, how_they_help
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content
        
        enriched_count = sum(1 for conn in connections if conn.get("enriched"))
        
        return {
            "mission": request.mission,
            "suggestions": ai_response,
            "total_connections": len(connections),
            "enriched_connections": enriched_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))