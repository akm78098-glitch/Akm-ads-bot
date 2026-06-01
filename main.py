from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import router
import uvicorn

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(
    title="AKM Ads Market API",
    description="Telegram Ad Marketplace Backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")

# Health check
@app.get("/")
def root():
    return {
        "message": "AKM Ads Market API is running",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )