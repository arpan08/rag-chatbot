import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app import route_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    thinkingTimeMs: int
    thinkingTimeSec: float

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    start_time = time.perf_counter()

    answer = route_question(request.question)

    elapsed = time.perf_counter() - start_time

    return {
        "answer": answer,
        "thinkingTimeMs": int(elapsed * 1000),
        "thinkingTimeSec": round(elapsed, 2)
    }