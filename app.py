import streamlit as st
import pandas as pd
from scraper import static_scrape, dynamic_scrape, save_to_firebase
from firebase_config import db 

# Set page config to centered to match your screenshot's narrow vertical look
st.set_page_config(
    page_title="Cloud Based Web Scraper",
    page_icon="🌐",
    layout="centered"
)

# --- THE EXACT TITLE FORMAT ---
st.title("🌐 Cloud Based Web Scraper")

# Custom CSS for the clean dark theme button
st.markdown("""
    <style>
    .stButton>button {
        width: 150px;
        border-radius: 5px;
        background-color: #1E2129;
        color: white;
        border: 1px solid #3d414b;
    }
    .stButton>button:hover {
        background-color: #FF4B4B;
        border: 1px solid #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERTICAL INPUTS ---
url = st.text_input("Enter Website URL", placeholder="https://en.wikipedia.org/wiki/Web_scraping")

scrape_type = st.selectbox(
    "Select Scraping Type",
    (
        "Static Website (BeautifulSoup)",
        "Dynamic Website (Selenium)"
    )
)

# Start button aligned to the left (Standard Streamlit behavior)
if st.button("Start Scraping"):
    if not url.startswith("http"):
        st.warning("Please enter a valid URL (include https://)")
    else:
        with st.spinner("Scraping in progress..."):
            if "Static" in scrape_type:
                result = static_scrape(url)
            else:
                result = dynamic_scrape(url)

        if result:
            save_to_firebase(url, result)
            st.success(f"Scraping completed! {len(result)} items saved.")
            
            # Preview of data
            df_preview = pd.DataFrame(result, columns=["Scraped Text"])
            st.dataframe(df_preview, use_container_width=True)
            
            # Download button
            csv = df_preview.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download as CSV", csv, "scraped_data.csv", "text/csv")
        else:
            st.error("⚠️ No data extracted.")

# --- HISTORY SECTION AT THE BOTTOM ---
st.markdown("---")
st.subheader("📜 Recent History")

if st.button("Refresh History"):
    try:
        docs = db.collection("scraped_data").order_by("timestamp", direction="DESCENDING").limit(5).stream()
        
        history_list = []
        for doc in docs:
            d = doc.to_dict()
            history_list.append({
                "Date": d.get('readable_date', 'N/A'),
                "URL": d.get('url', 'Unknown'),
                "Count": d.get('item_count', 0)
            })
        
        if history_list:
            st.table(pd.DataFrame(history_list))
        else:
            st.info("No records found.")
    except Exception as e:
        st.error(f"Error loading history: {e}")