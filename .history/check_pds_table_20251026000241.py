#!/usr/bin/env python3
"""
Check for pds_candidates table
"""

import sqlite3

def check_pds_table():
    conn = sqlite3.connect('resume_screening.db')
    cursor = conn.cursor()

    # Check if pds_candidates table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pds_candidates'")
    result = cursor.fetchone()

    if result:
        print('✅ pds_candidates table exists')
        
        # Get column info
        cursor.execute('PRAGMA table_info(pds_candidates)')
        columns = [row[1] for row in cursor.fetchall()]
        print(f'Columns: {columns}')
        
        # Get count
        cursor.execute('SELECT COUNT(*) FROM pds_candidates')
        count = cursor.fetchone()[0]
        print(f'Records: {count}')
        
        if count > 0:
            cursor.execute('SELECT id, name, email, phone FROM pds_candidates LIMIT 3')
            for row in cursor.fetchall():
                print(f'Sample: ID={row[0]}, Name={row[1]}, Email={row[2]}, Phone={row[3]}')
    else:
        print('❌ pds_candidates table does not exist')
        
        # Show available tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f'Available tables: {tables}')

    conn.close()

if __name__ == "__main__":
    check_pds_table()