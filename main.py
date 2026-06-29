import argparse
import os
import loader
import analyzer
import narrator
import renderer

def run_pipeline(year, round_num, session_type):
    print(f"--- Starting F1 Pipeline for {year} Round {round_num} Session {session_type} ---")
    
    db_path = 'f1_data.db'
    output_dir = f"output/round_{round_num}"
    
    print("\n[1/4] Loading Data...")
    loader.load_session_data(year, round_num, session_type, db_path)
    
    print("\n[2/4] Analyzing Data...")
    analyzer.generate_insights(db_path)
    
    print("\n[3/4] Generating Narratives...")
    narrator.generate_narratives('insights.json')
    
    print("\n[4/4] Rendering Graphics...")
    renderer.render_insights('narrated_insights.json', output_dir)
    
    print(f"\n--- Pipeline Complete! Check {output_dir} for outputs ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="F1 Post-Race Pipeline")
    parser.add_argument('--year', type=int, required=True, help="Season year (e.g., 2024)")
    parser.add_argument('--round', type=int, required=True, help="Round number (e.g., 1)")
    parser.add_argument('--session', type=str, required=True, help="Session type (e.g., R for Race, Q for Qualifying)")
    
    args = parser.parse_args()
    
    run_pipeline(args.year, args.round, args.session)
