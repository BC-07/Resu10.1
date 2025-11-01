#!/usr/bin/env python3
"""
Test the updated database mapping for PDS data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database import DatabaseManager
import json

def test_candidate_data_mapping():
    print("🧪 Testing candidate data mapping...")
    
    db_manager = DatabaseManager()
    
    # Get all candidates
    candidates = db_manager.get_all_candidates()
    print(f"Found {len(candidates)} candidates")
    
    # Find a candidate with PDS data
    pds_candidate = None
    for candidate in candidates:
        if candidate.get('pds_data') and isinstance(candidate['pds_data'], dict):
            if candidate['pds_data'].get('personal_info'):
                pds_candidate = candidate
                break
    
    if pds_candidate:
        print(f"\n✅ Found PDS candidate: {pds_candidate['name']} (ID: {pds_candidate['id']})")
        
        # Check personal info
        personal_info = pds_candidate['pds_data']['personal_info']
        print(f"\n📋 Personal Info Fields:")
        print(f"  - first_name: '{personal_info.get('first_name')}'")
        print(f"  - middle_name: '{personal_info.get('middle_name')}'")
        print(f"  - surname: '{personal_info.get('surname')}'") 
        print(f"  - full_name: '{personal_info.get('full_name')}'")
        print(f"  - mobile_no: '{personal_info.get('mobile_no')}'")
        print(f"  - email: '{personal_info.get('email')}'")
        
        # Test individual candidate retrieval
        single_candidate = db_manager.get_candidate(pds_candidate['id'])
        if single_candidate and single_candidate.get('pds_data'):
            single_personal_info = single_candidate['pds_data']['personal_info']
            print(f"\n✅ Single candidate retrieval test:")
            print(f"  - full_name in single retrieval: '{single_personal_info.get('full_name')}'")
            
            if single_personal_info.get('full_name'):
                print("✅ SUCCESS: full_name is now populated!")
            else:
                print("❌ FAILED: full_name is still missing")
        else:
            print("❌ FAILED: Could not retrieve single candidate or no PDS data")
    else:
        print("❌ No candidates with PDS data found")

if __name__ == "__main__":
    test_candidate_data_mapping()