from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.audio import router as audio_router
from api.grievance import router as grievance_router
from api.threads import router as threads_router

app = FastAPI(
    title="Scheme Bot API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(audio_router, prefix="/audio", tags=["Audio"])
app.include_router(threads_router, prefix="/threads", tags=["Threads"])
app.include_router(grievance_router, prefix="/grievance", tags=["Grievance"])


@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Scheme Bot API"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }