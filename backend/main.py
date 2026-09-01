from fastapi import FastAPI
from router.utente_router import router as utente_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(utente_router)

@app.get("/")
def read_root():
    return {"message": "Benvenuto"}