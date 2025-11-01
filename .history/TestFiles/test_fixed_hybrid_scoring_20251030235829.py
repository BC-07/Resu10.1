#!/usr/bin/env python3

import requests
import json

def test_fixed_hybrid_scoring():
    """Test hybrid scoring with candidates that now have education data"""
    
    print("🧪 TESTING FIXED HYBRID SCORING")
    print("=" * 40)
    
    # Test with first candidate
    candidate_id = 463
    job_id = 8
    url = f'http://127.0.0.1:5000/api/candidates/{candidate_id}/assessment/{job_id}'
    
    print(f"📡 Testing: candidate {candidate_id}, job {job_id}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            print('✅ API Response successful!')
            print(f'Success: {result.get("success", False)}')
            
            if 'assessment' in result:
                assessment = result['assessment']
                
                # Check enhanced assessment
                enhanced = assessment.get('enhanced_assessment', {})
                print(f'\n📊 ENHANCED ASSESSMENT:')
                semantic_score = enhanced.get('semantic_score', 0)
                traditional_score = enhanced.get('traditional_score', 0)
                recommended_score = enhanced.get('recommended_score', 0)
                
                print(f'   Semantic Score: {semantic_score}')
                print(f'   Traditional Score: {traditional_score}')
                print(f'   Recommended Score: {recommended_score}')
                
                # Check university assessment
                university = assessment.get('university_assessment', {})
                print(f'\n🎓 UNIVERSITY ASSESSMENT:')
                total_score = university.get('total_score', 0)
                print(f'   Total Score: {total_score}')
                
                detailed = university.get('detailed_scores', {})
                print(f'   Education: {detailed.get("education", 0)}')
                print(f'   Experience: {detailed.get("experience", 0)}')
                print(f'   Training: {detailed.get("training", 0)}')
                print(f'   Eligibility: {detailed.get("eligibility", 0)}')
                print(f'   Performance: {detailed.get("performance", 0)}')
                print(f'   Potential: {detailed.get("potential", 0)}')
                
                # Check semantic analysis
                semantic = assessment.get('semantic_analysis', {})
                print(f'\n🔍 SEMANTIC ANALYSIS:')
                overall_score = semantic.get('overall_score', 0)
                skills_relevance = semantic.get('skills_relevance', 0)
                training_relevance = semantic.get('training_relevance', 0)
                education_relevance = semantic.get('education_relevance', 0)
                experience_relevance = semantic.get('experience_relevance', 0)
                
                print(f'   Overall Score: {overall_score}%')
                print(f'   Education Relevance: {education_relevance}%')
                print(f'   Experience Relevance: {experience_relevance}%')
                print(f'   Skills Relevance: {skills_relevance}%')
                print(f'   Training Relevance: {training_relevance}%')
                
                # Verify fix results
                print(f'\n🎯 FIX VERIFICATION:')
                
                if traditional_score > 0:
                    print(f'   ✅ Traditional assessment working: {traditional_score}')
                else:
                    print(f'   ❌ Traditional assessment still 0')
                
                if semantic_score > 0:
                    print(f'   ✅ Semantic assessment working: {semantic_score}')
                else:
                    print(f'   ❌ Semantic assessment still 0')
                
                if overall_score > 0:
                    print(f'   ✅ Semantic analysis working: {overall_score}%')
                else:
                    print(f'   ❌ Semantic analysis still 0')
                
                if skills_relevance > 0:
                    print(f'   ✅ Skills relevance fix working: {skills_relevance}%')
                else:
                    print(f'   ❌ Skills relevance still 0')
                
                # Calculate score difference
                if traditional_score > 0 and semantic_score > 0:
                    score_diff = abs(traditional_score - semantic_score)
                    print(f'   ✅ Score difference: {score_diff:.1f} points')
                
                # Overall status
                if (traditional_score > 0 and semantic_score > 0 and 
                    overall_score > 0 and skills_relevance > 0):
                    print(f'\n🎉 ALL FIXES SUCCESSFUL!')
                    print(f'   - University assessment scores working')
                    print(f'   - Enhanced assessment scores working')
                    print(f'   - Semantic analysis working')
                    print(f'   - Skills relevance showing training data')
                    print(f'   - Score differences calculating')
                else:
                    print(f'\n⚠️  Some issues remain:')
                    if traditional_score == 0:
                        print(f'     - Traditional assessment still 0')
                    if semantic_score == 0:
                        print(f'     - Semantic assessment still 0')
                    if overall_score == 0:
                        print(f'     - Semantic analysis still 0')
                    if skills_relevance == 0:
                        print(f'     - Skills relevance still 0')
            
            else:
                print('❌ No assessment data in response')
        
        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'Response: {response.text[:500]}')
    
    except Exception as e:
        print(f'❌ Request failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fixed_hybrid_scoring()