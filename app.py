import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

# Setting up the page title and icon for Streamlit
st.set_page_config(page_title="ONE Athlete Profile", page_icon="🥊")
st.title("🥊 ONE Athlete Profile")

# Input for user to paste URL
url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Function to fetch details of an athlete from the local API or database
def fetch_athlete_info(slug):
    try:
        # Example API endpoint, replace it with actual ONE Championship API endpoint
        api_endpoint = f"https://your-atlas-endpoint/api/athletes/{slug}"
        response = requests.get(api_endpoint)
        response.raise_for_status()
        athlete_info = response.json()
        return athlete_info.get('country', 'Country not found')
    except Exception as e:
        return "Not found"

# Function to fetch athlete's name from the web page, if needed
def fetch_name(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Name not found"
    except Exception as e:
        return "Error: " + str(e)

# Check if the URL contains the athlete segment
if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()

    langs_url_templates = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    # Fetching names and countries using a spinner for user feedback
    with st.spinner("Fetching names and country..."):
        results = {lang: fetch_name(link) for lang, link in langs_url_templates.items()}
        country = fetch_athlete_info(slug)

    # Display country info
    st.markdown(f"**🌍 Country:** `{country}`")
    
    # Create and display a DataFrame of names in different languages
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
