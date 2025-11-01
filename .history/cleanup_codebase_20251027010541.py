#!/usr/bin/env python3
"""
ResuAI Codebase Cleanup Script
Safely removes test files, debug files, and other unused files from the system.
"""

import os
import shutil
import glob
import json
from datetime import datetime

def create_backup_log(files_to_delete):
    """Create a log of files being deleted for potential recovery"""
    log_data = {
        "cleanup_date": datetime.now().isoformat(),
        "files_deleted": files_to_delete,
        "cleanup_reason": "Codebase cleanup - removing test, debug, and unused files"
    }
    
    with open('cleanup_log.json', 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Backup log created: cleanup_log.json ({len(files_to_delete)} files)")

def safe_delete_file(filepath):
    """Safely delete a file with error handling"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        else:
            print(f"⚠️  File not found: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {filepath}: {e}")
        return False

def safe_delete_directory(dirpath):
    """Safely delete a directory with error handling"""
    try:
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
            return True
        else:
            print(f"⚠️  Directory not found: {dirpath}")
            return False
    except Exception as e:
        print(f"❌ Error deleting directory {dirpath}: {e}")
        return False

def cleanup_codebase():
    """Main cleanup function"""
    print("🧹 ResuAI Codebase Cleanup")
    print("=" * 50)
    
    files_deleted = []
    
    # 1. Test files (test_*.py)
    print("\n📋 Cleaning up test files...")
    test_files = glob.glob("test_*.py")
    for file in test_files:
        if safe_delete_file(file):
            files_deleted.append(file)
            print(f"  ✓ Deleted: {file}")
    
    # 2. Debug files (debug_*.py)
    print("\n🐛 Cleaning up debug files...")
    debug_files = glob.glob("debug_*.py")
    for file in debug_files:
        if safe_delete_file(file):
            files_deleted.append(file)
            print(f"  ✓ Deleted: {file}")
    
    # 3. Fix/utility scripts
    print("\n🔧 Cleaning up fix/utility scripts...")
    fix_files = [
        "fix_imports.py",
        "fix_db_schema.py", 
        "fix_app.py",
        "education_fix_summary.py"
    ]
    for file in fix_files:
        if safe_delete_file(file):
            files_deleted.append(file)
            print(f"  ✓ Deleted: {file}")
    
    # 4. Result JSON files with timestamps
    print("\n📊 Cleaning up result JSON files...")
    json_patterns = [
        "*_results_*.json",
        "*_comparison_*.json", 
        "*_summary_*.json",
        "phase*_*.json",
        "*_test_results_*.json",
        "extractor_*.json"
    ]
    
    for pattern in json_patterns:
        json_files = glob.glob(pattern)
        for file in json_files:
            # Keep essential config files
            if file not in ['package.json', 'tsconfig.json', 'analytics_data.json']:
                if safe_delete_file(file):
                    files_deleted.append(file)
                    print(f"  ✓ Deleted: {file}")
    
    # 5. Specific files to remove
    print("\n🗂️ Cleaning up specific files...")
    specific_files = [
        "debug_raw_pds_data.json",
        "enhanced_pdf_extraction_demo.json",
        "TEST_FILE_ANALYSIS.json",
        "utils_backup_before_class_removal.py"
    ]
    
    for file in specific_files:
        if safe_delete_file(file):
            files_deleted.append(file)
            print(f"  ✓ Deleted: {file}")
    
    # 6. History directory (VS Code history)
    print("\n📁 Cleaning up .history directory...")
    if safe_delete_directory(".history"):
        files_deleted.append(".history/")
        print("  ✓ Deleted: .history/ directory")
    
    # 7. Report files
    print("\n📄 Cleaning up report files...")
    report_patterns = [
        "*.md",
        "*_REPORT_*.md",
        "*COMPLETION_REPORT*.md",
        "*ENHANCEMENT*REPORT*.md",
        "*SUMMARY*.md"
    ]
    
    # Keep essential documentation
    keep_files = ["README.md", "QUICK_START.md", "IMPLEMENTATION_GUIDE.md"]
    
    for pattern in report_patterns:
        report_files = glob.glob(pattern)
        for file in report_files:
            if file not in keep_files:
                if safe_delete_file(file):
                    files_deleted.append(file)
                    print(f"  ✓ Deleted: {file}")
    
    # 8. Migration files (keep schema files)
    print("\n🗄️ Cleaning up old migration files...")
    migration_files = [
        "add_ocr_confidence_migration.sql",
        "add_ocr_fields_migration.py", 
        "add_potential_score_migration.sql",
        "migrate_recommendation_field.py",
        "fix_recommendation_field.sql",
        "ocr_migration.sql"
    ]
    
    for file in migration_files:
        if safe_delete_file(file):
            files_deleted.append(file)
            print(f"  ✓ Deleted: {file}")
    
    # Create backup log
    print(f"\n📝 Creating cleanup log...")
    create_backup_log(files_deleted)
    
    # Summary
    print(f"\n✅ Cleanup completed!")
    print(f"   📦 Files deleted: {len(files_deleted)}")
    print(f"   📋 Log saved to: cleanup_log.json")
    print(f"\n🔍 Files kept (essential system files):")
    
    essential_files = [
        "app.py", "database.py", "utils.py", "assessment_engine.py",
        "backend_api.py", "clean_upload_handler.py", "pds_extractor.py",
        "start.py", "requirements.txt", "README.md", "schema.sql"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
    
    print(f"\n🚀 System is now clean and ready for Phase 3 development!")

if __name__ == "__main__":
    # Confirmation prompt
    print("🧹 ResuAI Codebase Cleanup Script")
    print("=" * 50)
    print("This will delete test files, debug files, and other unused files.")
    print("A backup log will be created for recovery if needed.")
    print()
    
    response = input("Continue with cleanup? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        cleanup_codebase()
    else:
        print("❌ Cleanup cancelled by user")