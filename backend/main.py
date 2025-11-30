from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from rag_service import RAGService

load_dotenv()

app = FastAPI(title="RAG Chatbot API")

# Mount uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Service Instance
rag_service = RAGService()

class ChatRequest(BaseModel):
    question: str
    model: str = "gpt-3.5-turbo"
    history: List[dict] = []

@app.get("/")
async def root():
    return {
        "message": "RAG Chatbot API is running",
        "status": "active",
        "llm_ready": True # Always return true as keys are checked per request
    }

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    result = await rag_service.ingest_files(files)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return {
        "message": f"Successfully processed {len(result['files'])} files",
        "files": result["files"]
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    answer = rag_service.query(request.question, request.model, request.history)
    return {"answer": answer}

@app.post("/clear")
async def clear_history():
    rag_service.clear()
    return {"message": "Conversation and document history cleared"}
