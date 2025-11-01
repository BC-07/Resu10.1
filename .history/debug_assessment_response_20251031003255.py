#!/usr/bin/env python3
"""
Debug script to test assessment endpoint response structure
"""

import requests
import json
import time

def test_assessment_response():
    """Test the assessment endpoint and print the response structure"""
    
    base_url = "http://127.0.0.1:5000"
    candidate_id = 484
    
    try:
        print("=== Testing Assessment Endpoint ===")
        
        # Test basic assessment endpoint
        assessment_url = f"{base_url}/api/candidates/{candidate_id}/assessment"
        print(f"Testing: {assessment_url}")
        
        response = requests.get(assessment_url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== ASSESSMENT RESPONSE STRUCTURE ===")
            print(json.dumps(data, indent=2))
            
            # Check specific fields that frontend expects
            print("\n=== FIELD ANALYSIS ===")
            
            if 'university_assessment' in data:
                ua = data['university_assessment']
                print(f"University Assessment keys: {list(ua.keys()) if isinstance(ua, dict) else type(ua)}")
                
                if isinstance(ua, dict):
                    if 'total_score' in ua:
                        print(f"✅ total_score found: {ua['total_score']}")
                    else:
                        print(f"❌ total_score missing. Available: {list(ua.keys())}")
                        
                    if 'detailed_scores' in ua:
                        ds = ua['detailed_scores']
                        print(f"✅ detailed_scores found: {ds}")
                        if isinstance(ds, dict):
                            print(f"   Education: {ds.get('education', 'MISSING')}")
                            print(f"   Experience: {ds.get('experience', 'MISSING')}")
                            print(f"   Training: {ds.get('training', 'MISSING')}")
                    else:
                        print(f"❌ detailed_scores missing")
            else:
                print("❌ university_assessment missing")
                
            if 'semantic_scores' in data:
                ss = data['semantic_scores']
                print(f"Semantic Scores: {ss}")
            else:
                print("❌ semantic_scores missing")
                
            if 'enhanced_assessment' in data:
                ea = data['enhanced_assessment']
                print(f"Enhanced Assessment: {ea}")
            else:
                print("❌ enhanced_assessment missing")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_assessment_response()