from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from mongoengine import connect, Q
from models import SearchHistory, SavedSearch
from datetime import datetime

app = FastAPI()

# MongoDB connection
connect(db="act", host="localhost", port=27017)

# Request schemas
class RemoveRequest(BaseModel):
    remove_key: str
    all: bool
    module: Literal["search_history"]

class AddRequest(BaseModel):
    module: Literal["search_history"]
    search_string: str

# Add to SearchHistory (recent searches)
@app.post("/add")
def add_entry(data: AddRequest):
    entry = SearchHistory(
        module=data.module,
        search_string=data.search_string,
        timestamp=datetime.utcnow()
    )
    entry.save()
    return {"status": "saved", "id": str(entry.id)}

# Remove from SearchHistory and save to SavedSearch
@app.post("/remove")
def remove_entries(request: RemoveRequest):
    query = Q(module=request.module)
    if not request.all:
        query &= Q(search_string__icontains=request.remove_key)

    # Fetch entries to be removed
    entries_to_remove = SearchHistory.objects(query)

    # Move each to SavedSearch before deleting
    for entry in entries_to_remove:
        SavedSearch(
            module=entry.module,
            search_string=entry.search_string,
            original_timestamp=entry.timestamp,
            saved_at=datetime.utcnow()
        ).save()

    removed_count = entries_to_remove.delete()
    return {
        "status": "success",
        "moved_to_saved_searches": removed_count
    }

# Get both recent and saved searches
@app.get("/search-history")
def get_history():
    recent = [
        {
            "id": str(entry.id),
            "module": entry.module,
            "search_string": entry.search_string,
            "timestamp": entry.timestamp.isoformat()
        }
        for entry in SearchHistory.objects().order_by("-timestamp")
    ]

    saved = [
        {
            "id": str(entry.id),
            "module": entry.module,
            "search_string": entry.search_string,
            "original_timestamp": entry.original_timestamp.isoformat() if entry.original_timestamp else None,
            "saved_at": entry.saved_at.isoformat()
        }
        for entry in SavedSearch.objects().order_by("-saved_at")
    ]

    return {
        "recent_searches": recent,
        "saved_searches": saved
    }
