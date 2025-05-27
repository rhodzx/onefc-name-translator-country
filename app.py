import streamlit as st
import requests
from urllib.parse import urlparse

st.set_page_config(page_title="ONE Athlete Profile", page_icon="🥊")
st.title("🥊 ONE Athlete Profile")

url = st.text_input("Paste the ONE athlete URL:", "https://www.onefc.com/athletes/rodtang/")

# Mock function to simulate user login/authorization
def login_and_get_token():
    # Simulate login POST request, replace with actual login endpoint and data if needed
    login_url = "https://atlas.tech.onefc.com/api/login"  # Example URL
    login_data = {"username": "your_username", "password": "your_password"}
    response = requests.post(login_url, data=login_data)
    response.raise_for_status()
    return response.json().get('token')  # Assuming the token is in the response

# Fetch athlete information using the available token
def fetch_athlete_info(slug, token):
    try:
        api_endpoint = f"https://atlas.tech.onefc.com/api/athletes/{slug}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(api_endpoint, headers=headers)
        response.raise_for_status()
        athlete_info = response.json()
        return athlete_info.get('country', 'Country not found')
    except Exception as e:
        return "Not found"

if "/athletes/" in url:
    parsed = urlparse(url)
    slug = parsed.path.strip('/').split('/')[-1].lower()
    
    # Attempt to obtain a login token
    token = login_and_get_token()

    if token:
        with st.spinner("Fetching country using API..."):
            country = fetch_athlete_info(slug, token)
        st.markdown(f"**🌍 Country:** `{country}`")
    else:
        st.error("Failed to authenticate or fetch data.")
