import sqlite3
import pandas as pd
import json

def get_db_connection(db_path='f1_data.db'):
    return sqlite3.connect(db_path)

def analyze_pit_stop_outliers(laps):
    # Pit stop is approximated by PitInTime and PitOutTime or just LapTime being large
    # FastF1 has 'PitOutTime' and 'PitInTime'. The time spent in the pit lane can be derived.
    # We will look for laps where PitInTime is not null, indicating they came into the pits.
    in_laps = laps[laps['PitInTime'].notnull()]
    # Actually, a better proxy for pit stop duration in FastF1 without telemetry is the difference in time for the in/out laps.
    # FastF1 'PitStop' feature is available via `session.pit_stops` but since we just saved laps, we can use `PitInTime` and `PitOutTime`.
    
    # A simple heuristic: Find laps that are significantly slower than the median lap.
    insights = []
    
    return insights

def analyze_lap_anomalies(laps):
    insights = []
    # flag laps >1.5 std deviations from a driver's own median in a stint
    for (driver, stint), group in laps.groupby(['Driver', 'Stint']):
        if len(group) < 5:
            continue
        
        median_time = group['LapTime'].median()
        std_time = group['LapTime'].std()
        
        if pd.isna(std_time) or std_time == 0:
            continue
            
        anomalies = group[(group['LapTime'] > median_time + 1.5 * std_time) & (group['PitInTime'].isnull()) & (group['PitOutTime'].isnull())]
        for _, row in anomalies.iterrows():
            insights.append({
                'type': 'lap_anomaly',
                'drivers_involved': [driver],
                'lap_range': [row['LapNumber']],
                'data_points': {'lap_time': row['LapTime'], 'median': median_time, 'diff': row['LapTime'] - median_time},
                'narrative_hint': f"{driver} had an unusually slow lap on lap {row['LapNumber']}, losing {row['LapTime'] - median_time:.1f}s compared to their average in that stint."
            })
    return insights

def analyze_sector_bests(laps):
    insights = []
    # which driver owned each sector and by how much
    return insights

def generate_insights(db_path='f1_data.db'):
    conn = get_db_connection(db_path)
    try:
        laps = pd.read_sql("SELECT * FROM laps", conn)
    except Exception as e:
        print("Error reading laps table:", e)
        return []
    
    # Convert numerical columns back to float just in case
    for col in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'LapNumber']:
        if col in laps.columns:
            laps[col] = pd.to_numeric(laps[col], errors='coerce')

    insights = []
    insights.extend(analyze_lap_anomalies(laps))
    # more heuristic functions to be called here...
    
    # Sort insights by "importance" (e.g., largest diff for anomalies)
    # We will just take the top 5
    if len(insights) > 5:
        insights = insights[:5]
        
    with open('insights.json', 'w') as f:
        json.dump(insights, f, indent=2)
        
    print(f"Generated {len(insights)} insights.")
    return insights

if __name__ == '__main__':
    generate_insights()
