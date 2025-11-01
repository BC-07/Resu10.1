#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

def check_database_structure():
    """Check database structure to understand why assessments return 0"""
    
    print("🔍 CHECKING DATABASE STRUCTURE")
    print("=" * 40)
    
    db = DatabaseManager()
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # List all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            print("📊 AVAILABLE TABLES:")
            table_names = []
            for table in tables:
                table_name = table[0]
                table_names.append(table_name)
                
                # Count records in each table
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"   {table_name}: {count} records")
                except Exception as e:
                    print(f"   {table_name}: Error counting - {e}")
            
            # Check if pds_candidates exists
            print(f"\n🔍 PDS CANDIDATES TABLE:")
            if 'pds_candidates' in table_names:
                print("   ✅ pds_candidates table exists")
                
                cursor.execute("SELECT COUNT(*) FROM pds_candidates")
                pds_count = cursor.fetchone()[0]
                print(f"   Records: {pds_count}")
                
                if pds_count > 0:
                    cursor.execute("""
                        SELECT id, name, email, 
                               CASE WHEN education IS NULL THEN 'NULL'
                                    WHEN education = '' THEN 'EMPTY'
                                    ELSE 'HAS_DATA' END as education_status,
                               CASE WHEN work_experience IS NULL THEN 'NULL'
                                    WHEN work_experience = '' THEN 'EMPTY'
                                    ELSE 'HAS_DATA' END as experience_status
                        FROM pds_candidates 
                        LIMIT 3
                    """)
                    samples = cursor.fetchall()
                    
                    print("   Sample PDS records:")
                    for sample in samples:
                        print(f"     ID {sample[0]}: {sample[1]} - Education: {sample[3]}, Experience: {sample[4]}")
                
            else:
                print("   ❌ pds_candidates table MISSING!")
                print("   This is likely why assessment scores are 0")
            
            # Check regular candidates table
            print(f"\n📋 REGULAR CANDIDATES TABLE:")
            if 'candidates' in table_names:
                cursor.execute("SELECT COUNT(*) FROM candidates")
                count = cursor.fetchone()[0]
                print(f"   Records: {count}")
                
                if count > 0:
                    cursor.execute("""
                        SELECT id, full_name,
                               CASE WHEN education IS NULL THEN 'NULL'
                                    WHEN education = '' THEN 'EMPTY'
                                    ELSE 'HAS_DATA' END as education_status,
                               CASE WHEN work_experience IS NULL THEN 'NULL'
                                    WHEN work_experience = '' THEN 'EMPTY'
                                    ELSE 'HAS_DATA' END as experience_status,
                               CASE WHEN learning_development IS NULL THEN 'NULL'
                                    WHEN learning_development = '' THEN 'EMPTY'
                                    ELSE 'HAS_DATA' END as training_status
                        FROM candidates 
                        LIMIT 3
                    """)
                    samples = cursor.fetchall()
                    
                    print("   Sample candidates:")
                    for sample in samples:
                        print(f"     ID {sample[0]}: {sample[1]}")
                        print(f"       Education: {sample[2]}, Experience: {sample[3]}, Training: {sample[4]}")
            
            # Check job postings
            print(f"\n💼 JOB POSTINGS:")
            if 'job_postings' in table_names:
                cursor.execute("SELECT COUNT(*) FROM job_postings")
                job_count = cursor.fetchone()[0]
                print(f"   Jobs: {job_count}")
                
                if job_count > 0:
                    cursor.execute("SELECT id, title FROM job_postings LIMIT 2")
                    jobs = cursor.fetchall()
                    for job in jobs:
                        print(f"     ID {job[0]}: {job[1]}")
            
    except Exception as e:
        print(f"❌ Database check error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_structure()