import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.microweather.service import WeatherService
from app.microweather.models import WeatherModel

app = FastAPI(root_path="/microweather", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=200,
    compresslevel=9,
)

@app.get("", response_model=WeatherModel)
async def get_weather(latitude: float, longitude: float):
    return await WeatherService(latitude=latitude, longitude=longitude).get_weather()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8089)

