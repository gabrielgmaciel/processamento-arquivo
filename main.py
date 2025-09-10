from fastapi import FastAPI

app = FastAPI()

from processamento.service import service_router

app.include_router(service_router)

# uvicorn main:app --reload
