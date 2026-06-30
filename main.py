# main.py
import argparse
import os
import sqlite3
import pandas as pd
import base64
from loader import load_session_data
from analyzer import generate_insights
from narrator import generate_narrative
from renderer import render_graphic

# Complete 2026 Grid Bunching directly aligned with image_553b1d.png
TEAM_PROFILES = {
    # Red Bull Racing
    "VER": {"logo": "Max-Verstappen-Logo-700x394.png", "color": "#061D41"},
    "HAD": {"logo": "oracle_red_bull_racing-logo_brandlogos.net_ktyln.png", "color": "#061D41"},
    
    # Aston Martin
    "ALO": {"logo": "Fernando-Alonso-Logo-700x394.png", "color": "#006F62"},
    "STR": {"logo": "Lance-Stroll-Logo-700x394.png", "color": "#006F62"},
    
    # Haas F1 Team
    "BEA": {"logo": "tgr_haas_f1_team-logo_brandlogos.net_4cn45.png", "color": "#E60000"},
    "OCO": {"logo": "Esteban-Ocon-Logo-700x394.png", "color": "#E60000"},
    
    # Racing Bulls
    "LAW": {"logo": "visa-cash-app-racing-bulls-formula-one-team-logo.png", "color": "#0045B5"},
    "LIN": {"logo": "visa-cash-app-racing-bulls-formula-one-team-logo.png", "color": "#0045B5"},
    
    # Audi F1 Team (Gabriel Bortoleto / Nico Hulkenberg)
    "BOR": {"logo": "formula-1-seeklogo.png", "color": "#A6192E"},
    "HUL": {"logo": "formula-1-seeklogo.png", "color": "#A6192E"},
    
    # Ferrari
    "LEC": {"logo": "Charles-Leclerc-Logo-700x394.png", "color": "#EF1A2D"},
    "HAM": {"logo": "Lewis-Hamilton-Logo-700x394.png", "color": "#EF1A2D"},
    
    # Mercedes
    "RUS": {"logo": "George-Russel-Logo-700x394.png", "color": "#00A69C"},
    "ANT": {"logo": "mercedes-amg_petronas_f1_team-logo_brandlogos.net_m9qjq.png", "color": "#00A69C"},
    
    # Williams
    "ALB": {"logo": "atlassian_williams_f1_team-logo_brandlogos.net_stzcn.png", "color": "#24A1FF"},
    "SAI": {"logo": "Carlos-Sainz-Logo-700x394.png", "color": "#24A1FF"},
    
    # Alpine
    "GAS": {"logo": "Pierre-Gasly-Logo-700x394.png", "color": "#0093CC"},
    "COL": {"logo": "alpine_f1_team-logo_brandlogos.net_4ny0w.png", "color": "#0093CC"},

    # Cadillac
    "PER": {"logo": "Sergio-Perez-Logo-700x394.png", "color": "#DEB900"},
    "BOT": {"logo": "Valtteri-Bottas-Logo-700x394.png", "color": "#DEB900"}
}

def get_base64_image(file_path):
    """Encodes a local file into a browser-safe data URI string."""
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                return f"data:image/png;base64,{encoded}"
        except Exception as e:
            print(f"⚠️ Base64 encoding failed for {file_path}: {e}")
    return ""

def get_driver_team_relation(driver_code, db_path="f1_data.db"):
    try:
        conn = sqlite3.connect(db_path)
        # Column names in DB might be uppercase like Driver and Team based on previous loader logic
        df = pd.read_sql_query(f"SELECT * FROM laps WHERE Driver='{driver_code}' LIMIT 1", conn)
        conn.close()
        if not df.empty and 'Team' in df.columns:
            return df.iloc[0]['Team']
    except Exception as e:
        pass
    return "Formula 1"

def run_pipeline(year, round_num, session):
    # Sync and get basic profiles
    load_session_data(year, round_num, session, "f1_data.db")
    insights = generate_insights("f1_data.db")
    
    output_dir = f"output/round_{round_num}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logo_base_dir = r"E:\PITwall Post\logos"

    for idx, insight in enumerate(insights[:5], start=1):
        raw_driver = insight["drivers_involved"][0] if insight["drivers_involved"] else "F1"
        
        # FIX 1: Enforce uppercase to eliminate case-sensitivity mismatches
        driver_code = str(raw_driver).upper().strip()
        team_name = get_driver_team_relation(driver_code)
        
        # Pull profile details, fallback to classic F1 Red if missing
        profile = TEAM_PROFILES.get(driver_code, {"logo": "formula-1-seeklogo.png", "color": "#E10600"})
        
        # Generate our brand new viral narrative caption text block
        narrative = generate_narrative(insight)

        # FIX 2: Resolve logos through absolute Base64 data streaming
        logo_filename = profile["logo"]
        logo_path_local = os.path.join(logo_base_dir, logo_filename) if logo_filename else ""
        base64_uri = get_base64_image(logo_path_local)

        brand_logo_filename = "pitwall_logo.png"
        brand_logo_path_local = os.path.join(logo_base_dir, brand_logo_filename)
        brand_base64_uri = get_base64_image(brand_logo_path_local)

        render_payload = {
            "stat_callout": narrative["stat_callout"],
            "headline": narrative["headline"],
            "caption": narrative["caption"],
            "session_text": f"2026 LIVE TELEMETRY // DATA STREAM",
            "color": profile["color"], 
            "logo_path": base64_uri,
            "brand_logo_path": brand_base64_uri
        }

        filename = f"{idx:02d}_{insight['type']}_{driver_code.lower()}.png"
        target_path = os.path.join(output_dir, filename)

        render_graphic(render_payload, "stat_card.html", target_path)
        print(f"🏁 Asset successfully saved: {target_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--round", type=int, default=1)
    parser.add_argument("--session", type=str, default="R")
    args = parser.parse_args()

    run_pipeline(args.year, args.round, args.session)

if __name__ == "__main__":
    main()
