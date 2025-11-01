#!/usr/bin/env python3
"""
Test the hybrid assessment endpoint response structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import PDSAssessmentApp
import traceback
import json

def test_assessment_response():
    """Test the assessment endpoint response structure"""
    try:
        print("🧪 Testing Assessment Response Structure...")
        
        # Create app instance
        app_instance = PDSAssessmentApp()
        
        print("✅ App instance created successfully")
        
        # Test the specific method that's failing
        candidate_id = 469
        job_id = 2
        
        print(f"🔍 Testing get_candidate_assessment_for_job({candidate_id}, {job_id})")
        
        # Call the method directly
        with app_instance.app.app_context():
            response = app_instance.get_candidate_assessment_for_job(candidate_id, job_id)
            
        print("✅ Assessment completed successfully!")
        
        # Parse the response
        if hasattr(response, 'data'):
            response_data = json.loads(response.data.decode('utf-8'))
            print(f"📊 Response structure:")
            print(f"  - success: {response_data.get('success')}")
            print(f"  - assessment keys: {list(response_data.get('assessment', {}).keys())}")
            
            assessment = response_data.get('assessment', {})
            
            # Check enhanced assessment
            enhanced = assessment.get('enhanced_assessment', {})
            print(f"  - enhanced_assessment:")
            print(f"    * semantic_score: {enhanced.get('semantic_score')}")
            print(f"    * traditional_score: {enhanced.get('traditional_score')}")
            print(f"    * recommended_score: {enhanced.get('recommended_score')}")
            print(f"    * assessment_method: {enhanced.get('assessment_method')}")
            
            # Check university assessment
            university = assessment.get('university_assessment', {})
            print(f"  - university_assessment:")
            print(f"    * total_score: {university.get('total_score')}")
            detailed = university.get('detailed_scores', {})
            print(f"    * detailed_scores: education={detailed.get('education')}, experience={detailed.get('experience')}")
            
            # Check semantic analysis  
            semantic = assessment.get('semantic_analysis', {})
            print(f"  - semantic_analysis:")
            print(f"    * overall_score: {semantic.get('overall_score')}")
            print(f"    * education_relevance: {semantic.get('education_relevance')}")
            
            # Check hybrid score
            hybrid_score = assessment.get('hybrid_score')
            print(f"  - hybrid_score: {hybrid_score}")
            
            # Analyze the issue
            print(f"\n🔍 Analysis:")
            if enhanced.get('semantic_score', 0) > 0:
                print(f"  ✅ Semantic scoring is working: {enhanced.get('semantic_score')}")
            else:
                print(f"  ❌ Semantic scoring returned 0 or None")
                
            if enhanced.get('traditional_score', 0) > 0:
                print(f"  ✅ Traditional scoring is working: {enhanced.get('traditional_score')}")
            else:
                print(f"  ❌ Traditional scoring returned 0: {enhanced.get('traditional_score')}")
                
            if hybrid_score and hybrid_score > 0:
                print(f"  ✅ Hybrid score is calculated: {hybrid_score}")
            else:
                print(f"  ❌ Hybrid score is 0 or missing: {hybrid_score}")
                
        return response
        
    except Exception as e:
        print(f"❌ Error testing assessment response: {e}")
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    test_assessment_response()