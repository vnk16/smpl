# main.py
from fastapi import FastAPI
from routes.routes import router as admin_router
from database.database import connect_db

app = FastAPI()

# Connect to MongoDB
connect_db()

# Include the admin user routes
app.include_router(admin_router)
