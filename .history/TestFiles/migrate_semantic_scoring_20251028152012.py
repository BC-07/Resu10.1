#!/usr/bin/env python3
"""
Database Migration: Add Semantic Scoring Fields
Adds semantic score fields to candidates table while preserving existing data
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Import database manager
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import DatabaseManager
except ImportError:
    print("❌ Could not import DatabaseManager. Make sure you're in the project directory.")
    sys.exit(1)

logger = logging.getLogger(__name__)

class SemanticScoringMigration:
    """Migration to add semantic scoring capabilities to the database"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.migration_id = "add_semantic_scoring_v1"
        self.migration_timestamp = datetime.now().isoformat()
    
    def check_migration_needed(self) -> bool:
        """Check if migration is needed by checking for semantic score columns"""
        try:
            if self.db_manager.use_sqlite:
                return self._check_sqlite_migration_needed()
            else:
                return self._check_postgresql_migration_needed()
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return False
    
    def _check_sqlite_migration_needed(self) -> bool:
        """Check if SQLite migration is needed"""
        import sqlite3
        
        # Check both possible SQLite database locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resume_screening.db'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'resume_screening.db'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resumeai.db')
        ]
        
        sqlite_path = None
        for path in possible_paths:
            if os.path.exists(path):
                sqlite_path = path
                break
        
        if not sqlite_path:
            raise FileNotFoundError("No SQLite database found")
        
        with sqlite3.connect(sqlite_path) as conn:
            cursor = conn.cursor()
            
            # Check if candidates table has semantic fields
            cursor.execute("PRAGMA table_info(candidates)")
            columns = cursor.fetchall()
            
            column_names = [col[1] for col in columns]
            
            semantic_fields = ['semantic_score', 'semantic_breakdown', 'semantic_updated']
            missing_fields = [field for field in semantic_fields if field not in column_names]
            
            return len(missing_fields) > 0
    
    def _check_postgresql_migration_needed(self) -> bool:
        """Check if PostgreSQL migration is needed"""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Check if semantic fields exist
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'candidates' 
                    AND column_name IN ('semantic_score', 'semantic_breakdown', 'semantic_updated')
                """)
                
                existing_fields = [row[0] for row in cursor.fetchall()]
                semantic_fields = ['semantic_score', 'semantic_breakdown', 'semantic_updated']
                
                missing_fields = [field for field in semantic_fields if field not in existing_fields]
                
                return len(missing_fields) > 0
    
    def run_migration(self) -> bool:
        """Run the semantic scoring migration"""
        print(f"🔄 Running semantic scoring migration: {self.migration_id}")
        
        try:
            if not self.check_migration_needed():
                print("✅ Migration not needed - semantic fields already exist")
                return True
            
            if self.db_manager.use_sqlite:
                success = self._migrate_sqlite()
            else:
                success = self._migrate_postgresql()
            
            if success:
                self._record_migration()
                print(f"✅ Semantic scoring migration completed successfully")
                return True
            else:
                print(f"❌ Migration failed")
                return False
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            print(f"❌ Migration error: {e}")
            return False
    
    def _migrate_sqlite(self) -> bool:
        """Run SQLite migration"""
        import sqlite3
        
        sqlite_path = os.path.join(os.path.dirname(__file__), 'resume_screening.db')
        
        print("📊 Migrating SQLite database...")
        
        with sqlite3.connect(sqlite_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Add semantic score fields
                print("   Adding semantic_score column...")
                cursor.execute("""
                    ALTER TABLE candidates 
                    ADD COLUMN semantic_score REAL DEFAULT 0.0
                """)
                
                print("   Adding semantic_breakdown column...")
                cursor.execute("""
                    ALTER TABLE candidates 
                    ADD COLUMN semantic_breakdown TEXT DEFAULT '{}'
                """)
                
                print("   Adding semantic_updated column...")
                cursor.execute("""
                    ALTER TABLE candidates 
                    ADD COLUMN semantic_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                
                # Create index for semantic scores
                print("   Creating index on semantic_score...")
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_candidates_semantic_score 
                    ON candidates(semantic_score)
                """)
                
                conn.commit()
                print("✅ SQLite migration completed")
                return True
                
            except Exception as e:
                conn.rollback()
                logger.error(f"SQLite migration failed: {e}")
                return False
    
    def _migrate_postgresql(self) -> bool:
        """Run PostgreSQL migration"""
        print("📊 Migrating PostgreSQL database...")
        
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                
                try:
                    # Add semantic score fields
                    print("   Adding semantic_score column...")
                    cursor.execute("""
                        ALTER TABLE candidates 
                        ADD COLUMN IF NOT EXISTS semantic_score FLOAT DEFAULT 0.0
                    """)
                    
                    print("   Adding semantic_breakdown column...")
                    cursor.execute("""
                        ALTER TABLE candidates 
                        ADD COLUMN IF NOT EXISTS semantic_breakdown JSONB DEFAULT '{}'::jsonb
                    """)
                    
                    print("   Adding semantic_updated column...")
                    cursor.execute("""
                        ALTER TABLE candidates 
                        ADD COLUMN IF NOT EXISTS semantic_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """)
                    
                    # Create index for semantic scores
                    print("   Creating index on semantic_score...")
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_candidates_semantic_score 
                        ON candidates(semantic_score)
                    """)
                    
                    # Create index for semantic breakdown queries
                    print("   Creating index on semantic_breakdown...")
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_candidates_semantic_breakdown 
                        ON candidates USING GIN(semantic_breakdown)
                    """)
                    
                    conn.commit()
                    print("✅ PostgreSQL migration completed")
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"PostgreSQL migration failed: {e}")
                    return False
    
    def _record_migration(self):
        """Record migration in database or log file"""
        migration_record = {
            'migration_id': self.migration_id,
            'timestamp': self.migration_timestamp,
            'description': 'Added semantic scoring fields to candidates table',
            'fields_added': ['semantic_score', 'semantic_breakdown', 'semantic_updated'],
            'database_type': 'sqlite' if self.db_manager.use_sqlite else 'postgresql'
        }
        
        # Save migration record to file
        migrations_dir = os.path.join(os.path.dirname(__file__), 'TestFiles')
        os.makedirs(migrations_dir, exist_ok=True)
        
        migration_file = os.path.join(migrations_dir, f'migration_{self.migration_id}.json')
        
        with open(migration_file, 'w') as f:
            json.dump(migration_record, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Migration record saved: {migration_file}")
    
    def rollback_migration(self) -> bool:
        """Rollback the semantic scoring migration (remove added fields)"""
        print(f"🔄 Rolling back semantic scoring migration...")
        
        try:
            if self.db_manager.use_sqlite:
                success = self._rollback_sqlite()
            else:
                success = self._rollback_postgresql()
            
            if success:
                print(f"✅ Migration rollback completed")
                return True
            else:
                print(f"❌ Rollback failed")
                return False
                
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            print(f"❌ Rollback error: {e}")
            return False
    
    def _rollback_sqlite(self) -> bool:
        """Rollback SQLite migration"""
        print("⚠️  SQLite doesn't support DROP COLUMN. Manual intervention needed.")
        print("   Consider recreating the table without semantic fields if rollback is critical.")
        return False
    
    def _rollback_postgresql(self) -> bool:
        """Rollback PostgreSQL migration"""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                
                try:
                    # Drop indexes first
                    cursor.execute("DROP INDEX IF EXISTS idx_candidates_semantic_score")
                    cursor.execute("DROP INDEX IF EXISTS idx_candidates_semantic_breakdown")
                    
                    # Drop columns
                    cursor.execute("ALTER TABLE candidates DROP COLUMN IF EXISTS semantic_score")
                    cursor.execute("ALTER TABLE candidates DROP COLUMN IF EXISTS semantic_breakdown")
                    cursor.execute("ALTER TABLE candidates DROP COLUMN IF EXISTS semantic_updated")
                    
                    conn.commit()
                    print("✅ PostgreSQL rollback completed")
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"PostgreSQL rollback failed: {e}")
                    return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        try:
            migration_needed = self.check_migration_needed()
            
            # Get current table structure
            if self.db_manager.use_sqlite:
                table_info = self._get_sqlite_table_info()
            else:
                table_info = self._get_postgresql_table_info()
            
            return {
                'migration_needed': migration_needed,
                'database_type': 'sqlite' if self.db_manager.use_sqlite else 'postgresql',
                'semantic_fields_present': not migration_needed,
                'table_structure': table_info,
                'migration_id': self.migration_id
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'migration_needed': 'unknown'
            }
    
    def _get_sqlite_table_info(self) -> List[Dict]:
        """Get SQLite table information"""
        import sqlite3
        
        sqlite_path = os.path.join(os.path.dirname(__file__), 'resume_screening.db')
        
        with sqlite3.connect(sqlite_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(candidates)")
            columns = cursor.fetchall()
            
            return [
                {
                    'column_name': col[1],
                    'data_type': col[2],
                    'nullable': not col[3],
                    'default_value': col[4]
                }
                for col in columns
            ]
    
    def _get_postgresql_table_info(self) -> List[Dict]:
        """Get PostgreSQL table information"""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'candidates'
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                
                return [
                    {
                        'column_name': col[0],
                        'data_type': col[1],
                        'nullable': col[2] == 'YES',
                        'default_value': col[3]
                    }
                    for col in columns
                ]

def main():
    """Main migration function"""
    print("🗄️  Semantic Scoring Database Migration")
    print("=" * 50)
    
    migration = SemanticScoringMigration()
    
    # Check current status
    status = migration.get_migration_status()
    print(f"📊 Current Status:")
    print(f"   Database Type: {status.get('database_type', 'unknown')}")
    print(f"   Migration Needed: {status.get('migration_needed', 'unknown')}")
    print(f"   Semantic Fields Present: {status.get('semantic_fields_present', 'unknown')}")
    
    if status.get('error'):
        print(f"❌ Status Check Error: {status['error']}")
        return
    
    if not status.get('migration_needed', True):
        print("\n✅ No migration needed - semantic fields already exist")
        return
    
    # Ask for confirmation
    print(f"\n⚠️  This will add semantic scoring fields to the candidates table:")
    print(f"   - semantic_score (FLOAT/REAL)")
    print(f"   - semantic_breakdown (JSONB/TEXT)")
    print(f"   - semantic_updated (TIMESTAMP)")
    
    confirm = input("\nProceed with migration? (y/N): ").strip().lower()
    
    if confirm in ['y', 'yes']:
        success = migration.run_migration()
        
        if success:
            print(f"\n🎉 Migration completed successfully!")
            print(f"   Candidates table now supports semantic scoring")
            print(f"   Existing data preserved")
        else:
            print(f"\n💥 Migration failed - check logs for details")
    else:
        print(f"\n❌ Migration cancelled by user")

if __name__ == "__main__":
    main()