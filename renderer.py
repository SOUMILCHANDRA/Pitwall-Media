import json
import os
import argparse
from playwright.sync_api import sync_playwright

def team_color(driver):
    # Mapping for 2024/2025 colors roughly
    colors = {
        'VER': '#3671C6', 'PER': '#3671C6', # Red Bull
        'LEC': '#E80020', 'SAI': '#E80020', 'HAM': '#E80020', # Ferrari (HAM in 2025)
        'NOR': '#FF8000', 'PIA': '#FF8000', # McLaren
        'RUS': '#27F4D2', 'ANTONELLI': '#27F4D2', # Mercedes
        'ALO': '#229971', 'STR': '#229971', # Aston Martin
        # Add more or fallback
    }
    return colors.get(driver, '#ffffff')

LOGO_MAPPING = {
    # Drivers
    "SAI": "Carlos-Sainz-Logo-700x394.png",
    "LEC": "Charles-Leclerc-Logo-700x394.png",
    "OCO": "Esteban-Ocon-Logo-700x394.png",
    "ALO": "Fernando-Alonso-Logo-700x394.png",
    "RUS": "George-Russel-Logo-700x394.png", 
    "STR": "Lance-Stroll-Logo-700x394.png",
    "NOR": "Lando-Norris-Logo-700x394.png",
    "HAM": "Lewis-Hamilton-Logo-700x394.png",
    "VER": "Max-Verstappen-Logo-700x394.png",
    "GAS": "Pierre-Gasly-Logo-700x394.png",
    "PER": "Sergio-Perez-Logo-700x394.png",
    "BOT": "Valtteri-Bottas-Logo-700x394.png",
    
    # Teams / Overrides (Fallback if driver asset isn't needed)
    "ALPINE": "alpine_f1_team-logo_brandlogos.net_4ny0w.png",
    "ASTON MARTIN": "aston-martin-aramco-formula-one-team-2024-logo.png",
    "WILLIAMS": "atlassian_williams_f1_team-logo_brandlogos.net_stzcn.png",
    "HAAS": "tgr_haas_f1_team-logo_brandlogos.net_4cn45.png",
    "MCLAREN": "mclaren-formula-1-team-seeklogo.png",
    "MERCEDES": "mercedes-amg_petronas_f1_team-logo_brandlogos.net_m9qjq.png",
    "RED BULL": "oracle_red_bull_racing-logo_brandlogos.net_ktyln.png",
    "FERRARI": "scuderia_ferrari-logo_brandlogos.net_uupa6.png",
    "RB": "visa-cash-app-racing-bulls-formula-one-team-logo.png",
    "SAUBER": "cadillac-formula-1-team-seeklogo.png"
}

def render_insights(narrated_insights_path='narrated_insights.json', output_dir='output'):
    try:
        with open(narrated_insights_path, 'r') as f:
            insights = json.load(f)
    except FileNotFoundError:
        print("No narrated insights found.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    template_path = f"file:///{os.path.abspath('templates/stat_card.html').replace(chr(92), '/')}"
    logo_base_dir = r"E:\PITwall Post\logos"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1080, 'height': 1080})
        
        for i, insight in enumerate(insights):
            driver = insight.get('drivers_involved', [''])[0]
            color = team_color(driver)
            
            logo_filename = LOGO_MAPPING.get(driver, "")
            logo_path = ""
            if logo_filename:
                full_logo_path = os.path.join(logo_base_dir, logo_filename)
                if os.path.exists(full_logo_path):
                    # For local CORS restrictions, pass an absolute file URL string
                    logo_path = "file:///" + full_logo_path.replace("\\", "/")
            
            data = {
                'headline': insight.get('headline', ''),
                'stat_callout': insight.get('stat_callout', ''),
                'caption': insight.get('caption', ''),
                'team_color': color,
                'logo_path': logo_path
            }
            
            page.goto(template_path)
            # Inject data
            page.evaluate(f"window.setData({json.dumps(data)})")
            
            # small wait for rendering if any fonts are loading
            page.wait_for_timeout(500)
            
            filename = f"{i+1:02d}_{insight.get('type', 'insight')}_{driver.lower()}.png"
            filepath = os.path.join(output_dir, filename)
            
            page.screenshot(path=filepath)
            print(f"Rendered {filename}")
            
        browser.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='narrated_insights.json')
    parser.add_argument('--output', type=str, default='output')
    args = parser.parse_args()
    
    render_insights(args.input, args.output)
