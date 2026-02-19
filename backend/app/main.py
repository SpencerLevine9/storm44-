from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Storm44 Backend")


#Allow frontend (Vite default dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],     # Adjust this to your frontend URL
)
@app.get("/health")
def health_check():
    return {"status": "ok"}
