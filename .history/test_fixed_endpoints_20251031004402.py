#!/usr/bin/env python3
"""
Test assessment endpoints directly without external dependencies
"""

import requests
import json
import time

def test_endpoints():
    """Test the assessment endpoints"""
    
    base_url = "http://127.0.0.1:5000"
    candidate_id = 484
    
    try:
        print("=== Testing Endpoints After Fixes ===")
        
        # Wait for server to be ready
        print("Waiting for server...")
        time.sleep(3)
        
        # Test 1: Basic assessment endpoint
        print("\n1. Testing basic assessment...")
        try:
            response = requests.get(f"{base_url}/api/candidates/{candidate_id}/assessment", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                # Show full response structure for debugging
                print(f"   Full response (first 500 chars): {str(data)[:500]}...")
                
                # Check university assessment structure
                if 'university_assessment' in data:
                    ua = data['university_assessment']
                    if 'detailed_scores' in ua:
                        scores = ua['detailed_scores']
                        print(f"   ✅ Education: {scores.get('education', 'MISSING')}")
                        print(f"   ✅ Experience: {scores.get('experience', 'MISSING')}")
                        print(f"   ✅ Training: {scores.get('training', 'MISSING')}")
                    else:
                        print(f"   ❌ detailed_scores missing from university_assessment")
                else:
                    print(f"   ❌ university_assessment missing")
            else:
                print(f"   ❌ Error: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # Test 2: Assessment comparison endpoint  
        print("\n2. Testing assessment comparison...")
        try:
            response = requests.get(f"{base_url}/api/candidates/{candidate_id}/assessment/comparison", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    comp_data = data['data']
                    print(f"   Comparison data keys: {list(comp_data.keys())}")
                    
                    # Check traditional assessment structure
                    if 'traditional_assessment' in comp_data:
                        trad = comp_data['traditional_assessment']
                        print(f"   Traditional keys: {list(trad.keys())}")
                        print(f"   ✅ Traditional total: {trad.get('total_score', 'MISSING')}")
                        print(f"   ✅ Traditional education: {trad.get('education', 'MISSING')}")
                        print(f"   ✅ Traditional experience: {trad.get('experience', 'MISSING')}")
                    else:
                        print(f"   ❌ traditional_assessment missing")
                    
                    # Check differences structure  
                    if 'differences' in comp_data:
                        diff = comp_data['differences']
                        print(f"   ✅ Score difference: {diff.get('score_difference', 'MISSING')}")
                    elif 'improvement_metrics' in comp_data:
                        diff = comp_data['improvement_metrics']
                        print(f"   ✅ Score difference (from improvement_metrics): {diff.get('score_difference', 'MISSING')}")
                    else:
                        print(f"   ❌ differences missing")
                else:
                    print(f"   ❌ data field missing from response")
            else:
                print(f"   ❌ Error: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            
        print("\n=== Test Complete ===")
            
    except Exception as e:
        print(f"Overall Error: {e}")

if __name__ == "__main__":
    test_endpoints()