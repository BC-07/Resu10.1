#!/usr/bin/env python3
"""
Test script with debugging to see why name cleaning isn't working
"""

import sys
import os
from database import DatabaseManager

def test_name_cleaning_debug():
    print("🧪 Testing Name Cleaning with Debug")
    print("=" * 50)
    
    try:
        # Initialize database
        db = DatabaseManager()
        
        # Get specific candidate that has N/a in name
        candidate = db.get_candidate(406)  # MARK RAINIER SORIANO COPIOSO N/a
        
        if candidate:
            print(f"👤 Testing Candidate ID: {candidate['id']}")
            
            if candidate.get('pds_data'):
                print("✅ PDS data exists")
                personal_info = candidate['pds_data'].get('personal_info')
                
                if personal_info:
                    print("✅ Personal info exists")
                    full_name = personal_info.get('full_name')
                    print(f"📝 Current full_name: '{full_name}'")
                    
                    # Test the cleaning logic manually
                    if full_name:
                        print("🔧 Testing cleaning logic...")
                        import re
                        cleaned = re.sub(r'\s+N/a$', '', full_name, flags=re.IGNORECASE)
                        cleaned = re.sub(r'\s+None$', '', cleaned, flags=re.IGNORECASE)
                        cleaned = cleaned.strip()
                        print(f"🧹 After cleaning: '{cleaned}'")
                        
                        if cleaned != full_name:
                            print("✅ Cleaning would change the name!")
                        else:
                            print("❌ Cleaning had no effect")
                    else:
                        print("❌ No full_name to clean")
                else:
                    print("❌ No personal_info section")
            else:
                print("❌ No pds_data")
        else:
            print("❌ Candidate not found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_name_cleaning_debug()