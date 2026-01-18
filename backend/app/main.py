import os
import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from app.services.attacker import run_attack
from app.services.logger import initialize_firebase

initialize_firebase()

app = FastAPI(title="Entropy Backend")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AttackRequest(BaseModel):
    url: str

@app.post("/attack")
async def start_attack(request: AttackRequest, background_tasks: BackgroundTasks):
    import uuid
    run_id = str(uuid.uuid4())
    
    background_tasks.add_task(run_attack, request.url, run_id)
    
    return {"runId": run_id}

@app.get("/")
def read_root():
    return {"status": "Entropy Backend is running"}
