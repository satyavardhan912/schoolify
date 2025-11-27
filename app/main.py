from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import auth

load_dotenv()

app = FastAPI(title="Schoolify")

app.include_router(auth.router) 

@app.get("/healthz")
def health():
    return {"status": "ok"}