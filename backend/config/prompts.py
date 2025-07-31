def get_instructions(mission: str, connections_text: str) -> str:
    return f"""
        Mission: {mission}

        LinkedIn Connections (enriched profiles with detailed information):
        {chr(10).join(connections_text)}

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


def get_linkedin_message_prompt(name: str, company: str, role: str, mission: str, profile_summary: str, location: str) -> str:
    return f"""
        Generate a professional LinkedIn message for reconnecting with a weak tie connection.

        Details:
        - Person: {name} at {company}
        - Their role: {role}
        - Your mission: {mission}
        - Their background: {profile_summary[:200] if profile_summary else "Limited profile information"}
        - Their location: {location if location else "Unknown"}

        Create a personalized, professional message that:
        1. References your previous connection naturally
        2. Mentions their relevant experience/company specifically
        3. Explains your mission and why you're reaching out
        4. Suggests a brief call or meeting
        5. Keeps it concise (2-3 paragraphs max)
        6. Maintains a warm but professional tone

        Return ONLY the message text, no subject line or additional formatting.
    """