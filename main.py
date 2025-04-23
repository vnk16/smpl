from fastapi import FastAPI
from mongoengine import connect
from account.routes import router as admin_router, otp_router

app = FastAPI()

connect(db="act", host="mongodb://localhost:27017")

app.include_router(admin_router)
app.include_router(otp_router)

@app.get("/")
def root():
    return {"message": "Admin Service Running"}
