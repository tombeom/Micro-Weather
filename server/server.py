import response
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()
app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/")
async def read_root(latitude: str, longitude: str, methods="GET"):
    if methods != "GET":
        raise HTTPException(status_code=404, detail="Not Found")
    return await response.getResponseData(latitude, longitude)

@app.route("/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"])
def handle_other_methods(path: str):
    raise HTTPException(status_code=404, detail="Not Found")