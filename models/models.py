from pydantic import BaseModel

class DurationRequest(BaseModel):
    duration: str
