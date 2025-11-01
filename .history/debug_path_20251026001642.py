#!/usr/bin/env python3
"""
Debug which database path is being used
"""

import sys
import os
from database import DatabaseManager

def debug_database_path():
    print("🔍 Debugging Database Path")
    print("=" * 40)
    
    try:
        # Initialize database
        db = DatabaseManager()
        
        print(f"use_sqlite: {db.use_sqlite}")
        
        # Test getting a single candidate with debugging
        print("\n🧪 Testing get_candidate(406)...")
        candidate = db.get_candidate(406)
        
        if candidate and candidate.get('pds_data') and candidate['pds_data'].get('personal_info'):
            personal_info = candidate['pds_data']['personal_info']
            full_name = personal_info.get('full_name')
            print(f"Result from get_candidate: '{full_name}'")
        else:
            print("No valid data from get_candidate")
        
        # Test getting all candidates
        print("\n🧪 Testing get_all_candidates()...")
        candidates = db.get_all_candidates()
        
        # Find candidate 406
        candidate_406 = None
        for c in candidates:
            if c['id'] == 406:
                candidate_406 = c
                break
        
        if candidate_406 and candidate_406.get('pds_data') and candidate_406['pds_data'].get('personal_info'):
            personal_info = candidate_406['pds_data']['personal_info']
            full_name = personal_info.get('full_name')
            print(f"Result from get_all_candidates: '{full_name}'")
        else:
            print("No valid data from get_all_candidates")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database_path()