import requests
from supabase import create_client, Client
from datetime import datetime
import re
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables from the .env file in the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Initialize Supabase client
url: str = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key: str = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

def fetch_wikipedia_data(page_title):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "list": "",
        "titles": "Timeline of ancient history",
        "formatversion": "2"
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    page = next(iter(data["query"]["pages"]))
    return page["extract"]

def parse_events(content):
    events = []
    soup = BeautifulSoup(content, 'html.parser')
    list_items = soup.find_all('li')
    
    for item in list_items:
        date_match = item.find('b')
        if date_match:
            date = date_match.text.strip(':')
            description = item.text[len(date)+1:].strip()
            
            if date is not None:
                events.append({
                    "year": date,
                    "description": description
                })
    return events



def process_year(year_str):
    year_str = year_str.lower().strip()
    
    # Handle BC years
    if 'bc' in year_str:
        year = -int(re.search(r'\d+', year_str).group())
    # Handle AD years or years without postfix
    elif 'ad' in year_str or year_str.isdigit():
        year = int(re.search(r'\d+', year_str).group())
    else:
        # Default to None if we can't parse the year
        year = None
    return year

def insert_event(event):
    # Process the year field
    original_year = event['year']
    year_parts = original_year.split('–')
    
    start_year = process_year(year_parts[0])
    end_year = process_year(year_parts[1]) if len(year_parts) > 1 else start_year
    # print(start_year, end_year, original_year, event['description'])
    # Insert into events table
    # event_data = supabase.table("historical_events").insert({
    #     "start_year": start_year,
    #     "end_year": end_year,
    #     "original_year": original_year,
    #     "description": event['description'],
    #     "created_at": datetime.now().isoformat()
    # }).execute()
    
    # print(f"Inserted event: Original Year: {original_year}, Start Year: {start_year}, End Year: {end_year}, Description: {event['description'][:50]}...")

def process_events(events):
    for event in events:
        print(event)
        insert_event(event)
    print(f"Processed {len(events)} events")

def extract_locations(description):
    # This is a simplified location extraction.
    # In a real-world scenario, you'd want to use a more sophisticated
    # named entity recognition system or a geography database.
    common_locations = ["Europe", "Asia", "Africa", "North America", "South America", 
                        "Australia", "Antarctica", "Pacific", "Atlantic", "Indian Ocean"]
    return [loc for loc in common_locations if loc.lower() in description.lower()]

def main():
    wikipedia_pages = [
        "Timeline of ancient history",
        "Timeline of the Middle Ages",
        "Timeline of early modern history",
        "Timeline of modern history",
    ]
    
    for page in wikipedia_pages:
        content = fetch_wikipedia_data(page)
        events = parse_events(content)
        process_events(events)
        print(f"Processed {len(events)} events from {page}")

if __name__ == "__main__":
    main()