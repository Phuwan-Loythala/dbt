import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Commodity Tracker", layout="wide")

st.title("📈 Commodity Real-Time Pipeline")
st.subheader("Personal Data Project")

try:
    # Connect using [connections.gsheets] from secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Read data with 0 cache for debugging (change to 5m later)
    df = conn.read(ttl=0)
    
    if df is not None and not df.empty:
        df['timestamp_bkk'] = pd.to_datetime(df['timestamp_bkk'])
        
        # Metrics
        latest = df.iloc[-1]
        col1, col2 = st.columns(2)
        col1.metric("Current Price", f"${latest['price']}")
        col2.metric("Last Sync", latest['timestamp_bkk'].strftime('%H:%M:%S'))

        # Visualization
        st.line_chart(df, x='timestamp_bkk', y='price')
        
        with st.expander("Raw Data View"):
            st.dataframe(df.sort_values('timestamp_bkk', ascending=False))
    else:
        st.warning("Connected, but no data found. Please run collector.py first!")

except Exception as e:
    st.error(f"Connection Failed: {e}")
    st.info("Ensure your Google Sheet is shared with 'Anyone with the link can edit'.")