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

        # 1. Try knowledge graph (most reliable)
        kg = data.get("knowledge_graph", {})
        if "nationality" in kg:
            return kg["nationality"]

        # 2. Try in title/snippet
        for result in data.get("organic_results", []):
            snippet = result.get("snippet", "").lower()
            title = result.get("title", "").lower()

            # Pattern: "is a Thai fighter" or "is a Thai..."
            match = re.search(r"is (an?|the)? ([a-z]+) fighter", snippet)
            if match:
                return match.group(2).capitalize()

            # Pattern: "Nationality: Thailand"
            match = re.search(r"nationality[:\-–\s]+([a-zA-Z\s]+)", snippet)
            if match:
                return match.group(1).strip().title()

            # Fallback: look for "from Thailand"
            match = re.search(r"from ([a-zA-Z\s]+)", snippet)
            if match:
                return match.group(1).strip().title()

        return "Not found"
    except Exception as e:
        return "Not found"
