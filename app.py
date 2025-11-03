import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="ONE Athlete Profile Search", page_icon="🥊", layout="wide")
st.title("🥊 ONE Athlete Profile Search")
st.markdown("Search for ONE Championship athletes by name. You can search multiple athletes by separating names with commas.")

# Input field for athlete names
names_input = st.text_area(
    "Enter athlete name(s):", 
    "Rodtang, Demetrious Johnson, Angela Lee",
    help="Enter one or more names separated by commas. The search will try common slug variations."
)

# Hardcoded emoji flags (expand as needed)
country_flags = {
    "Thailand": "🇹🇭",
    "Philippines": "🇵🇭",
    "Japan": "🇯🇵",
    "China": "🇨🇳",
    "Singapore": "🇸🇬",
    "United States": "🇺🇸",
    "Malaysia": "🇲🇾",
    "Brazil": "🇧🇷",
    "India": "🇮🇳",
    "Russia": "🇷🇺",
    "South Korea": "🇰🇷",
    "Vietnam": "🇻🇳",
    "France": "🇫🇷",
    "Azerbaijan": "🇦🇿",
    "Belarus": "🇧🇾",
    "Canada": "🇨🇦",
    "Italy": "🇮🇹",
    "United Kingdom": "🇬🇧",
    "Morocco": "🇲🇦",
    "Algeria": "🇩🇿",
    "Senegal": "🇸🇳",
    "Hong Kong SAR China": "🇭🇰",
    "Australia": "🇦🇺",
    "Germany": "🇩🇪",
    "Netherlands": "🇳🇱",
    "Argentina": "🇦🇷",
    "Colombia": "🇨🇴",
    "Myanmar": "🇲🇲",
    "Indonesia": "🇮🇩",
    "Kazakhstan": "🇰🇿",
    "Ukraine": "🇺🇦",
    "South Africa": "🇿🇦",
    "Turkey": "🇹🇷",
    "Iran": "🇮🇷",
    "Pakistan": "🇵🇰",
    "Nepal": "🇳🇵",
    "Cambodia": "🇰🇭",
    "Laos": "🇱🇦",
    "Taiwan": "🇹🇼",
    "Mongolia": "🇲🇳",
    "New Zealand": "🇳🇿",
    "Spain": "🇪🇸",
    "Portugal": "🇵🇹",
    "Sweden": "🇸🇪",
    "Norway": "🇳🇴",
    "Denmark": "🇩🇰",
    "Finland": "🇫🇮",
    "Poland": "🇵🇱",
    "Czech Republic": "🇨🇿",
    "Slovakia": "🇸🇰",
    "Hungary": "🇭🇺",
    "Romania": "🇷🇴",
    "Bulgaria": "🇧🇬",
    "Greece": "🇬🇷",
    "Serbia": "🇷🇸",
    "Croatia": "🇭🇷",
    "Slovenia": "🇸🇮",
    "Bosnia and Herzegovina": "🇧🇦",
    "North Macedonia": "🇲🇰",
    "Albania": "🇦🇱",
    "Georgia": "🇬🇪",
    "Armenia": "🇦🇲",
    "Uzbekistan": "🇺🇿",
    "Kyrgyzstan": "🇰🇬",
    "Tajikistan": "🇹🇯",
    "Afghanistan": "🇦🇫",
    "Iraq": "🇮🇶",
    "Syria": "🇸🇾",
    "Lebanon": "🇱🇧",
    "Jordan": "🇯🇴",
    "Israel": "🇮🇱",
    "Palestine": "🇵🇸",
    "Saudi Arabia": "🇸🇦",
    "United Arab Emirates": "🇦🇪",
    "Qatar": "🇶🇦",
    "Kuwait": "🇰🇼",
    "Bahrain": "🇧🇭",
    "Oman": "🇴🇲",
    "Yemen": "🇾🇪",
    "Egypt": "🇪🇬",
    "Tunisia": "🇹🇳",
    "Libya": "🇱🇾",
    "Sudan": "🇸🇩",
    "Ethiopia": "🇪🇹",
    "Kenya": "🇰🇪",
    "Uganda": "🇺🇬",
    "Tanzania": "🇹🇿",
    "Rwanda": "🇷🇼",
    "Nigeria": "🇳🇬",
    "Ghana": "🇬🇭",
    "Ivory Coast": "🇨🇮",
    "Luxembourg": "🇱🇺",
    "Malta": "🇲🇹",
    "Iceland": "🇮🇸",
    "Estonia": "🇪🇪",
    "Latvia": "🇱🇻",
    "Lithuania": "🇱🇹",
    "Moldova": "🇲🇩"
}

def name_to_slug_variations(name):
    """Generate possible slug variations for a name"""
    name = name.strip().lower()
    # Remove special characters and normalize
    name = re.sub(r'[^\w\s-]', '', name)
    
    variations = []
    # Full name with hyphens
    full_slug = re.sub(r'\s+', '-', name)
    variations.append(full_slug)
    
    # First name only
    parts = name.split()
    if parts:
        variations.append(parts[0])
    
    # First and last name (if multiple parts)
    if len(parts) > 1:
        variations.append(f"{parts[0]}-{parts[-1]}")
    
    # All parts without hyphens (sometimes used)
    variations.append(''.join(parts))
    
    return variations

def try_fetch_athlete_data(slug):
    """Try to fetch data with a specific slug"""
    base_url = f"https://www.onefc.com/athletes/{slug}/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        r = requests.get(base_url, headers=headers, timeout=5)
        if r.status_code == 200:
            return slug, r.content
        return None, None
    except:
        return None, None

def fetch_athlete_data(name):
    """Fetch athlete data by trying different slug variations"""
    slugs = name_to_slug_variations(name)
    
    for slug in slugs:
        slug, content = try_fetch_athlete_data(slug)
        if slug and content:
            return slug, content
    
    return None, None

def parse_athlete_page(content):
    """Parse athlete page content to extract nationality"""
    soup = BeautifulSoup(content, 'html.parser')
    
    countries = []
    attr_blocks = soup.select("div.attr")
    for block in attr_blocks:
        title = block.find("h5", class_="title")
        if title and "country" in title.get_text(strip=True).lower():
            value = block.find("div", class_="value")
            if value:
                countries = [a.get_text(strip=True) for a in value.find_all("a")]
            break
    
    return countries if countries else ["Not found"]

def fetch_localized_name(slug, lang_code=""):
    """Fetch athlete name from localized page"""
    if lang_code:
        url = f"https://www.onefc.com/{lang_code}/athletes/{slug}/"
    else:
        url = f"https://www.onefc.com/athletes/{slug}/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')
        h1 = soup.find('h1', {'class': 'use-letter-spacing-hint my-4'}) or soup.find('h1')
        return h1.get_text(strip=True) if h1 else "Not found"
    except:
        return "Not found"

def fetch_all_names_parallel(slug):
    """Fetch names in all languages in parallel"""
    langs = {
        "English": "",
        "Thai": "th",
        "Japanese": "jp",
        "Chinese": "cn"
    }
    
    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_lang = {
            executor.submit(fetch_localized_name, slug, code): lang 
            for lang, code in langs.items()
        }
        
        for future in as_completed(future_to_lang):
            lang = future_to_lang[future]
            try:
                results[lang] = future.result()
            except:
                results[lang] = "Error"
    
    return results

# Search button
if st.button("Search Athletes", type="primary"):
    # Parse names
    names = [name.strip() for name in names_input.split(',') if name.strip()]
    
    if not names:
        st.error("Please enter at least one athlete name")
    else:
        # Progress bar
        progress = st.progress(0)
        status = st.empty()
        
        all_results = []
        
        for idx, name in enumerate(names):
            status.text(f"Searching for {name}...")
            progress.progress((idx + 1) / len(names))
            
            # Try to find the athlete
            slug, content = fetch_athlete_data(name)
            
            if slug and content:
                # Get nationality
                countries = parse_athlete_page(content)
                flags = [country_flags.get(c, "") for c in countries]
                nationality_str = " / ".join(f"{c} {f}" for c, f in zip(countries, flags))
                
                # Get names in all languages
                name_results = fetch_all_names_parallel(slug)
                
                # Add to results
                result = {
                    "Search Query": name,
                    "Status": "✅ Found",
                    "Nationality": nationality_str,
                    "English Name": name_results.get("English", "N/A"),
                    "Thai Name": name_results.get("Thai", "N/A"),
                    "Japanese Name": name_results.get("Japanese", "N/A"),
                    "Chinese Name": name_results.get("Chinese", "N/A"),
                    "Profile URL": f"https://www.onefc.com/athletes/{slug}/"
                }
            else:
                result = {
                    "Search Query": name,
                    "Status": "❌ Not found",
                    "Nationality": "-",
                    "English Name": "-",
                    "Thai Name": "-",
                    "Japanese Name": "-",
                    "Chinese Name": "-",
                    "Profile URL": "-"
                }
            
            all_results.append(result)
        
        progress.empty()
        status.empty()
        
        # Display results in a DataFrame
        st.success(f"Search complete! Found {sum(1 for r in all_results if r['Status'] == '✅ Found')} out of {len(names)} athletes.")
        
        df = pd.DataFrame(all_results)
        
        # Display the dataframe with custom styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Profile URL": st.column_config.LinkColumn("Profile URL"),
                "Status": st.column_config.TextColumn("Status", width="small"),
            }
        )
        
        # Download button for CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="one_athletes_search_results.csv",
            mime="text/csv"
        )
        
        # Summary statistics
        with st.expander("📊 Summary Statistics"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Searched", len(names))
            with col2:
                st.metric("Found", sum(1 for r in all_results if r['Status'] == '✅ Found'))
            with col3:
                st.metric("Not Found", sum(1 for r in all_results if r['Status'] == '❌ Not found'))
            
            # Country distribution
            all_countries = []
            for result in all_results:
                if result['Nationality'] != "-":
                    countries = result['Nationality'].split(" / ")
                    for country in countries:
                        # Extract country name without flag
                        country_name = country.split(" ")[0]
                        all_countries.append(country_name)
            
            if all_countries:
                country_counts = pd.Series(all_countries).value_counts()
                st.subheader("Country Distribution")
                st.bar_chart(country_counts)
