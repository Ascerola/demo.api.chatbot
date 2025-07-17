from fastapi import FastAPI
from src.v1.bitacora.controller import router as bitacora_router
from src.v1.question.controller import router as question_router

def register_routes(app: FastAPI):
    app.include_router(bitacora_router, tags=["Logs"])
    app.include_router(question_router, tags=["Questions"])



