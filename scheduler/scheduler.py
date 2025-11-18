import asyncio
import os
import csv
import logging
import json
from crawler.crawler import run_crawler
from utilities.database import get_books_collection, get_changelog_collection
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from pymongo.errors import DuplicateKeyError

def process_book_change(book):
    """
    Compare a Book object to DB, insert/update, and log changes.
    """
    books_col = get_books_collection()
    changelog_col = get_changelog_collection()
    data = book.model_dump()  # convert Pydantic to dict

    # Try to find existing book by name (or book_id if you use one)
    existing = books_col.find_one({"name": data["name"]})

    # --------------------------
    # NEW BOOK
    # --------------------------
    if not existing:
        print(f"[NEW] {data['name']}")
        books_col.insert_one(data)

        # Insert changelog for new book
        changelog_col.insert_one({
            "book_id": str(data.get("hash", "")),
            "event": "new_book",
            "timestamp": datetime.utcnow(),
            "changes": {}  # No old values
        })
        return "new"

    # --------------------------
    # UPDATED BOOK (hash mismatch)
    # --------------------------
    if existing["hash"] != data["hash"]:
        print(f"[UPDATED] {data['name']}")
        print(f"old hash {existing['hash']}")
        print(f"new hash {data['hash']}")

        # Detect only changed fields
        changed_fields = {}
        for field in ["category","image_url","raw_html","price_excl_tax", "price_incl_tax", "availability", "num_reviews", "rating", "description"]:
            old_value = existing.get(field)
            new_value = data.get(field)
            if old_value != new_value:
                changed_fields[field] = {"old": old_value, "new": new_value}

        # SAFE: Update the book using upsert to prevent DuplicateKeyError
        try:
            print("HASH BEING SAVED:", data["hash"])
            books_col.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    **data,
                    "hash": data["hash"]  # explicitly set new hash
                }},
                upsert=False
            )
        except DuplicateKeyError:
            print(f"[WARNING] Duplicate hash detected for {data['name']}, skipping update.")

        # Insert changelog with only changed fields
        changelog_col.insert_one({
            "book_id": str(existing["_id"]),
            "event": "update",
            "timestamp": datetime.utcnow(),
            "changes": changed_fields
        })

        return "updated"

    # --------------------------
    # NO CHANGE
    # --------------------------
    #print(f"[NO CHANGE] {data['name']}")
    return "same"

# -----------------------------
# Logging Setup
# -----------------------------
logging.basicConfig(
    filename="crawler_scheduler.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# -----------------------------
# Daily job function
# -----------------------------
async def daily_crawl_job():
    logging.info("Starting daily crawler job...")
    books = await run_crawler()
    summary = {"new": 0, "updated": 0, "same": 0}
    changes_list = []

    for book in books:
        status = process_book_change(book)
        summary[status] += 1

        # If new or updated, log it and collect for report
        if status in ["new", "updated"]:
            book_data = book.model_dump()
            changes_list.append({
                "name": book_data["name"],
                "status": status,
                "hash": book_data.get("hash"),
                "timestamp": book_data.get("meta", {}).get("timestamp")
            })
            logging.info(f"{status.upper()} book: {book_data['name']}")

    logging.info(f"Daily summary: {summary}")
    generate_report(changes_list)
    return summary

# -----------------------------
# Generate JSON/CSV Persistent Report
# -----------------------------
def generate_report(changes):
    if not changes:
        logging.info("No changes to report this run.")
        return

    # Folder
    reports_dir = os.path.join(os.path.dirname(__file__), "../tests")
    os.makedirs(reports_dir, exist_ok=True)

    # -------------------------
    # 1) JSON REPORT (append to single file)
    # -------------------------
    json_file = os.path.join(reports_dir, "report.json")

    # Load old data if file exists
    all_changes = []
    if os.path.exists(json_file):
        try:
            with open(json_file, "r") as jf:
                all_changes = json.load(jf)
        except json.JSONDecodeError:
            all_changes = []

    # Append new changes
    all_changes.extend(changes)

    # Save back
    with open(json_file, "w") as jf:
        json.dump(all_changes, jf, indent=4)

    logging.info(f"Appended {len(changes)} changes to JSON report: {json_file}")

    # -------------------------
    # 2) CSV REPORT (append rows)
    # -------------------------
    csv_file = os.path.join(reports_dir, "report.csv")
    file_exists = os.path.exists(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=changes[0].keys())

        # Write header only once
        if not file_exists:
            writer.writeheader()

        writer.writerows(changes)

    logging.info(f"Appended {len(changes)} changes to CSV report: {csv_file}")

# -----------------------------
# APScheduler setup
# -----------------------------
scheduler = BlockingScheduler()

# Run every day at 2 AM UTC
#@scheduler.scheduled_job("cron", hour=2, minute=0)
@scheduler.scheduled_job("interval", minutes=5)
def scheduled_crawl():
    asyncio.run(daily_crawl_job())

# -----------------------------
# Run scheduler
# -----------------------------
if __name__ == "__main__":
    logging.info("Starting scheduler...")
    scheduler.start()
