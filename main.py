from fastapi import FastAPI

app = FastAPI()

from controller.controller import controller_router

app.include_router(controller_router)

# uvicorn main:app --reload

