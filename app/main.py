from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import auth, users,students

load_dotenv()

app = FastAPI(title="Schoolify")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(students.router)

@app.get("/healthz")
def health():
    return {"status": "ok"}