#!/usr/bin/env python3
"""
Debug script to test frontend job ID detection logic
"""

import json

def debug_frontend_job_detection():
    """Simulate the frontend job ID detection logic"""
    
    # Simulate candidate 484 data (based on our debug output)
    candidate = {
        'id': 484,
        'name': 'Bernadette Loeta Cruz',
        'job_id': 1,  # This should be detected!
        'position_id': None,
        'lspu_job_id': None,
        'target_job_id': None,
        'job_posting_id': None
    }
    
    print("🔍 Simulating frontend getJobIdForCandidate logic...")
    print(f"Candidate: {candidate['name']} (ID: {candidate['id']})")
    print(f"Available job_id: {candidate.get('job_id')}")
    
    # Simulate the frontend logic
    possible_job_ids = [
        candidate.get('job_id'),
        candidate.get('position_id'),
        candidate.get('lspu_job_id'),
        candidate.get('target_job_id'),
        candidate.get('job_posting_id')
    ]
    
    print(f"🎯 Possible job IDs: {possible_job_ids}")
    
    # Find first valid job ID (same logic as frontend)
    for jobId in possible_job_ids:
        print(f"🔍 Checking jobId: {jobId} (type: {type(jobId)})")
        
        # Frontend condition: jobId && jobId !== null && jobId !== undefined && jobId !== 0
        if jobId and jobId != None and jobId != 0:
            print(f"✅ Found valid job ID: {jobId}")
            return jobId
        else:
            print(f"❌ Invalid job ID: {jobId}")
    
    print("❌ No valid job ID found")
    return None

def test_different_data_types():
    """Test with different data types that might come from the database"""
    print("\n🧪 Testing different data types...")
    
    test_cases = [
        {'job_id': 1, 'name': 'integer 1'},
        {'job_id': '1', 'name': 'string "1"'},
        {'job_id': 0, 'name': 'integer 0'},
        {'job_id': '0', 'name': 'string "0"'},
        {'job_id': None, 'name': 'None'},
        {'job_id': '', 'name': 'empty string'},
    ]
    
    for test_case in test_cases:
        job_id = test_case['job_id']
        print(f"\nTest case: {test_case['name']}")
        print(f"Value: {job_id} (type: {type(job_id)})")
        
        # Frontend condition
        if job_id and job_id != None and job_id != 0:
            print(f"✅ Would be detected: {job_id}")
        else:
            print(f"❌ Would be rejected: {job_id}")

if __name__ == "__main__":
    result = debug_frontend_job_detection()
    test_different_data_types()
    
    # Save results
    debug_results = {
        'candidate_484_job_detection': result,
        'expected_result': 1,
        'issue_identified': result != 1
    }
    
    with open('candidate_484_job_debug.json', 'w') as f:
        json.dump(debug_results, f, indent=2)
    
    print(f"\n💾 Results saved to candidate_484_job_debug.json")