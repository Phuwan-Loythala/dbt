import requests
import gspread
import os
import sys
import json
import tomllib
from datetime import datetime, timedelta

def load_config():
    """Loads secrets from local TOML or Environment Variables."""
    try:
        # 1. Local Development Path
        base_path = os.path.dirname(os.path.abspath(__file__))
        toml_path = os.path.join(base_path, ".streamlit", "secrets.toml")
        with open(toml_path, "rb") as f:
            secrets = tomllib.load(f)
            api_key = secrets.get("API_KEY_DATA")
            full_url = secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet")
            sheet_id = full_url.split("/d/")[1].split("/")[0] if "/d/" in full_url else full_url
            # Local dev: set GCP_SERVICE_ACCOUNT as an env var in your terminal
            creds = os.environ.get("GCP_SERVICE_ACCOUNT")
            return api_key, sheet_id, creds
    except:
        # 2. GitHub Actions / Cloud Path
        api_key = os.environ.get("API_KEY_DATA")
        raw_id = os.environ.get("SHEET_ID")
        # Safety: extract ID if the full URL was pasted into GitHub
        sheet_id = raw_id.split("/d/")[1].split("/")[0] if raw_id and "/d/" in raw_id else raw_id
        creds = os.environ.get("GCP_SERVICE_ACCOUNT")
        return api_key, sheet_id, creds

API_KEY, SHEET_ID, GCP_JSON = load_config()
COMMODITY = 'silver'

def fetch_and_save():
    if not all([API_KEY, SHEET_ID, GCP_JSON]):
        print("❌ Error: Missing configuration. Check Secrets/Env Vars.")
        return

    # --- 1. Fetch from API-Ninjas ---
    url = f'https://api.api-ninjas.com/v1/commodityprice?name={COMMODITY}'
    headers = {'X-Api-Key': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            bkk_now = datetime.now() + timedelta(hours=7)
            timestamp_str = bkk_now.strftime('%Y-%m-%d %H:%M:%S')

            # --- 2. Authenticate with Service Account ---
            info = json.loads(GCP_JSON)
            gc = gspread.service_account_from_dict(info)
            sh = gc.open_by_key(SHEET_ID)
            worksheet = sh.get_worksheet(0)

            # --- 3. Schema Check & Append ---
            # If Row 1 is empty, add headers
            if not worksheet.row_values(1):
                worksheet.append_row(["name", "price", "updated_unix", "timestamp_bkk"])

            new_row = [data['name'], data['price'], data.get('updated'), timestamp_str]
            worksheet.append_row(new_row)
            print(f"✅ [{timestamp_str}] Data Point Added: ${data['price']}")
        else:
            print(f"❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"🔥 Script Error: {e}")

if __name__ == "__main__":
    fetch_and_save()