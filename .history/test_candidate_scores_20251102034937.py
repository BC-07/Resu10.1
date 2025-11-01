#!/usr/bin/env python3
"""
Test script to check candidate list scores after enhanced assessment integration
"""

import requests
import json

def test_candidate_scores():
    """Test the candidates API to see if enhanced scoring is working"""
    try:
        print("🧪 Testing candidate list scoring system...")
        
        # Make request to candidates API
        response = requests.get('http://127.0.0.1:5000/api/candidates')
        
        if response.status_code != 200:
            print(f"❌ API request failed with status: {response.status_code}")
            return
        
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ API returned error: {data.get('error', 'Unknown error')}")
            return
        
        print(f"✅ API Success: {data.get('success')}")
        print(f"📊 Total candidates: {data.get('total_candidates')}")
        print(f"🏢 Total jobs: {data.get('total_jobs')}")
        print(f"🔧 System: {data.get('system')}")
        
        candidates_by_job = data.get('candidates_by_job', {})
        
        print("\n📋 Jobs with candidates:")
        for job_id, job_data in candidates_by_job.items():
            candidate_count = len(job_data.get('candidates', []))
            if candidate_count > 0:
                job_title = job_data.get('position_title') or job_data.get('job_title', 'Unknown')
                print(f"  {job_id}: {candidate_count} candidates - {job_title}")
        
        # Check scores from first job with candidates
        print("\n🎯 Candidate Scores Analysis:")
        found_candidates = False
        
        for job_id, job_data in candidates_by_job.items():
            candidates = job_data.get('candidates', [])
            if candidates:
                found_candidates = True
                job_title = job_data.get('position_title') or job_data.get('job_title', 'Unknown')
                print(f"\n📝 Job: {job_title} ({job_id})")
                print("   Candidate Scores:")
                
                for i, candidate in enumerate(candidates[:5]):  # Show first 5 candidates
                    name = candidate.get('name', 'Unknown')
                    score = candidate.get('score', 0)
                    assessment_score = candidate.get('assessment_score', 0)
                    processing_type = candidate.get('processing_type', 'unknown')
                    
                    print(f"   {i+1}. {name[:30]:30} | Score: {score:6.1f} | Assessment: {assessment_score:6.1f} | Type: {processing_type}")
                
                # Check if scores are enhanced (should be different from simple university scores)
                enhanced_scores = [c.get('score', 0) for c in candidates]
                avg_score = sum(enhanced_scores) / len(enhanced_scores) if enhanced_scores else 0
                max_score = max(enhanced_scores) if enhanced_scores else 0
                min_score = min(enhanced_scores) if enhanced_scores else 0
                
                print(f"\n   📈 Score Statistics:")
                print(f"      Average: {avg_score:.1f}")
                print(f"      Range: {min_score:.1f} - {max_score:.1f}")
                
                # Check if scores look like enhanced scores (typically higher and more varied)
                if max_score > 85:
                    print("   ✅ Scores appear to be enhanced (high scores detected)")
                elif avg_score > 50:
                    print("   ⚠️  Scores may be partially enhanced")
                else:
                    print("   ❌ Scores appear to be basic university scores only")
                
                break  # Only check first job with candidates
        
        if not found_candidates:
            print("   ❌ No candidates found in any jobs")
        
        print("\n🏁 Test completed!")
        
    except Exception as e:
        print(f"❌ Error testing candidate scores: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_candidate_scores()