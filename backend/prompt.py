INSTRUCTIONS = """
    Based on the mission above and the detailed profile information provided, suggest the top 4 most relevant connections who could help. Use the enriched profile data (summary, location, industry, company info) to make intelligent matches.

    For each suggestion, provide:
    1. Name and current role/headline
    2. Why they're relevant (specific reasoning based on their enriched profile data)
    3. How they could specifically help with this mission
    4. What makes them a strong connection for this goal

    Return ONLY a valid JSON array with this exact structure:
    [
    {{
        "name": "Full Name",
        "role": "Current Role/Headline", 
        "company": "Current Company",
        "reasoning": "Why they're relevant based on their profile",
        "how_they_help": "Specific ways they can help with the mission"
    }}
    ]
"""