#!/usr/bin/env python3
"""
Test script to verify name cleaning functionality
"""

import sys
import os
from database import DatabaseManager

def test_clean_names():
    print("🧪 Testing Name Cleaning Functionality")
    print("=" * 50)
    
    try:
        # Initialize database
        db = DatabaseManager()
        
        # Get all candidates
        candidates = db.get_all_candidates()
        print(f"📊 Found {len(candidates)} candidates")
        
        # Find PDS candidates and check their names
        pds_candidates = []
        for candidate in candidates:
            if candidate.get('pds_data') and candidate['pds_data'].get('personal_info'):
                pds_candidates.append(candidate)
        
        print(f"📋 Found {len(pds_candidates)} PDS candidates")
        
        for candidate in pds_candidates:
            personal_info = candidate['pds_data']['personal_info']
            full_name = personal_info.get('full_name', 'No full name')
            
            print(f"\n👤 Candidate ID: {candidate['id']}")
            print(f"   Full Name: '{full_name}'")
            print(f"   First: '{personal_info.get('first_name', 'N/A')}'")
            print(f"   Last: '{personal_info.get('surname', 'N/A')}'")
            print(f"   Mobile: '{personal_info.get('mobile_no', 'N/A')}'")
            print(f"   Email: '{personal_info.get('email', 'N/A')}'")
            
            # Check if name was cleaned properly
            if full_name and 'N/a' not in full_name:
                print("   ✅ Name appears clean!")
            elif full_name and 'N/a' in full_name:
                print("   ⚠️  Name still contains 'N/a'")
            else:
                print("   ❌ No full name available")
        
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clean_names()