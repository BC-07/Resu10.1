#!/usr/bin/env python3
"""
Test database connection and determine database type
"""

import os
import sys

# Import database manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import DatabaseManager
    
    print("🔍 Testing Database Connection")
    print("=" * 40)
    
    try:
        db_manager = DatabaseManager()
        print(f"✅ DatabaseManager initialized")
        print(f"   Database Type: {'SQLite' if db_manager.use_sqlite else 'PostgreSQL'}")
        
        if db_manager.use_sqlite:
            print(f"   SQLite Mode: {db_manager.use_sqlite}")
            
            # Check for SQLite files
            possible_files = [
                'resume_screening.db',
                'instance/resume_screening.db', 
                'resumeai.db',
                'candidates.db',
                'pds_assessment.db'
            ]
            
            print(f"   SQLite files found:")
            base_dir = os.path.dirname(os.path.dirname(__file__))
            for file in possible_files:
                path = os.path.join(base_dir, file)
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"     ✅ {file} ({size} bytes)")
                else:
                    print(f"     ❌ {file} (not found)")
                    
        else:
            try:
                # Test PostgreSQL connection
                conn = db_manager.get_connection()
                print(f"   ✅ PostgreSQL connection successful")
                cursor = conn.cursor()
                cursor.execute("SELECT current_database()")
                result = cursor.fetchone()
                print(f"   Database: {result[0] if result else 'Unknown'}")
                cursor.close()
                conn.close()
                    
            except Exception as e:
                print(f"   ❌ PostgreSQL connection failed: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ DatabaseManager initialization failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Could not import DatabaseManager: {e}")
    sys.exit(1)