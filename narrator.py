# narrator.py
import os
import json
from google import genai
from google.genai import types

def generate_narrative(insight: dict) -> dict:
    prompt = (
        f"You are a viral motorsport content creator writing historical summaries. \n"
        f"Review the telemetry data and write the summary strictly in the PAST TENSE.\n\n"
        f"CRITICAL RULES:\n"
        f"1. Headline: Max 4 words. Use maximum hype/drama (e.g., 'ALONSO SHREDDED THE GAP', 'HADJAR FLAMED THE FIELD').\n"
        f"2. Caption: Max 2 sentences. Tell the story of what happened during the session using past-tense action verbs. Do not use words like 'median', 'parameters', or 'telemetry'.\n"
        f"3. Stat Callout: The big metric callout (e.g., '18.6s GONE', 'GAP ERASED').\n"
        f"4. NO MARKDOWN: Never output asterisks (**), bold tags, or hashtags.\n\n"
        f"Data points: {json.dumps(insight['data_points'])}\n"
        f"Context details: {insight['narrative_hint']}\n\n"
        f"Return EXCLUSIVELY a clean JSON object with keys: headline, caption, stat_callout."
    )

    api_key_primary = os.getenv("GEMINI_API_KEY")
    api_key_backup = os.getenv("GEMINI_API_KEY_BACKUP")
    
    keys = [api_key_primary, api_key_backup] if api_key_primary else [api_key_backup]

    for key in keys:
        if not key:
            continue
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.85 
                ),
            )
            return json.loads(response.text.strip())
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                import time
                print(f"⚠️ API Key quota exhausted. Pausing for 5 seconds before trying next key...")
                time.sleep(5)
                continue
            else:
                # We catch invalid API keys or other issues and seamlessly drop to fallback
                print(f"⚠️ Gemini API Error: {e}")
                break

    print(f"⚠️ Both keys exhausted limits or failed. Using local programmatic fallback.")

    return {
        "headline": "GAP COLLAPSED!",
        "caption": "The chasing car put down an absolute masterclass and caught the leader at an unprecedented rate.",
        "stat_callout": "GAP ERASED"
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
