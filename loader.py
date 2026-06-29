import fastf1
import sqlite3
import pandas as pd
import os
import argparse

def init_db(db_path='f1_data.db'):
    conn = sqlite3.connect(db_path)
    return conn

def load_session_data(year, round_num, session_type, db_path='f1_data.db'):
    # Enable cache
    if not os.path.exists('cache'):
        os.makedirs('cache')
    fastf1.Cache.enable_cache('cache')

    print(f"Loading data for {year} Round {round_num} Session {session_type}...")
    session = fastf1.get_session(year, round_num, session_type)
    session.load(telemetry=False, weather=False)
    
    conn = init_db(db_path)
    
    # 1. Lap times
    laps = session.laps
    if not laps.empty:
        # Keep relevant columns and convert timedeltas
        timedelta_cols = ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Time', 'PitOutTime', 'PitInTime']
        for col in timedelta_cols:
            if col in laps.columns:
                laps[col] = laps[col].dt.total_seconds()
                
        # FastF1 returns some complex types, convert to string where necessary or drop
        laps_db = laps.copy()
        
        # Save to SQLite
        # Convert any remaining objects to string just in case
        for col in laps_db.columns:
            if laps_db[col].dtype == 'object':
                laps_db[col] = laps_db[col].astype(str)
                
        laps_db.to_sql('laps', conn, if_exists='replace', index=False)
        print(f"Saved {len(laps_db)} laps to DB.")

    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--round', type=int, required=True)
    parser.add_argument('--session', type=str, required=True)
    args = parser.parse_args()
    
    load_session_data(args.year, args.round, args.session)
