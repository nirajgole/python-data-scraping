import requests
import sqlite3
from dotenv import dotenv_values

# Load environment variables
secrets = dotenv_values(".env")
api_key = secrets["API_KEY"]
base_url = secrets["BASE_URL"]
host = secrets["HOST"]

# Database connection
conn = sqlite3.connect("./company.db")
cur = conn.cursor()

# Extract Company URL from Database
query = "SELECT company_linkedin_url FROM company_data;"
cur.execute(query)
rows = cur.fetchall()
links = [row[0] for row in rows]

print(links)

# Scrape company data via API
url = f"{base_url}/companies"
payload = {"links": links}
headers = {
    "x-rapidapi-key": api_key,
    "x-rapidapi-host": host,
    "Content-Type": "application/json",
}
response = requests.post(url, json=payload, headers=headers, timeout=30)


try:
    companies = response.json().get("data", [])
except Exception as e:
    print("Error", e)

if len(companies):
    dataset = [
        (
            company["data"]["companyId"],
            company["data"]["companyName"],
            company["data"]["employeeCount"],
            company["data"]["followerCount"],
        )
        for company in companies
        if company.get("data", None)
    ]

    print(dataset)

    # Create table for Enriched Data
    cur.execute("""
    CREATE TABLE IF NOT EXISTS enriched_company
    (
        company_id INTEGER PRIMARY KEY,
        company_name TEXT,
        employee_count INTEGER,
        follower_count INTEGER
    )
    """)

    # upsert records
    query_text = """
    INSERT OR REPLACE INTO enriched_company (company_id, company_name, employee_count, follower_count)
    VALUES (?, ?, ?, ?)
    """
    cur.executemany(query_text, dataset)
else:
    print('No records found')

conn.commit()
cur.close()
conn.close()
