#!/usr/bin/env python3
"""
Debug script to examine candidate data structure and identify issues
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from database import db_manager
    
    def examine_candidate_data(candidate_id):
        """Examine the data structure for a specific candidate"""
        print(f"🔍 Examining candidate {candidate_id} data structure...")
        
        # Get candidate data
        candidate = db_manager.get_candidate(candidate_id)
        if not candidate:
            print(f"❌ Candidate {candidate_id} not found")
            return
        
        print(f"✅ Found candidate: {candidate.get('name', 'Unknown')}")
        print(f"📋 Available fields ({len(candidate.keys())}): {list(candidate.keys())}")
        
        # Examine PDS data structure
        print("\n🔧 PDS Data Analysis:")
        pds_data = candidate.get('pds_extracted_data')
        if pds_data:
            print(f"PDS data type: {type(pds_data)}")
            if isinstance(pds_data, str):
                try:
                    parsed_pds = json.loads(pds_data)
                    print(f"✅ PDS string successfully parsed to dict with {len(parsed_pds)} keys")
                    print(f"PDS keys: {list(parsed_pds.keys())}")
                except Exception as e:
                    print(f"❌ Failed to parse PDS string: {e}")
            elif isinstance(pds_data, dict):
                print(f"✅ PDS is already a dict with {len(pds_data)} keys")
                print(f"PDS keys: {list(pds_data.keys())}")
            else:
                print(f"⚠️ PDS data is {type(pds_data)}: {pds_data}")
        else:
            print("❌ No PDS data found")
        
        # Examine job-related fields
        print("\n🎯 Job Assignment Analysis:")
        job_fields = {
            'job_id': candidate.get('job_id'),
            'position_id': candidate.get('position_id'), 
            'lspu_job_id': candidate.get('lspu_job_id'),
            'target_job_id': candidate.get('target_job_id'),
            'job_posting_id': candidate.get('job_posting_id'),
            'job_assignment_id': candidate.get('job_assignment_id'),
            'application_job_id': candidate.get('application_job_id'),
            'assigned_position': candidate.get('assigned_position'),
            'job_category_id': candidate.get('job_category_id')
        }
        
        print("Job-related fields:")
        for field, value in job_fields.items():
            if value is not None:
                print(f"  ✅ {field}: {value} ({type(value)})")
            else:
                print(f"  ❌ {field}: None")
        
        # Check for any field that might contain job references
        print("\n🔍 Scanning all fields for potential job references:")
        for key, value in candidate.items():
            if value is not None and str(value).isdigit() and 'job' in key.lower():
                print(f"  🎯 Potential job field {key}: {value}")
        
        # Check candidate_job_assignments table
        print("\n📋 Checking candidate_job_assignments table:")
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute("""
                SELECT cja.*, lp.title as job_title 
                FROM candidate_job_assignments cja
                LEFT JOIN lspu_job_postings lp ON cja.job_id = lp.id
                WHERE cja.candidate_id = ?
            """, (candidate_id,))
            assignments = cursor.fetchall()
            
            if assignments:
                print(f"✅ Found {len(assignments)} job assignment(s):")
                for assignment in assignments:
                    print(f"  Job ID: {assignment[1]}, Title: {assignment[-1]}, Assigned: {assignment[3]}")
            else:
                print("❌ No job assignments found in candidate_job_assignments table")
                
        except Exception as e:
            print(f"❌ Error checking assignments: {e}")
        
        # Check applications table
        print("\n📝 Checking applications table:")
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute("""
                SELECT a.*, lp.title as job_title 
                FROM applications a
                LEFT JOIN lspu_job_postings lp ON a.job_posting_id = lp.id
                WHERE a.candidate_id = ?
            """, (candidate_id,))
            applications = cursor.fetchall()
            
            if applications:
                print(f"✅ Found {len(applications)} application(s):")
                for app in applications:
                    print(f"  Job ID: {app[2]}, Title: {app[-1]}, Applied: {app[4]}")
            else:
                print("❌ No applications found")
                
        except Exception as e:
            print(f"❌ Error checking applications: {e}")
        
        return candidate
    
    def test_pds_parsing_fix(candidate_id):
        """Test the PDS parsing fix"""
        print(f"\n🔧 Testing PDS parsing fix for candidate {candidate_id}...")
        
        candidate = db_manager.get_candidate(candidate_id)
        if not candidate:
            return
        
        pds_data = candidate.get('pds_extracted_data')
        
        # Test current parsing logic (from backend)
        try:
            if isinstance(pds_data, str):
                parsed_pds = json.loads(pds_data)
                print("✅ Current logic: PDS string parsed successfully")
            elif isinstance(pds_data, dict):
                parsed_pds = pds_data  # Use directly
                print("✅ Fixed logic: PDS dict used directly")
            else:
                print(f"⚠️ PDS data is {type(pds_data)}, using fallback")
                parsed_pds = {
                    'educational_background': {'course': 'Not specified', 'school_name': 'Not specified'},
                    'work_experience': [],
                    'learning_development': [],
                    'civil_service_eligibility': []
                }
            
            print(f"📊 Parsed PDS structure: {list(parsed_pds.keys())}")
            return parsed_pds
            
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            return None
    
    if __name__ == "__main__":
        candidate_id = 484  # The candidate showing issues
        candidate_data = examine_candidate_data(candidate_id)
        
        if candidate_data:
            pds_result = test_pds_parsing_fix(candidate_id)
            
            # Save debug info to file
            debug_info = {
                'candidate_id': candidate_id,
                'candidate_fields': list(candidate_data.keys()),
                'pds_data_type': str(type(candidate_data.get('pds_extracted_data'))),
                'job_fields': {k: v for k, v in candidate_data.items() if 'job' in k.lower() and v is not None},
                'parsing_result': 'success' if pds_result else 'failed'
            }
            
            with open('testfiles/candidate_484_debug.json', 'w') as f:
                json.dump(debug_info, f, indent=2, default=str)
            
            print(f"\n💾 Debug info saved to testfiles/candidate_484_debug.json")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the ResuAI directory")
except Exception as e:
    print(f"❌ Error: {e}")