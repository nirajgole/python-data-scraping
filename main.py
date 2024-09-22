import requests
import sqlite3
import logging
from dotenv import dotenv_values

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
secrets = dotenv_values(".env")
api_key = secrets.get("API_KEY")
base_url = secrets.get("BASE_URL")
host = secrets.get("HOST")

# Validate environment variables
if not all([api_key, base_url, host]):
    logger.error("Missing required environment variables.")
    exit(1)

def fetch_company_links():
    """Fetch company LinkedIn URLs from the database."""
    with sqlite3.connect("./company.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT company_linkedin_url FROM company_data;")
        rows = cur.fetchall()
        return [row[0] for row in rows]

def fetch_company_data(links:list)->list:
    """Fetch company data from the API."""
    url = f"{base_url}/companies"
    payload = {"links": links}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": host,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return []

def process_data(companies:list):
    """Process and insert/update company data in the database."""
    dataset = [
        (
            company["data"]["companyId"],
            company["data"]["companyName"],
            company["data"]["employeeCount"],
            company["data"]["followerCount"],
        )
        for company in companies
        if company.get("data")
    ]

    if dataset:
        logger.info(f"Fetched {len(dataset)} records to insert/update.")

        with sqlite3.connect("./company.db") as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS enriched_company
                (
                    company_id INTEGER PRIMARY KEY,
                    company_name TEXT,
                    employee_count INTEGER,
                    follower_count INTEGER
                )
            """)

            query_text = """
                INSERT OR REPLACE INTO enriched_company (company_id, company_name, employee_count, follower_count)
                VALUES (?, ?, ?, ?)
            """
            try:
                cur.executemany(query_text, dataset)
                conn.commit()
                logger.info("Data inserted/updated successfully.")
            except sqlite3.Error as e:
                logger.error(f"Database error: {e}")
    else:
        logger.info("No records found")

def main():
    """
    entry point
    """
    links = fetch_company_links()
    logger.info(f"Fetched {len(links)} company links.")
    companies = fetch_company_data(links)
    process_data(companies)

if __name__ == "__main__":
    main()
