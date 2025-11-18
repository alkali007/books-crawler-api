import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel, field_validator
import re
from datetime import datetime
import hashlib
from typing import Optional, Dict
from utilities.database import get_books_collection

BASE_URL = "https://books.toscrape.com/catalogue/"


# -------------------------
# Pydantic Model
# -------------------------
class Book(BaseModel):
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

    @field_validator("price_excl_tax", "price_incl_tax", "availability", "num_reviews", mode="before")
    def extract_number(cls, v):
        number = re.findall(r"[\d.]+", v)
        return float(number[0]) if number else 0


# -------------------------
# Async helpers
# -------------------------
async def fetch(session, url, retries=3, delay=2):
    """
    Async GET request with retry logic using aiohttp.

    Args:
        session: aiohttp.ClientSession
        url: URL to fetch
        retries: number of retries on failure
        delay: seconds to wait between retries
    Returns:
        response text if successful, else None
    """
    for attempt in range(1, retries + 1):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"Attempt {attempt}: Non-200 status {response.status} for {url}")
        except Exception as e:
            print(f"Attempt {attempt} failed for {url}: {e}")
        if attempt < retries:
            await asyncio.sleep(delay)
    print(f"All {retries} attempts failed for {url}")
    return None


async def scrape_book_list(session, url):
    """Scrape list page to get book links"""
    html = await fetch(session, url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("article", class_="product_pod")

    links = []
    for item in items:
        h3 = item.find("h3")
        a_tag = h3.find("a")
        href = a_tag.get("href")
        full_link = BASE_URL + href
        links.append(full_link)

    return links


async def scrape_book_detail(session, url):
    """Scrape details from each book page"""
    timestamp = datetime.utcnow().isoformat()
    status = "Success"

    html = await fetch(session, url)
    if not html:
        status = "Failed"
        return Book(
            name=None,
            description=None,
            category=None,
            price_excl_tax="0",
            price_incl_tax="0",
            availability="0",
            num_reviews="0",
            image_url=None,
            rating=None,
            meta={
                "timestamp": timestamp,
                "status": status,
                "source_url": url,
            },
            raw_html=None,
            hash=None
        )

    soup = BeautifulSoup(html, "html.parser")

    # Extract fields
    name = soup.find("div", class_="col-sm-6 product_main").find("h1").text.strip()
    rating = soup.find("p", class_="star-rating").get("class")[1]
    rating_str = rating.lower()
    rating_map = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0
    }

    rating_float = rating_map.get(rating_str, 0.0)  # default to 0.0 if not found

    desc_header = soup.find(id="product_description")
    description = (
        desc_header.find_next("p").text.strip()
        if desc_header else None
    )

    bc = soup.find("ul", class_="breadcrumb").find_all("li")
    category = bc[-2].text.strip()

    table = soup.find("table", class_="table table-striped")
    rows = {row.th.text.strip(): row.td.text.strip() for row in table.find_all("tr")}

    img = soup.find("div", class_="carousel-inner").find("img")["src"]
    img_url = "https://books.toscrape.com/" + img.replace("../", "")

    # Compute hash for deduplication
    hash_input = f"{name}{description}{category}{rows.get('Price (excl. tax)','0')}{rows.get('Price (incl. tax)','0')}{rows.get('Availability','0')}{rows.get('Number of reviews', '0')}{img_url}{rating_float}"
    book_hash = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

    # Return Book with metadata
    return Book(
        name=name,
        description=description,
        category=category,
        price_excl_tax=rows.get("Price (excl. tax)", "0"),
        price_incl_tax=rows.get("Price (incl. tax)", "0"),
        availability=rows.get("Availability", "0"),
        num_reviews=rows.get("Number of reviews", "0"),
        image_url=img_url,
        rating=rating_float,
        meta={
            "timestamp": timestamp,
            "status": status,
            "source_url": url,
        },
        raw_html=html,
        hash=book_hash
    )

# -------------------------
# MAIN ASYNC CRAWLER
# -------------------------
async def run_crawler():
    results = []
    page = 1

    async with aiohttp.ClientSession() as session:

        while True:
            list_url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            print(f"Scraping page {page}")

            try:
                book_links = await scrape_book_list(session, list_url)
            except:
                print("max page")
                break

            if not book_links:
                print("max page")
                break

            # Make async tasks for all book detail pages
            tasks = [
                scrape_book_detail(session, link)
                for link in book_links
            ]

            books = await asyncio.gather(*tasks)

            # Save only non-None Book objects
            results.extend([b for b in books if b])

            page += 1

    return results

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    all_books = asyncio.run(run_crawler())
    print(f"Total books scraped: {len(all_books)}")
