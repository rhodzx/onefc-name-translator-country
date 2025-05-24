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
