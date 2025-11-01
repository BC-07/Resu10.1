#!/usr/bin/env python3
"""
Check database schema for candidates table
"""

import os
import sys

# Import database manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import DatabaseManager
    
    print("🔍 Checking candidates table schema")
    print("=" * 40)
    
    db_manager = DatabaseManager()
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'candidates'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    print(f"📊 Candidates table columns:")
    for col in columns:
        if hasattr(col, 'keys'):  # RealDictRow
            print(f"   {col['column_name']} ({col['data_type']}) - nullable: {col['is_nullable']}")
        else:  # tuple
            print(f"   {col[0]} ({col[1]}) - nullable: {col[2]}")
    
    # Get sample data
    cursor.execute("SELECT * FROM candidates LIMIT 3")
    sample_data = cursor.fetchall()
    
    print(f"\n📋 Sample data ({len(sample_data)} rows):")
    for i, row in enumerate(sample_data):
        print(f"\n   Row {i+1}:")
        if hasattr(row, 'keys'):  # RealDictRow
            for key, value in row.items():
                value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"      {key}: {value_str}")
        else:  # tuple
            for j, value in enumerate(row):
                value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"      Column {j}: {value_str}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()