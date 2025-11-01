#!/usr/bin/env python3

"""
Test Research Coordinator Position Loading
Tests the API endpoints to understand the candidate loading issue
"""

import requests
import json

def test_research_coordinator_candidates():
    """Test Research Coordinator candidates loading"""
    
    base_url = "http://localhost:5000"
    
    print("🎯 Testing Research Coordinator Candidates Loading")
    print("=" * 50)
    
    # Test 1: Get all candidates
    print("\n📊 Test 1: Get All Candidates")
    try:
        response = requests.get(f"{base_url}/api/candidates")
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('candidates', [])
            print(f"✅ Found {len(candidates)} candidates")
            for candidate in candidates:
                print(f"  - ID {candidate['id']}: {candidate['name']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Try to get candidate 481 (the problematic one)
    print("\n🔍 Test 2: Get Candidate 481 (Expected to fail)")
    try:
        response = requests.get(f"{base_url}/api/candidates/481")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Candidate 481 found: {data}")
        else:
            print(f"❌ Expected error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Get Research Coordinator job details
    print("\n🎯 Test 3: Get Research Coordinator Job")
    try:
        response = requests.get(f"{base_url}/api/job-postings")
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            print(f"✅ Found {len(jobs)} jobs")
            
            # Look for Research Coordinator
            research_job = None
            for job in jobs:
                if 'Research Coordinator' in job.get('position_title', ''):
                    research_job = job
                    print(f"✅ Found Research Coordinator: Job ID {job['id']}")
                    break
            
            if not research_job:
                print("❌ Research Coordinator job not found")
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Try each existing candidate with assessment
    print("\n🧪 Test 4: Test Assessment for Each Candidate")
    candidate_ids = [1, 2, 3, 4]  # Known existing candidates
    
    for candidate_id in candidate_ids:
        try:
            response = requests.get(f"{base_url}/api/candidates/{candidate_id}/assessment")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    assessment = data.get('assessment', {})
                    overall_total = assessment.get('overall_total', 0)
                    print(f"✅ Candidate {candidate_id} assessment: {overall_total} points")
                else:
                    print(f"⚠️ Candidate {candidate_id} assessment failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Candidate {candidate_id} assessment error: {response.status_code}")
        except Exception as e:
            print(f"❌ Candidate {candidate_id} exception: {e}")
    
    print("\n✅ Research Coordinator Test Complete!")
    print("\n💡 Recommended fixes:")
    print("1. Update frontend to use existing candidate IDs (1, 2, 3, 4)")
    print("2. Add proper error handling for missing candidates")
    print("3. Ensure job-candidate associations are properly set up")

if __name__ == "__main__":
    test_research_coordinator_candidates()