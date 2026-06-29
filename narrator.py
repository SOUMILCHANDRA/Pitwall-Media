# narrator.py
import os
import json
from google import genai
from google.genai import types

def generate_narrative(insight: dict) -> dict:
    """Uses Gemini Free Tier API (0MB Space) with an immediate local dictionary fallback."""
    
    prompt = (
        f"You are an expert Formula 1 data journalist. Write a concise social media caption for a graphic card.\n"
        f"CRITICAL: Use ONLY the numbers and facts provided below. Do not invent details.\n"
        f"Keep the caption strictly under 2 sentences.\n\n"
        f"Data Points: {json.dumps(insight['data_points'])}\n"
        f"Context: {insight['narrative_hint']}\n\n"
        f"Return EXCLUSIVELY a JSON object matching this exact schema:\n"
        f'{{"headline": "Short punchy title", "caption": "Max 2 sentence description using the data.", "stat_callout": "The single most impactful metric formatted simply like \'-3.4s\' or \'P2\'"}}'
    )

    # Check for the free API key
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                ),
            )
            # Parse and return clean JSON straight from the cloud
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"⚠️ Gemini Cloud API error ({e}), falling back to programmatic matching.")

    # =========================================================================
    # BULLETPROOF PROGRAMMATIC FALLBACK (Works instantly if offline / no key)
    # =========================================================================
    driver = insight["drivers_involved"][0] if insight["drivers_involved"] else "F1"
    
    if insight["type"] == "lap_anomaly":
        time_lost = insight["data_points"].get("time_saved", "N/A") # using fallback defaults
        lap_num = insight["data_points"].get("lap", "0")
        return {
            "headline": f"{driver} PACE DROP",
            "caption": f"Telemetry caught an unexpected pace disruption on Lap {lap_num}. The driver dropped {time_lost}s compared to their steady stint rhythm.",
            "stat_callout": f"+{time_lost}s"
        }
    
    if insight["type"] == "pit_outlier":
        duration = insight["data_points"].get("duration", "N/A")
        delay = insight["data_points"].get("delay", "N/A")
        return {
            "headline": f"CRITICAL STOP: {driver}",
            "caption": f"Disaster in the pit lane as a prolonged pit stop costs {driver} an extra {delay} seconds over the average baseline.",
            "stat_callout": f"{duration}s"
        }
        
    return {
        "headline": f"RACE INSIGHT: {driver}",
        "caption": insight["narrative_hint"],
        "stat_callout": "DATA"
    }

def generate_narratives(insights_path='insights.json'):
    try:
        with open(insights_path, 'r') as f:
            insights = json.load(f)
    except FileNotFoundError:
        print("No insights found.")
        return []
    
    narrated_insights = []
    
    for insight in insights:
        narrative = generate_narrative(insight)
        insight.update(narrative)
        narrated_insights.append(insight)
        
    with open('narrated_insights.json', 'w') as f:
        json.dump(narrated_insights, f, indent=2)
        
    print(f"Generated narratives for {len(narrated_insights)} insights using Gemini/Fallback.")
    return narrated_insights

if __name__ == '__main__':
    generate_narratives()
