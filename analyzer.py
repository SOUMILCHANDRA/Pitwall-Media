import sqlite3
import pandas as pd
import json

def generate_insights(db_path='f1_data.db'):
    conn = sqlite3.connect(db_path)
    
    # Read the full laps table; loader.py replaces this per session so we don't need year/round filters
    try:
        df_laps = pd.read_sql_query("SELECT * FROM laps ORDER BY LapNumber ASC", conn)
    except Exception as e:
        print("Error reading laps:", e)
        df_laps = pd.DataFrame()
        
    conn.close()
    
    insights = []
    if df_laps.empty:
        return insights

    # Convert numeric columns safely
    for col in ['LapNumber', 'LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Position']:
        if col in df_laps.columns:
            df_laps[col] = pd.to_numeric(df_laps[col], errors='coerce')

    laps_count = int(df_laps['LapNumber'].max())

    # --- 1. GAP COLLAPSE DETECTION (THE CHASE) ---
    for lap in range(2, laps_count + 1):
        current_lap = df_laps[df_laps['LapNumber'] == lap].sort_values('Position')
        
        # We need pairs of cars running nose to tail
        for i in range(len(current_lap) - 1):
            p1_driver = current_lap.iloc[i]['Driver']
            p2_driver = current_lap.iloc[i+1]['Driver']
            
            p1_time = current_lap.iloc[i]['LapTime']
            p2_time = current_lap.iloc[i+1]['LapTime']
            
            if pd.notna(p1_time) and pd.notna(p2_time):
                delta_change = p1_time - p2_time # Positive means trailing car caught up
                if delta_change > 0.8: # Catching by more than 0.8s in a single lap
                    insights.append({
                        "type": "gap_collapse",
                        "drivers_involved": [p2_driver, p1_driver],
                        "lap_range": [int(lap-1), int(lap)],
                        "data_points": {"rate": round(delta_change, 1), "lap": int(lap)},
                        "narrative_hint": f"{p2_driver} is absolutely hunting down {p1_driver}, closing the gap by {round(delta_change, 1)}s on lap {lap}.",
                        "score": float(delta_change) * 12 # High weight score multiplier
                    })

    # --- 2. UNDERCUT / OVERCUT STRATEGY DETECTION ---
    # Derive pit stops from PitInTime
    if 'PitInTime' in df_laps.columns:
        df_pits = df_laps[df_laps['PitInTime'].notna()]
        for _, pit in df_pits.iterrows():
            p_driver = pit['Driver']
            p_lap = pit['LapNumber']
            
            pre_pit = df_laps[(df_laps['Driver'] == p_driver) & (df_laps['LapNumber'] == p_lap - 2)]
            post_pit = df_laps[(df_laps['Driver'] == p_driver) & (df_laps['LapNumber'] == p_lap + 2)]
            
            if not pre_pit.empty and not post_pit.empty:
                pos_gained = pre_pit.iloc[0]['Position'] - post_pit.iloc[0]['Position']
                if pos_gained > 0:
                    insights.append({
                        "type": "undercut",
                        "drivers_involved": [p_driver],
                        "lap_range": [int(p_lap-2), int(p_lap+2)],
                        "data_points": {"positions_gained": int(pos_gained), "pit_lap": int(p_lap)},
                        "narrative_hint": f"Brilliant strategy call! {p_driver} executed a flawless pit stop sequence on lap {p_lap} to jump {pos_gained} places forward.",
                        "score": float(pos_gained) * 15
                    })

    # --- 3. SECTOR DOMINANCE BESTS ---
    for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
        if sector in df_laps.columns:
            valid_sectors = df_laps.dropna(subset=[sector])
            if not valid_sectors.empty:
                fastest_lap_row = valid_sectors.loc[valid_sectors[sector].idxmin()]
                sec_name = sector.replace('Time', '').replace('Sector', 'Sector ').upper()
                insights.append({
                    "type": "sector_best",
                    "drivers_involved": [fastest_lap_row['Driver']],
                    "lap_range": [int(fastest_lap_row['LapNumber']), int(fastest_lap_row['LapNumber'])],
                    "data_points": {"time": round(fastest_lap_row[sector], 3), "sector": sec_name},
                    "narrative_hint": f"{fastest_lap_row['Driver']} completely owned {sec_name} with an unmatched blistering sector benchmark.",
                    "score": 10.0 # Standard benchmark score layout baseline
                })

    # --- 4. LAP TIME ANOMALIES (CRASHES / ERRORS) ---
    # FastF1 TrackStatus '1' usually means green flag
    if 'TrackStatus' in df_laps.columns:
        clean_laps = df_laps[df_laps['TrackStatus'].astype(str).str.contains('1')]
    else:
        clean_laps = df_laps
        
    for driver, group in clean_laps.groupby('Driver'):
        median = group['LapTime'].median()
        std = group['LapTime'].std()
        if pd.notna(median) and pd.notna(std) and std > 0:
            for _, row in group.iterrows():
                if row['LapTime'] > (median + 2.5 * std): # Major drop threshold
                    diff = row['LapTime'] - median
                    insights.append({
                        "type": "lap_anomaly",
                        "drivers_involved": [driver],
                        "lap_range": [int(row['LapNumber']), int(row['LapNumber'])],
                        "data_points": {"time_saved": round(diff, 1), "lap": int(row['LapNumber'])},
                        "narrative_hint": f"{driver} suffered a major pace drop on lap {row['LapNumber']}.",
                        "score": float(diff) * 2 # Reduced weighting to balance single mistakes
                    })

    # =========================================================================
    # THE SMART FILTER: SORT, DEDUPLICATE, AND MIX NARRATIVES
    # =========================================================================
    insights = sorted(insights, key=lambda x: x.get('score', 0), reverse=True)
    
    filtered_insights = []
    seen_drivers_for_anomalies = set()
    seen_types = set()

    for entry in insights:
        d_key = entry["drivers_involved"][0] if entry["drivers_involved"] else "None"
        i_type = entry["type"]

        # Prevent one driver's technical difficulties from filling all visual card output allocations
        if i_type == "lap_anomaly":
            if d_key in seen_drivers_for_anomalies:
                continue
            seen_drivers_for_anomalies.add(d_key)
            
        # Optional: strictly enforce variety so we don't just get 5 'sector_best' cards
        # We can cap sector bests or just let the score dictate as requested.

        filtered_insights.append(entry)
        if len(filtered_insights) >= 5:
            break

    # Save to file to ensure the rest of pipeline (or debugging) has access
    with open('insights.json', 'w') as f:
        json.dump(filtered_insights, f, indent=2)

    return filtered_insights

if __name__ == "__main__":
    generate_insights()
