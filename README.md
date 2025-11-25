# Books Crawler + API + Scheduler

https://books.toscrape.com/

## Setup
1. Create a virtual environment
2. Install dependencies
3. Setup .env file

## Run API
uvicorn api.api:app --host 0.0.0.0 --port 8000

## Run Scheduler
python -m scheduler.scheduler

## 📘 Swagger UI (API Documentation)

The API provides interactive documentation using Swagger UI.

You can access it here:

👉 **http://3.27.1.157:8000/docs**

## 📦 Sample MongoDB Document Structure

### Collection: `books`
```json
{
  "_id": "679efc624219b9750f4bc343",
  "name": "The Python Handbook",
  "description": "A full guide to Python programming.",
  "category": "Programming",
  "price_excl_tax": 45.99,
  "price_incl_tax": 49.99,
  "availability": 12,
  "num_reviews": 130,
  "image_url": "http://example.com/image.jpg",
  "rating": 4.5,
  "meta": { "crawl timestamp": "", "status": "", "source URL" :"" },
  "raw_html": "<html>...</html>",
  "hash": "ab1293c32f1acf8c7b4ef1f0dd98d201"
}
````
### Collection: `changes`
```json
{
  "_id": "67a0a24b69670f1e079a4345",
  "book_id": "679efc624219b9750f4bc343",
  "event": "updated",
  "timestamp": "2025-11-18T10:05:33Z",
  "changes": {
    "price_incl_tax": { "old": 45.99, "new": 49.99 },
    "rating": { "old": 4.2, "new": 4.5 }
  }
}
```
## Screenshot(s) or logs of successful crawl + scheduler runs
<img width="2711" height="375" alt="image" src="https://github.com/user-attachments/assets/1f4c5579-14a6-4e3c-9c98-d26599d2873c" />
