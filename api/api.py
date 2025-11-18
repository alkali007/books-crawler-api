from fastapi import FastAPI, Query, Depends, Request
from fastapi.responses import JSONResponse
from bson import ObjectId
from utilities.models import BookResponse, ChangeLogResponse
from utilities.database import get_books_collection, get_changelog_collection
from utilities.security import verify_api_key
from utilities.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(
    title="Books API",
    description="REST API for books + changes tracking",
    version="1.0"
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, lambda r, e:
    JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"}))


# ----------------------------------------------------
# 1. GET /books (filtering + sorting + pagination)
# ----------------------------------------------------
@app.get("/books")
@limiter.limit("100/hour")
async def get_books(
    request: Request,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    rating: float = None,
    sort_by: str = Query(None, regex="^(rating|price_excl_tax|num_reviews)$"),
    page: int = 1,
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
):
    col = get_books_collection()
    query = {}

    if category:
        query["category"] = category

    if min_price is not None or max_price is not None:
        query["price_excl_tax"] = {}
        if min_price is not None:
            query["price_excl_tax"]["$gte"] = min_price
        if max_price is not None:
            query["price_excl_tax"]["$lte"] = max_price

    if rating is not None:
        query["rating"] = {"$gte": rating}

    skip = (page - 1) * limit
    sort = [(sort_by, -1)] if sort_by else [("rating", -1)]

    docs = list(col.find(query).sort(sort).skip(skip).limit(limit))

    results = []
    for d in docs:
        d["id"] = str(d["_id"])
        del d["_id"]
        results.append(BookResponse(**d))

    return {
        "page": page,
        "limit": limit,
        "count": len(results),
        "results": results
    }


# ----------------------------------------------------
# 2. GET /books/{book_id}
# ----------------------------------------------------
@app.get("/books/{book_id}", response_model=BookResponse)
@limiter.limit("100/hour")
async def get_book_detail(
        request: Request,
        book_id: str, 
        api_key: str = Depends(verify_api_key)):
    col = get_books_collection()

    try:
        obj_id = ObjectId(book_id)
    except:
        return JSONResponse(status_code=400, content={"detail": "Invalid book_id"})

    doc = col.find_one({"_id": obj_id})
    if not doc:
        return JSONResponse(status_code=404, content={"detail": "Book not found"})

    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return BookResponse(**doc)


# ----------------------------------------------------
# 3. GET /changes (recent updates)
# ----------------------------------------------------
@app.get("/changes")
@limiter.limit("100/hour")
async def get_changes(
        request: Request,
        limit: int = 20, 
        api_ke: str = Depends(verify_api_key)):
    col = get_changelog_collection()
    docs = list(col.find().sort("timestamp", -1).limit(limit))

    results = []
    for d in docs:
        d["id"] = str(d["_id"])
        del d["_id"]
        results.append(ChangeLogResponse(**d))

    return {
        "count": len(results),
        "results": results
    }

