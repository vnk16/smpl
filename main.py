from fastapi import FastAPI
from routes.routes import router
from database.database import init_db

app = FastAPI()
init_db()
app.include_router(router)

@app.get("/")
def index():
    return {"message": "Admin API is running"}
