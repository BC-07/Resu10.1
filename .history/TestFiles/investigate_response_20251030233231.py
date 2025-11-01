#!/usr/bin/env python3
"""
Investigate the exact response structure from the assessment endpoint
"""

import sys
import os
# Add parent directory to path since we're in TestFiles subfolder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import PDSAssessmentApp
import json
import traceback

def investigate_response_structure():
    """Get the exact JSON response structure"""
    try:
        print("🔍 Investigating Assessment Response Structure...")
        
        # Create app instance
        app_instance = PDSAssessmentApp()
        
        # Get the response from the endpoint
        with app_instance.app.app_context():
            response = app_instance.get_candidate_assessment_for_job(469, 2)
            
            # Extract JSON data from Flask response
            if hasattr(response, 'get_json'):
                response_data = response.get_json()
            elif hasattr(response, 'json'):
                response_data = response.json
            else:
                # Try to get data from response
                response_data = response.data
                if isinstance(response_data, bytes):
                    response_data = json.loads(response_data.decode('utf-8'))
            
            print("📊 ACTUAL BACKEND RESPONSE STRUCTURE:")
            print("=" * 60)
            print(json.dumps(response_data, indent=2))
            
            print("\n🔑 TOP-LEVEL KEYS:")
            if isinstance(response_data, dict):
                for key in response_data.keys():
                    print(f"  - {key}")
                    
                # Check if assessment exists and its structure
                if 'assessment' in response_data:
                    assessment = response_data['assessment']
                    print(f"\n📋 ASSESSMENT KEYS:")
                    for key in assessment.keys():
                        print(f"  - {key}")
                        
                    # Check specific problematic fields
                    if 'university_assessment' in assessment:
                        print(f"\n✅ 'university_assessment' found in response")
                        print(f"   Value: {assessment['university_assessment']}")
                    else:
                        print(f"\n❌ 'university_assessment' NOT found in assessment")
                        print(f"   Available keys: {list(assessment.keys())}")
                        
                    if 'enhanced_assessment' in assessment:
                        print(f"\n✅ 'enhanced_assessment' found in response") 
                        print(f"   Value: {assessment['enhanced_assessment']}")
            
            return response_data
            
    except Exception as e:
        print(f"❌ Error investigating response: {e}")
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    investigate_response_structure()