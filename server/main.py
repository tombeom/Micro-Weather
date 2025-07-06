import uvicorn
from fastapi import FastAPI
from app.database.mongo import Mongo
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.weather import router as weather
from app.location import router as location
from app.pm import router as particulate_matter


@asynccontextmanager
async def lifespan(
        app: FastAPI
):
    client = Mongo.create_client()
    app.state.client = client
    try:
        yield
    finally:
        client.close()


app = FastAPI(
    root_path="/microweather",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan
)


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

app.include_router(
    weather.router, tags=["Weather"]
)
app.include_router(
    particulate_matter.router, tags=["Particulate Matter"]
)
app.include_router(
    location.router, tags=["Location"]
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
    )
