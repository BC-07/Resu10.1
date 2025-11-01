#!/usr/bin/env python3
"""
Test the hybrid assessment endpoint directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import PDSAssessmentApp
import traceback

def test_assessment_endpoint():
    """Test the assessment endpoint that's causing 500 errors"""
    try:
        print("🧪 Testing Assessment Endpoint...")
        
        # Create app instance
        app_instance = PDSAssessmentApp()
        
        print("✅ App instance created successfully")
        
        # Test the specific method that's failing
        candidate_id = 469
        job_id = 2
        
        print(f"🔍 Testing get_candidate_assessment_for_job({candidate_id}, {job_id})")
        
        # Call the method directly
        with app_instance.app.app_context():
            result = app_instance.get_candidate_assessment_for_job(candidate_id, job_id)
            
        print("✅ Assessment completed successfully!")
        print(f"📊 Result keys: {result.keys() if isinstance(result, dict) else type(result)}")
        
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"  {key}: {len(value)} items")
                else:
                    print(f"  {key}: {type(value)} - {str(value)[:100]}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing assessment endpoint: {e}")
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    test_assessment_endpoint()