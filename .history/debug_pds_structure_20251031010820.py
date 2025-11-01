#!/usr/bin/env python3
"""
Debug script to examine PDS data structure
"""

import requests
import json
import sqlite3
import os

def get_candidate_pds_data():
    """Get the actual PDS data structure from the database"""
    
    try:
        # Use SQLite database
        db_path = os.path.join(os.path.dirname(__file__), 'resume_screening.db')
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return None
            
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        
        cursor = conn.cursor()
        
        # Get candidate 4's PDS data (from the available candidates)
        cursor.execute("""
            SELECT name, pds_extracted_data 
            FROM candidates 
            WHERE id = 4
        """)
        
        result = cursor.fetchone()
        if result:
            name, pds_data = result
            print(f"=== CANDIDATE: {name} ===")
            
            if isinstance(pds_data, str):
                pds_dict = json.loads(pds_data)
            else:
                pds_dict = pds_data
                
            print("\n=== PDS DATA STRUCTURE ===")
            print(f"Top-level keys: {list(pds_dict.keys()) if isinstance(pds_dict, dict) else type(pds_dict)}")
            
            if isinstance(pds_dict, dict):
                # Check educational_background structure
                edu_bg = pds_dict.get('educational_background', None)
                print(f"\n=== EDUCATIONAL_BACKGROUND ===")
                print(f"Type: {type(edu_bg)}")
                print(f"Value: {edu_bg}")
                
                if isinstance(edu_bg, list) and edu_bg:
                    print(f"First education entry: {edu_bg[0]}")
                    if isinstance(edu_bg[0], dict):
                        print(f"Education entry keys: {list(edu_bg[0].keys())}")
                
                # Check other relevant fields
                print(f"\n=== OTHER EDUCATION FIELDS ===")
                for key in pds_dict.keys():
                    if 'education' in key.lower():
                        print(f"{key}: {pds_dict[key]}")
                        
                # Check experience structure
                work_exp = pds_dict.get('work_experience', None)
                print(f"\n=== WORK_EXPERIENCE ===")
                print(f"Type: {type(work_exp)}")
                if isinstance(work_exp, list) and work_exp:
                    print(f"First work entry: {work_exp[0]}")
                    
                # Check training structure
                training = pds_dict.get('learning_development', None)
                print(f"\n=== LEARNING_DEVELOPMENT ===")
                print(f"Type: {type(training)}")
                if isinstance(training, list) and training:
                    print(f"First training entry: {training[0]}")
        else:
            print("❌ Candidate 4 not found")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_candidate_pds_data()