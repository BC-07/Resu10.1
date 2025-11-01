#!/usr/bin/env python3
"""
Debug Candidate Loading Issue
Investigates the candidate 481 loading problem and Research Coordinator job issues
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import PDSAssessmentApp
from database import db_manager

def debug_candidate_loading():
    """Debug the candidate loading issue"""
    print("🔍 Debugging Candidate Loading Issue")
    print("🎯 Focus: Candidate 481 & Research Coordinator Position")
    print("=" * 60)
    
    # Initialize the Flask app
    app_instance = PDSAssessmentApp()
    app = app_instance.app
    
    print("✅ Flask app initialized")
    
    # Check if candidate 481 exists
    print("\n🧪 Testing Candidate 481 Existence")
    print("-" * 40)
    
    try:
        candidate = db_manager.get_candidate(481)
        if candidate:
            print(f"✅ Candidate 481 found:")
            print(f"   📝 Name: {candidate.get('name', 'Unknown')}")
            print(f"   📧 Email: {candidate.get('email', 'No email')}")
            print(f"   📄 Has PDS Data: {'Yes' if candidate.get('pds_extracted_data') else 'No'}")
            print(f"   🔢 Database ID: {candidate.get('id', 'Unknown')}")
            
            # Check PDS data structure
            if candidate.get('pds_extracted_data'):
                try:
                    pds_data = json.loads(candidate['pds_extracted_data'])
                    print(f"   📊 PDS Data Keys: {list(pds_data.keys())}")
                    
                    # Check educational background
                    edu_data = pds_data.get('educational_background', [])
                    print(f"   🎓 Education Records: {len(edu_data)}")
                    
                    # Check work experience
                    work_data = pds_data.get('work_experience', [])
                    print(f"   💼 Work Records: {len(work_data)}")
                    
                except Exception as e:
                    print(f"   ❌ PDS Data Parse Error: {e}")
        else:
            print("❌ Candidate 481 NOT found in database")
            
            # Let's check what candidates do exist
            print("\n🔍 Checking Available Candidates")
            print("-" * 40)
            
            try:
                # Get all candidates
                candidates = db_manager.get_all_candidates()
                if candidates:
                    print(f"📊 Total candidates in database: {len(candidates)}")
                    print("Recent candidates:")
                    for i, cand in enumerate(candidates[-5:]):  # Show last 5
                        print(f"   {cand.get('id', 'No ID')}: {cand.get('name', 'Unknown')}")
                else:
                    print("❌ No candidates found in database")
            except Exception as e:
                print(f"❌ Error getting candidates: {e}")
                
    except Exception as e:
        print(f"❌ Error checking candidate 481: {e}")
        import traceback
        traceback.print_exc()
    
    # Test the hybrid assessment API endpoint
    print("\n🧪 Testing Hybrid Assessment API")
    print("-" * 40)
    
    try:
        with app.app_context():
            # Try to get assessment for candidate 481
            assessment_result = app_instance.get_candidate_assessment(481)
            
            if hasattr(assessment_result, 'status_code'):
                print(f"📊 API Response Status: {assessment_result.status_code}")
                
                if assessment_result.status_code == 200:
                    print("✅ Assessment API working")
                elif assessment_result.status_code == 404:
                    print("❌ Assessment API returns 404 - Candidate not found")
                else:
                    print(f"⚠️ Assessment API returns {assessment_result.status_code}")
                    
                # Try to get JSON data
                try:
                    data = assessment_result.get_json()
                    if data:
                        print(f"📋 Response Data: {data.get('success', False)}")
                        if not data.get('success'):
                            print(f"❌ Error: {data.get('error', 'Unknown error')}")
                except:
                    print("❌ Could not parse response JSON")
            else:
                print("❌ Unexpected response format from assessment API")
                
    except Exception as e:
        print(f"❌ Error testing assessment API: {e}")
        import traceback
        traceback.print_exc()
    
    # Check job postings (Research Coordinator specifically)
    print("\n🧪 Testing Job Postings")
    print("-" * 40)
    
    try:
        with app.app_context():
            from lspu_job_api import get_job_postings
            job_postings = get_job_postings()
            
            if hasattr(job_postings, 'get_json'):
                job_data = job_postings.get_json()
                if job_data and 'job_postings' in job_data:
                    jobs = job_data['job_postings']
                    print(f"📊 Total job postings: {len(jobs)}")
                    
                    # Look for Research Coordinator
                    research_job = None
                    for job in jobs:
                        print(f"   📝 {job.get('id', 'No ID')}: {job.get('title', 'No title')}")
                        if 'research' in job.get('title', '').lower():
                            research_job = job
                    
                    if research_job:
                        print(f"✅ Found Research Coordinator job: ID {research_job.get('id')}")
                    else:
                        print("⚠️ No Research Coordinator job found")
                else:
                    print("❌ No job postings data")
            else:
                print("❌ Job postings API error")
                
    except Exception as e:
        print(f"❌ Error checking job postings: {e}")
    
    # Recommendations
    print(f"\n🎯 Debug Results & Recommendations")
    print("=" * 60)
    print("Based on the investigation:")
    print("1. Check if candidate 481 exists in database")
    print("2. Verify PDS data integrity for existing candidates") 
    print("3. Add better error handling to frontend")
    print("4. Implement fallback for missing candidates")
    print("5. Add proper 404 handling in candidate loading")

if __name__ == "__main__":
    debug_candidate_loading()