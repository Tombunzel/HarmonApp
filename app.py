from fastapi import FastAPI
from database import engine
from HarmonApp import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello World"}
