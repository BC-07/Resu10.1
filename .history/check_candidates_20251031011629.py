#!/usr/bin/env python3
"""
Check what candidates exist in the database
"""

import sqlite3
import os
import json

def check_candidates():
    """Check what candidates exist in the database"""
    
    try:
        # Use SQLite database
        db_path = os.path.join(os.path.dirname(__file__), 'resume_screening.db')
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return None
            
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all candidates
        cursor.execute("""
            SELECT id, name, pds_extracted_data 
            FROM candidates 
            ORDER BY id
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        if results:
            print("=== AVAILABLE CANDIDATES ===")
            for candidate_id, name, pds_data in results:
                print(f"ID: {candidate_id}, Name: {name}")
                
                if pds_data:
                    if isinstance(pds_data, str):
                        try:
                            pds_dict = json.loads(pds_data)
                            print(f"  PDS keys: {list(pds_dict.keys()) if isinstance(pds_dict, dict) else type(pds_dict)}")
                            
                            # Check educational_background specifically
                            if isinstance(pds_dict, dict):
                                edu_bg = pds_dict.get('educational_background', None)
                                print(f"  Educational background type: {type(edu_bg)}")
                                if isinstance(edu_bg, list) and edu_bg:
                                    print(f"  First education entry: {edu_bg[0]}")
                                elif isinstance(edu_bg, dict):
                                    print(f"  Education dict keys: {list(edu_bg.keys())}")
                                else:
                                    print(f"  Education value: {edu_bg}")
                        except json.JSONDecodeError as e:
                            print(f"  PDS JSON decode error: {e}")
                    else:
                        print(f"  PDS data type: {type(pds_data)}")
                else:
                    print("  No PDS data")
                print()
        else:
            print("❌ No candidates found")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_candidates()