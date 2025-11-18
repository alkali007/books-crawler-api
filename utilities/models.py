from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class BookResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    price_excl_tax: float
    price_incl_tax: float
    availability: int
    num_reviews: int
    image_url: str
    rating: float
    meta: Optional[Dict] = None
    raw_html: Optional[str] = None
    hash: Optional[str] = None

    class Config:
        orm_mode = True


class ChangeLogResponse(BaseModel):
    id: str
    book_id: str
    event: str
    timestamp: datetime
    changes: Dict

