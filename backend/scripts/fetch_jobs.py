import ssl
import certifi
import sys
import os
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime

# Fix SSL certificate verification on macOS
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

# Adjust Python path to recognize app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from supabase import create_client, Client
from app.config import settings

def get_supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

def fetch_remote_ok_jobs():
    print("Fetching jobs from RemoteOK RSS...")
    url = "https://remoteok.com/remote-dev-jobs.rss"

    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )

    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        supabase = get_supabase_client()

        inserted_count = 0

        # Parse RSS items
        for item in root.findall('.//item'):
            title_text = item.find('title').text if item.find('title') is not None else "Unknown"
            link = item.find('link').text if item.find('link') is not None else ""
            description_text = item.find('description').text if item.find('description') is not None else ""

            # Basic parsing of "Company: Role" from title string
            if " : " in title_text:
                company, title = title_text.split(" : ", 1)
            else:
                company, title = "RemoteOK", title_text

            job_data = {
                "title": title.strip(),
                "company": company.strip(),
                "location": "Remote",
                "description": description_text.strip(),
                "url": link.strip(),
                "source": "RemoteOK",
                "is_remote": True
            }

            try:
                # Upsert to avoid crash on duplicate URL keys
                supabase.table("jobs").upsert(job_data, on_conflict="url").execute()
                inserted_count += 1
            except Exception:
                continue

        print(f"Pipeline finished processing. Successfully updated/inserted {inserted_count} jobs.")

    except Exception as e:
        print(f"Error executing job ingestion pipeline: {e}")

if __name__ == "__main__":
    fetch_remote_ok_jobs()
