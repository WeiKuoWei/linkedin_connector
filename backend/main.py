from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

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

class MissionRequest(BaseModel):
    mission: str

@app.get("/")
async def root():
    return {"message": "LinkedIn AI Chatbot API"}

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
                "connected_on": row.get("Connected On", "")
            }
            connections.append(connection)
        
        # Save to JSON
        with open("data/connections.json", "w") as f:
            json.dump(connections, f, indent=2)
        
        return {"message": f"Parsed {len(connections)} connections", "count": len(connections)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-suggestions")
async def get_suggestions(request: MissionRequest):
    try:
        # Load connections
        with open("data/connections.json", "r") as f:
            connections = json.load(f)
        
        # Create prompt for AI
        connections_text = "\n".join([
            f"- {conn['first_name']} {conn['last_name']}: {conn['position']} at {conn['company']}"
            for conn in connections[:50]  # Limit for token efficiency
        ])
        
        prompt = f"""
Mission: {request.mission}

LinkedIn Connections:
{connections_text}

Based on the mission above, suggest the top 4 most relevant connections who could help. For each suggestion, provide:
1. Name and current role
2. Why they're relevant (specific reasoning)
3. How they could help

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
        
        return {
            "mission": request.mission,
            "suggestions": ai_response,
            "total_connections": len(connections)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))