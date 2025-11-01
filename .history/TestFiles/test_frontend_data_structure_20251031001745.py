#!/usr/bin/env python3

import requests
import json

def test_frontend_data_structure():
    """Test what data structure is sent to frontend"""
    
    print("🔍 TESTING FRONTEND DATA STRUCTURE")
    print("=" * 40)
    
    # Use the actual candidate/job ID combination
    candidate_id = 484
    job_id = 1
    
    url = f'http://127.0.0.1:5000/api/candidates/{candidate_id}/assessment/{job_id}'
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'assessment' in result:
                assessment = result['assessment']
                
                print("📊 FRONTEND RECEIVES:")
                print("assessment = {")
                
                # University assessment structure
                university = assessment.get('university_assessment', {})
                print(f"  university_assessment: {{")
                print(f"    total_score: {university.get('total_score', 0)}")
                
                detailed = university.get('detailed_scores', {})
                print(f"    detailed_scores: {{")
                print(f"      education: {detailed.get('education', 0)}")
                print(f"      experience: {detailed.get('experience', 0)}")
                print(f"      training: {detailed.get('training', 0)}")
                print(f"      eligibility: {detailed.get('eligibility', 0)}")
                print(f"      performance: {detailed.get('performance', 0)}")
                print(f"      potential: {detailed.get('potential', 0)}")
                print(f"    }}")
                print(f"  }}")
                
                # Enhanced assessment structure
                enhanced = assessment.get('enhanced_assessment', {})
                print(f"  enhanced_assessment: {{")
                print(f"    semantic_score: {enhanced.get('semantic_score', 0)}")
                print(f"    traditional_score: {enhanced.get('traditional_score', 0)}")
                print(f"    recommended_score: {enhanced.get('recommended_score', 0)}")
                print(f"  }}")
                
                # Semantic analysis structure
                semantic = assessment.get('semantic_analysis', {})
                print(f"  semantic_analysis: {{")
                print(f"    overall_score: {semantic.get('overall_score', 0)}")
                print(f"    education_relevance: {semantic.get('education_relevance', 0)}")
                print(f"    experience_relevance: {semantic.get('experience_relevance', 0)}")
                print(f"    skills_relevance: {semantic.get('skills_relevance', 0)}")
                print(f"    training_relevance: {semantic.get('training_relevance', 0)}")
                print(f"  }}")
                
                print("}")
                
                # Test our fixes
                print(f"\n🔧 FRONTEND FIXES VERIFICATION:")
                
                # Test university score display
                univ_score = university.get('total_score', 0)
                if univ_score > 0:
                    print(f"   ✅ University score: {univ_score} (should display)")
                else:
                    print(f"   ❌ University score: {univ_score} (will show 0)")
                
                # Test breakdown display
                exp_score = detailed.get('experience', 0)
                train_score = detailed.get('training', 0)
                if exp_score > 0 or train_score > 0:
                    print(f"   ✅ Breakdown working: Experience={exp_score}, Training={train_score}")
                else:
                    print(f"   ❌ Breakdown showing 0s")
                
                # Test enhanced assessment
                trad_score = enhanced.get('traditional_score', 0)
                if trad_score > 0:
                    print(f"   ✅ Enhanced traditional: {trad_score} (should display)")
                else:
                    print(f"   ❌ Enhanced traditional: {trad_score} (will show 0)")
            
            else:
                print("❌ No assessment data")
        
        else:
            print(f"❌ API Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_data_structure()