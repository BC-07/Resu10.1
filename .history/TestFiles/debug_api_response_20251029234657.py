#!/usr/bin/env python3
"""
Test script to examine the exact API response for candidate 484
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from database import DatabaseManager
    db_manager = DatabaseManager()
    
    def test_candidate_api_response(candidate_id):
        """Test what the API actually returns for a candidate"""
        print(f"🔍 Testing API response for candidate {candidate_id}...")
        
        # Get candidate data (same as API would)
        candidate = db_manager.get_candidate(candidate_id)
        if not candidate:
            print(f"❌ Candidate {candidate_id} not found")
            return
        
        print(f"✅ Raw database candidate data:")
        print(f"  - job_id: {candidate.get('job_id')} (type: {type(candidate.get('job_id'))})")
        print(f"  - name: {candidate.get('name')}")
        print(f"  - total fields: {len(candidate.keys())}")
        
        # Check what fields have 'job' in the name and their values
        job_related_fields = {}
        for key, value in candidate.items():
            if 'job' in key.lower() and value is not None:
                job_related_fields[key] = value
        
        print(f"🎯 Job-related fields in database: {job_related_fields}")
        
        # Simulate the candidates API endpoint response formatting
        # This is typically what gets sent to the frontend
        api_response_candidate = {
            'id': candidate.get('id'),
            'name': candidate.get('name'),
            'email': candidate.get('email'),
            'phone': candidate.get('phone'),
            'category': candidate.get('category'),
            'skills': candidate.get('skills'),
            'education': candidate.get('education'),
            'experience': candidate.get('experience'),
            'status': candidate.get('status'),
            'score': candidate.get('score'),
            'job_id': candidate.get('job_id'),  # This should be included!
            'notes': candidate.get('notes'),
            'created_at': candidate.get('created_at'),
            'updated_at': candidate.get('updated_at'),
            'filename': candidate.get('filename'),
            'latest_total_score': candidate.get('latest_total_score'),
            'latest_percentage_score': candidate.get('latest_percentage_score'),
            'latest_recommendation': candidate.get('latest_recommendation')
        }
        
        print(f"\n📡 Simulated API response:")
        print(f"  - job_id: {api_response_candidate.get('job_id')} (type: {type(api_response_candidate.get('job_id'))})")
        
        # Test the frontend logic with this data
        print(f"\n🧪 Testing frontend getJobIdForCandidate with API data:")
        possible_job_ids = [
            api_response_candidate.get('job_id'),
            api_response_candidate.get('position_id'),
            api_response_candidate.get('lspu_job_id'),
            api_response_candidate.get('target_job_id'),
            api_response_candidate.get('job_posting_id')
        ]
        
        print(f"🎯 Possible job IDs from API response: {possible_job_ids}")
        
        for jobId in possible_job_ids:
            if jobId and jobId != None and jobId != 0:
                print(f"✅ Frontend SHOULD detect job ID: {jobId}")
                break
        else:
            print(f"❌ Frontend WOULD NOT detect any job ID")
            print(f"Available API fields: {list(api_response_candidate.keys())}")
        
        # Save the API response for analysis
        with open('candidate_484_api_response.json', 'w') as f:
            json.dump(api_response_candidate, f, indent=2, default=str)
        
        return api_response_candidate
    
    if __name__ == "__main__":
        result = test_candidate_api_response(484)
        print(f"\n💾 API response saved to candidate_484_api_response.json")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")