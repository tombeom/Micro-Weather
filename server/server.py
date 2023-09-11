import response
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root(latitude: str, longitude: str, methods="GET"):
    if methods != "GET":
        raise HTTPException(status_code=404, detail="Not Found")
    return await response.getResponseData(latitude, longitude)

@app.route("/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"])
def handle_other_methods(path: str):
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)