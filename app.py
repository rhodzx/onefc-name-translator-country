import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import re

st.set_page_config(page_title="ONE FC Name Translator + Country", page_icon="🏋️")
st.title("🏋️ ONE FC Athlete Name Translator + Country")

url = st.text_input("Paste the ONE FC athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Enhanced Google Search function via SerpAPI
def fetch_country_from_google(slug, api_key):
    import re
    try:
        query = f"{slug.replace('-', ' ')} ONE Championship nationality"
        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
        }
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 1. Knowledge Graph (most reliable)
        kg = data.get("knowledge_graph", {})
        if "nationality" in kg:
            return kg["nationality"]

        def extract_country(text):
            text = text.lower()

            # Match: Nationality: France
            match = re.search(r"nationality[:\-–\s]+([a-zA-Z\s]+)", text)
            if match:
                return match.group(1).strip().title()

            # Match: is a French / Thai fighter
            match = re.search(r"is an? ([a-zA-Z\s]+) fighter", text)
            if match:
                return match.group(1).strip().title()

            # Match: from France
            match = re.search(r"from ([a-zA-Z\s]+)", text)
            if match:
                return match.group(1).strip().title()

            return None

        # 2. Scan organic_results
        for result in data.get("organic_results", []):
            for field in ["snippet", "title"]:
                val = result.get(field, "")
                found = extract_country(val)
                if found:
                    return found

        # 3. Scan related_questions (optional)
        for q in data.get("related_questions", []):
            for field in ["snippet", "title"]:
                val = q.get(field, "")
                found = extract_country(val)
                if found:
                    return found

        return "Not found"
    except Exception as e:
        return "Not found"

# Language name scraper
def fetch_name(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Name not found"
    except Exception as e:
        return f"Error: {e}"

# Main logic
if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()

    langs = {
        "English": f"https://www.onefc.com/athletes/{slug}/",
        "Thai": f"https://www.onefc.com/th/athletes/{slug}/",
        "Japanese": f"https://www.onefc.com/jp/athletes/{slug}/",
        "Chinese": f"https://www.onefc.com/cn/athletes/{slug}/"
    }

    with st.spinner("Fetching names and country..."):
        results = {lang: fetch_name(link) for lang, link in langs.items()}
        country = fetch_country_from_google(slug, st.secrets["SERPAPI_KEY"])

    st.markdown(f"**🌍 Country:** `{country}`")
    df = pd.DataFrame(results.items(), columns=["Language", "Name"])
    st.dataframe(df)
