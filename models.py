from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

# Collection for active/recent searches
class SearchHistory(Document):
    module = StringField(required=True, choices=["search_history"])
    search_string = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)

# Collection for removed/saved searches
class SavedSearch(Document):
    module = StringField(required=True, choices=["search_history"])
    search_string = StringField(required=True)
    original_timestamp = DateTimeField()
    saved_at = DateTimeField(default=datetime.utcnow)
