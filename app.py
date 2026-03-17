import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Cloud Commodity Tracker", layout="wide")

st.title("📈 Google Sheets Powered Dashboard")

# Create Connection
conn = st.connection("gsheets", type=GSheetsConnection)
import streamlit as st
api_key = st.secrets["API_KEY_DATA"]
sheet_url = st.secrets["SPRDSHEET"]

st.write(f"Connected to data source using key: {api_key[:4]}****")
# Read Data (it uses the URL from your secrets)
try:
    df = conn.read(ttl="5m") # Cache for 5 mins
    
    if not df.empty:
        latest = df.iloc[-1]
        st.metric(label=f"Latest {latest['name']}", value=f"${latest['price']}")
        
        st.subheader("Price History")
        st.line_chart(df, x='timestamp_bkk', y='price')
        
        with st.expander("View Spreadsheet Data"):
            st.dataframe(df)
    else:
        st.info("Sheet is empty.")
except Exception as e:
    st.error(f"Connect your Google Sheet in Secrets! Error: {e}")