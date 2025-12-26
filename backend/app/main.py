from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from app.api.routers import agents, oauth, auth, vault, posts, calendar 
# Import other existing routers if any (not shown in list_dir but likely exist)
import os


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="StudioFlow AI Backend")

# CORS Configuration
origins = [
    "http://localhost:5173", # Frontend Dev
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files for Charts
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include Routers
app.include_router(agents.router)
app.include_router(oauth.router)
app.include_router(auth.router)
app.include_router(vault.router)
app.include_router(posts.router)
app.include_router(calendar.router)

@app.get("/")
def read_root():
    return {"message": "StudioFlow AI Backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
