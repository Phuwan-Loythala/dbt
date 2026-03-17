import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Commodity Dashboard", layout="wide")

st.title("📈 Commodity Real-Time Pipeline")
st.caption("Automated Data Pipeline via GitHub Actions & Google Sheets")

try:
    # Connect using [connections.gsheets] from Streamlit Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Read data (Cache for 5 mins)
    df = conn.read(ttl="5m")
    
    if df is not None and not df.empty:
        df['timestamp_bkk'] = pd.to_datetime(df['timestamp_bkk'])
        
        # Display latest metrics
        latest = df.iloc[-1]
        c1, c2 = st.columns(2)
        c1.metric(f"Latest {latest['name'].title()} Price", f"${latest['price']}")
        c2.metric("Last Update (BKK)", latest['timestamp_bkk'].strftime('%H:%M:%S'))

        # Charting
        st.line_chart(df, x='timestamp_bkk', y='price')
        
        with st.expander("Show Raw Data"):
            st.dataframe(df.sort_values('timestamp_bkk', ascending=False), use_container_width=True)
    else:
        st.warning("Connected to database, but no data found. Ensure collector.py is running.")

except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.info("Ensure your spreadsheet URL is correct in the Streamlit Secrets tab.")