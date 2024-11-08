from fastapi import FastAPI
from datamanager.database import engine
from HarmonApp import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}
