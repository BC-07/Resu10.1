#!/usr/bin/env python3
"""
Check actual PDS data in candidates table
"""

import sqlite3
import json

def check_candidate_pds_data():
    conn = sqlite3.connect('resume_screening.db')
    cursor = conn.cursor()

    # Check for pds_extracted_data field
    cursor.execute('PRAGMA table_info(candidates)')
    columns = [row[1] for row in cursor.fetchall()]
    print(f'Available columns: {columns}')
    
    # Check for candidates with PDS data
    if 'pds_extracted_data' in columns:
        print('\n✅ pds_extracted_data column exists')
        
        # Get candidates with non-null PDS data
        cursor.execute('SELECT id, name, email, phone, pds_extracted_data FROM candidates WHERE pds_extracted_data IS NOT NULL AND pds_extracted_data != "" LIMIT 3')
        pds_candidates = cursor.fetchall()
        
        print(f'Candidates with PDS data: {len(pds_candidates)}')
        
        for candidate in pds_candidates:
            candidate_id, name, email, phone, pds_data_str = candidate
            print(f'\n=== Candidate {candidate_id}: {name} ===')
            
            if pds_data_str:
                try:
                    pds_data = json.loads(pds_data_str)
                    print(f'PDS keys: {list(pds_data.keys())}')
                    
                    if 'personal_info' in pds_data:
                        personal_info = pds_data['personal_info']
                        print(f'Personal info keys: {list(personal_info.keys())}')
                        print(f'  Full name: {personal_info.get("full_name")}')
                        print(f'  First name: {personal_info.get("first_name")}')
                        print(f'  Surname: {personal_info.get("surname")}')
                        print(f'  Mobile: {personal_info.get("mobile_no")}')
                        print(f'  Email: {personal_info.get("email")}')
                    else:
                        print('No personal_info section found')
                        print(f'Available sections: {list(pds_data.keys())}')
                        
                except Exception as e:
                    print(f'Error parsing PDS data: {e}')
                    print(f'Raw data sample: {pds_data_str[:200]}...')
    else:
        print('❌ pds_extracted_data column not found')
        
        # Check other possible PDS fields
        pds_fields = [field for field in columns if 'pds' in field.lower()]
        print(f'PDS-related fields found: {pds_fields}')

    conn.close()

if __name__ == "__main__":
    check_candidate_pds_data()