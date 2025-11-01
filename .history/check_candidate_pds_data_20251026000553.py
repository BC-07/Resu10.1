#!/usr/bin/env python3
"""
Check candidate data structure in resume_screening.db
"""

import sqlite3
import json

def check_candidate_data():
    conn = sqlite3.connect('resume_screening.db')
    cursor = conn.cursor()

    # Get a sample candidate to check the data structure
    cursor.execute('SELECT id, name, email, phone, pds_extracted_data FROM candidates LIMIT 1')
    row = cursor.fetchone()

    if row:
        candidate_id, name, email, phone, pds_data_str = row
        print('=== Sample Candidate Data ===')
        print(f'ID: {candidate_id}')
        print(f'Name: {name}')
        print(f'Email: {email}')
        print(f'Phone: {phone}')
        
        if pds_data_str:
            try:
                pds_data = json.loads(pds_data_str)
                print('\n=== PDS Data Structure ===')
                print(f'Top-level keys: {list(pds_data.keys())}')
                
                if 'personal_info' in pds_data:
                    personal_info = pds_data['personal_info']
                    print(f'\nPersonal Info Keys: {list(personal_info.keys())}')
                    print('\nName fields:')
                    print(f'  - first_name: "{personal_info.get("first_name")}"')
                    print(f'  - middle_name: "{personal_info.get("middle_name")}"')
                    print(f'  - surname: "{personal_info.get("surname")}"')
                    print(f'  - full_name: "{personal_info.get("full_name")}"')
                    print(f'  - name_extension: "{personal_info.get("name_extension")}"')
                    print('\nContact fields:')
                    print(f'  - mobile_no: "{personal_info.get("mobile_no")}"')
                    print(f'  - telephone_no: "{personal_info.get("telephone_no")}"')
                    print(f'  - email: "{personal_info.get("email")}"')
                    print('\nOther fields:')
                    print(f'  - date_of_birth: "{personal_info.get("date_of_birth")}"')
                    print(f'  - place_of_birth: "{personal_info.get("place_of_birth")}"')
                    print(f'  - sex: "{personal_info.get("sex")}"')
                    print(f'  - civil_status: "{personal_info.get("civil_status")}"')
                else:
                    print('❌ No personal_info found in PDS data')
                    print('Available keys:', list(pds_data.keys()))
                    # Show some data from other keys
                    for key in list(pds_data.keys())[:3]:
                        print(f'{key} sample: {str(pds_data[key])[:100]}...')
            except Exception as e:
                print(f'❌ Error parsing PDS data: {e}')
                print(f'Raw PDS data (first 200 chars): {pds_data_str[:200]}')
        else:
            print('❌ No PDS data available')
    else:
        print('❌ No candidates found in database')

    conn.close()

if __name__ == "__main__":
    check_candidate_data()