#!/usr/bin/env python3

import requests

def test_correct_job_id():
    """Test with the actual job ID the candidate has"""
    
    print("🔍 TESTING WITH CORRECT JOB ID")
    print("=" * 35)
    
    # Use the CORRECT job ID that the candidate actually has
    candidate_id = 484  
    job_id = 1  # The actual job_id from database
    
    url = f'http://127.0.0.1:5000/api/candidates/{candidate_id}/assessment/{job_id}'
    print(f"📡 URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response: SUCCESS")
            
            if 'assessment' in result:
                assessment = result['assessment']
                
                # Check all score components
                enhanced = assessment.get('enhanced_assessment', {})
                university = assessment.get('university_assessment', {})
                semantic = assessment.get('semantic_analysis', {})
                
                print(f"\n📊 SCORES WITH CORRECT JOB ID:")
                trad_score = enhanced.get('traditional_score', 0)
                sem_score = enhanced.get('semantic_score', 0)
                univ_score = university.get('total_score', 0)
                sem_overall = semantic.get('overall_score', 0)
                
                print(f"   Traditional Score: {trad_score}")
                print(f"   Semantic Score: {sem_score}")
                print(f"   University Score: {univ_score}")
                print(f"   Semantic Overall: {sem_overall}%")
                
                # Check breakdown
                detailed = university.get('detailed_scores', {})
                print(f"\n📋 BREAKDOWN:")
                print(f"   Education: {detailed.get('education', 0)}")
                print(f"   Experience: {detailed.get('experience', 0)}")
                print(f"   Training: {detailed.get('training', 0)}")
                
                # Determine if the problem is job-specific
                print(f"\n🎯 DIAGNOSIS:")
                if trad_score > 0:
                    print(f"   ✅ Assessment working with correct job ID: {trad_score}")
                    print(f"   🔧 Frontend issue: May be using wrong job ID")
                elif trad_score == 0:
                    print(f"   ❌ Still 0 with correct job ID")
                    print(f"   🔧 Assessment engine issue: Job/candidate mismatch")
                
            else:
                print("❌ No assessment data in response")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_correct_job_id()