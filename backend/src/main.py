from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utenti.routers import router as utente_router
from src.clienti.models import Cliente
from src.ruolo.models import Ruolo
from src.utenti.models import Utente
from src.aziende.models import Azienda
from src.ruolo.routers import router as ruolo_router
from src.clienti.routers import router as cliente_router
from src.auth.routers import router as auth_router
from src.aziende.routers import router as azienda_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(utente_router)
app.include_router(ruolo_router)
app.include_router(cliente_router)
app.include_router(auth_router)
app.include_router(azienda_router)

@app.get("/")
def read_root():
    return {"message": "Benvenuto"}