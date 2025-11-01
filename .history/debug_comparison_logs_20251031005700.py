#!/usr/bin/env python3
"""
Debug server logs during endpoint calls
"""

import requests
import json
import time

def test_comparison_with_logs():
    """Test the assessment comparison endpoint and watch server logs"""
    
    base_url = "http://127.0.0.1:5000"
    candidate_id = 484
    
    try:
        print("=== Testing Assessment Comparison with Logs ===")
        
        # Make the comparison call
        comparison_url = f"{base_url}/api/candidates/{candidate_id}/assessment/comparison"
        print(f"Calling: {comparison_url}")
        
        response = requests.get(comparison_url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', 'MISSING')}")
            if 'data' in data:
                comp_data = data['data'] 
                print(f"Data keys: {list(comp_data.keys())}")
                
                if 'traditional_assessment' in comp_data:
                    trad = comp_data['traditional_assessment']
                    print(f"Traditional assessment: {json.dumps(trad, indent=2)}")
            else:
                print("No 'data' field")
                print(f"Full response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_comparison_with_logs()