# Books Crawler + API + Scheduler

https://books.toscrape.com/

## Setup instructions
# 1. Install Miniconda (Linux)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# 2. Create environment from requirements.txt
# Create new environment (example name: books-api)
conda create --name books-api --file requirements.txt

# 3. Activate the environment
conda activate books-api

# 4. Clone the repository
git clone https://github.com/alkali007/books-crawler-api.git
cd books-crawler-api

## Python version and dependency versions
This project uses **Python 3.11**.

### Key Dependencies
The main libraries used are:

- **FastAPI 0.121.1** – API framework  
- **Uvicorn 0.35.0** – ASGI server  
- **APScheduler 3.10.4** – Task scheduler  
- **PyMongo 4.13.0** – MongoDB client  
- **BeautifulSoup4 4.13.5** – HTML parsing  
- **aiohttp 3.13.2** – Async HTTP client  
- **python-dotenv 1.2.1** – Environment variable loader  

You can find the complete list in `requirements.txt`.

## Example .env file for config
API_KEY=fad41b17245f09eaf6f1606da8df7ce9e746cf5af3c4d450dc54c3bbafad8432

MONGO_USER=
MONGO_PASSWORD=
MONGO_HOST=localhost:27017
MONGO_DB=books_db

RATE_LIMIT=100

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
  "meta": { "timestamp": "2025-11-18T08:09:35.213750", "status": "Success", "source_url" :"'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html" },
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
