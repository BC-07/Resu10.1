#!/usr/bin/env python3
"""
Check database structure for candidates
"""

import sqlite3

def check_databases():
    databases = ['candidates.db', 'resumeai.db', 'resume_screening.db']

    for db_name in databases:
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f'\n=== {db_name} ===')
            print(f'Tables: {tables}')
            
            # Check if candidates table exists
            if 'candidates' in tables:
                cursor.execute('SELECT COUNT(*) FROM candidates')
                count = cursor.fetchone()[0]
                print(f'  -> candidates table has {count} records')
                
                # Get column names
                cursor.execute('PRAGMA table_info(candidates)')
                columns = [row[1] for row in cursor.fetchall()]
                print(f'  -> columns: {columns}')
                
                # Get a sample record
                if count > 0:
                    cursor.execute('SELECT * FROM candidates LIMIT 1')
                    sample = cursor.fetchone()
                    print(f'  -> sample record exists: {bool(sample)}')
            
            conn.close()
        except Exception as e:
            print(f'{db_name}: Error - {e}')

if __name__ == "__main__":
    check_databases()