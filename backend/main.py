from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.routes.career import router as career_router
from backend.routes.jobs import router as jobs_router
from backend.routes.resume import router as resume_router

app = FastAPI(
    title="AI Career Intelligence",
    description="AI-powered Career and Job Matching Platform",
    version="1.0.0"
)

app.include_router(career_router)
app.include_router(jobs_router)
app.include_router(resume_router)

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")


@app.get("/")
def home():
    return {
        "message": "AI Career Intelligence API is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
