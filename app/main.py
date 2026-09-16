from fastapi import FastAPI
from app.api.v1.viagens import router

app = FastAPI(
    title="API de Normalização de Viagens",
    version="1.0.0",
)

app.include_router(router)
