import requests
import gspread
import os
import sys
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_KEY = os.environ.get("API_KEY_DATA")
SHEET_ID = os.environ.get('SPRDSHEET', 'YOUR_GOOGLE_SHEET_ID_HERE')
COMMODITY = 'silver'

def fetch_and_save_to_sheets():
    # 1. API Fetch
    url = f'https://api.api-ninjas.com/v1/commodityprice?name={COMMODITY}'
    headers = {'X-Api-Key': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # Validation
            if not data.get('price') or data.get('price') <= 0:
                print("⚠️ Invalid price. Skipping.")
                return

            # Time Conversion
            bkk_now = datetime.now() + timedelta(hours=7)
            timestamp_str = bkk_now.strftime('%Y-%m-%d %H:%M:%S')

            # 2. Google Sheets Connection
            # This uses a simple "Public" sheet logic. 
            # For Streamlit Cloud, you will use st.connection later.
            gc = gspread.public_api() 
            sh = gc.open_by_key(SHEET_ID)
            worksheet = sh.get_worksheet(0) # First tab

            # 3. Append Row
            new_row = [data['name'], data['price'], data.get('updated'), timestamp_str]
            worksheet.append_row(new_row)
            
            print(f"✅ [{timestamp_str}] Saved to Google Sheets: ${data['price']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"🔥 Error: {e}")

if __name__ == "__main__":
    # If running in GitHub Actions, run once. Else loop.
    if "--once" in sys.argv:
        fetch_and_save_to_sheets()
    else:
        while True:
            fetch_and_save_to_sheets()
            time.sleep(900)
