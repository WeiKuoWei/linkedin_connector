from pydantic import BaseModel

class MissionRequest(BaseModel):
    mission: str

class MessageRequest(BaseModel):
    name: str
    company: str
    role: str
    mission: str
    profile_summary: str = ""
    location: str = ""
