from fastapi import FastAPI

app = FastAPI(
    title="AI Banking Platform",
    version="1.0.0",
    description="AI Powered Banking Platform with Multi-Agent Architecture"
)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "AI Banking Platform is Running 🚀",
        "version": "1.0.0"
    }
