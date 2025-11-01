#!/usr/bin/env python3

import requests
import json

def quick_regression_test():
    """Quick test to see if our fixes are still working"""
    
    print("🔍 CHECKING FOR REGRESSION")
    print("=" * 30)
    
    # Test the API that was working before
    url = 'http://127.0.0.1:5000/api/candidates/463/assessment/8'
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API responded successfully")
            
            if 'assessment' in result:
                assessment = result['assessment']
                
                # Check the scores that were working before
                enhanced = assessment.get('enhanced_assessment', {})
                university = assessment.get('university_assessment', {})
                semantic = assessment.get('semantic_analysis', {})
                
                print("\n📊 CURRENT SCORES:")
                trad_score = enhanced.get('traditional_score', 0)
                univ_score = university.get('total_score', 0)
                sem_score = semantic.get('overall_score', 0)
                
                print(f"   Traditional Score: {trad_score}")
                print(f"   University Score: {univ_score}")
                print(f"   Semantic Score: {sem_score}")
                
                # Check detailed breakdown
                detailed = university.get('detailed_scores', {})
                edu_score = detailed.get('education', 0)
                exp_score = detailed.get('experience', 0)
                train_score = detailed.get('training', 0)
                
                print(f"\n📋 BREAKDOWN:")
                print(f"   Education: {edu_score}")
                print(f"   Experience: {exp_score}")
                print(f"   Training: {train_score}")
                
                # Determine what's wrong
                print(f"\n🎯 REGRESSION ANALYSIS:")
                
                if trad_score == 0 and univ_score == 0:
                    print("   ❌ MAJOR REGRESSION: All traditional scores back to 0")
                    print("   This suggests education data issue or assessment engine problem")
                elif trad_score > 0:
                    print(f"   ✅ Traditional assessment still working: {trad_score}")
                
                if sem_score == 0:
                    print("   ❌ Semantic analysis still broken (expected)")
                else:
                    print(f"   ✅ Semantic analysis fixed: {sem_score}")
                
                # Overall status
                if trad_score > 0:
                    print(f"\n✅ ASSESSMENT SYSTEM: Working (Traditional: {trad_score})")
                else:
                    print(f"\n❌ ASSESSMENT SYSTEM: Broken - all scores 0")
                    
            else:
                print("❌ No assessment data in API response")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    quick_regression_test()