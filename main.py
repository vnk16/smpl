from fastapi import FastAPI
from routes.routes import router as admin_routes
from database.database import connect_to_mongo

app = FastAPI()

connect_to_mongo()
app.include_router(admin_routes)
