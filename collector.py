import requests
import gspread
import os
import sys
import time
import tomllib
from datetime import datetime, timedelta

def load_config():
    """Reads local Streamlit secrets and extracts the Sheet ID."""
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        toml_path = os.path.join(base_path, ".streamlit", "secrets.toml")
        
        with open(toml_path, "rb") as f:
            secrets = tomllib.load(f)
            api_key = secrets.get("API_KEY_DATA")
            full_url = secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet")
            
            # Extract ID from URL to avoid 404 errors
            if full_url and "/d/" in full_url:
                sheet_id = full_url.split("/d/")[1].split("/")[0]
            else:
                sheet_id = full_url
                
            return api_key, sheet_id
    except Exception as e:
        # Fallback for GitHub Actions
        return os.environ.get("API_KEY_DATA"), os.environ.get("SHEET_ID")

API_KEY, SHEET_ID = load_config()
COMMODITY = 'silver'

def fetch_and_save():
    if not API_KEY or not SHEET_ID:
        print("❌ Missing API_KEY or SHEET_ID.")
        return

    url = f'https://api.api-ninjas.com/v1/commodityprice?name={COMMODITY}'
    headers = {'X-Api-Key': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Time: Bangkok (UTC+7)
            bkk_now = datetime.now() + timedelta(hours=7)
            timestamp_str = bkk_now.strftime('%Y-%m-%d %H:%M:%S')

            # Connection (Sheet must be "Anyone with link can Edit")
            gc = gspread.public_api() 
            sh = gc.open_by_key(SHEET_ID)
            worksheet = sh.get_worksheet(0)

            # Auto-initialize headers if empty
            if not worksheet.row_values(1):
                worksheet.append_row(["name", "price", "updated_unix", "timestamp_bkk"])

            # Save data
            new_row = [data['name'], data['price'], data.get('updated'), timestamp_str]
            worksheet.append_row(new_row)
            print(f"✅ [{timestamp_str}] Saved ${data['price']} to Google Sheets")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"🔥 Error: {e}")

if __name__ == "__main__":
    if "--once" in sys.argv:
        fetch_and_save()
    else:
        while True:
            fetch_and_save()
            time.sleep(900) # Every 15 minutes