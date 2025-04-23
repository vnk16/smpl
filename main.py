from fastapi import FastAPI
from account.database.database import connect_db
from account.routes.routes import router

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def startup_db():
    connect_db()
