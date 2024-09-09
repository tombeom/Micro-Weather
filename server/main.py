import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.microweather import weather

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(weather.router, tags=["Weather"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8089)
