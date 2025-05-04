from fastapi import FastAPI
from . import auth, models
from .database import engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "AuthAPI is running."}
