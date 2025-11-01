#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database
import json

def debug_assessment_scores():
    """
    Debug why all assessment scores are showing 0
    Check:
    1. Do we have candidate data?
    2. Is assessment calculation working?
    3. Are semantic scores being calculated?
    """
    
    print("🔍 DEBUGGING ASSESSMENT SCORES SHOWING 0")
    print("=" * 50)
    
    try:
        # Initialize database
        db = Database()
        
        # Check candidates
        print("📊 CHECKING CANDIDATES:")
        candidates = db.get_all_candidates()
        print(f"   Total candidates: {len(candidates)}")
        
        if not candidates:
            print("   ❌ No candidates found - need to upload PDS first")
            return
        
        # Get first candidate for testing
        candidate = candidates[0]
        candidate_id = candidate['id']
        full_name = candidate.get('full_name', 'Unknown')
        
        print(f"   Testing with: ID {candidate_id} - {full_name}")
        
        # Check candidate data completeness
        print(f"\n📋 CHECKING CANDIDATE DATA:")
        required_fields = ['education', 'work_experience', 'learning_development']
        
        for field in required_fields:
            value = candidate.get(field)
            if value and value.strip():
                print(f"   ✅ {field}: Has data ({len(value)} chars)")
            else:
                print(f"   ❌ {field}: Empty or missing")
        
        # Check if job posting exists
        print(f"\n📝 CHECKING JOB POSTINGS:")
        jobs = db.get_all_jobs()
        print(f"   Total jobs: {len(jobs)}")
        
        if not jobs:
            print("   ❌ No job postings found")
            return
        
        job = jobs[0]
        job_id = job['id']
        print(f"   Using job: ID {job_id} - {job.get('title', 'Unknown')}")
        
        # Test assessment calculation manually
        print(f"\n🧮 TESTING ASSESSMENT CALCULATION:")
        
        # Import assessment modules
        from assessment_engine import AssessmentEngine
        from semantic_engine import SemanticEngine
        
        # Initialize engines
        assessment_engine = AssessmentEngine()
        semantic_engine = SemanticEngine()
        
        print("   ✅ Engines initialized")
        
        # Test university assessment
        print(f"\n🎓 TESTING UNIVERSITY ASSESSMENT:")
        try:
            university_result = assessment_engine.calculate_university_assessment(
                candidate['education'],
                candidate['work_experience'],
                job_id
            )
            print(f"   University assessment result: {university_result}")
            
            if isinstance(university_result, dict):
                total_score = university_result.get('total_score', 0)
                print(f"   Total score: {total_score}")
                
                if total_score == 0:
                    print("   ❌ University assessment returning 0")
                    # Check detailed scores
                    detailed = university_result.get('detailed_scores', {})
                    print(f"   Detailed scores: {detailed}")
                else:
                    print("   ✅ University assessment working")
            
        except Exception as e:
            print(f"   ❌ University assessment error: {e}")
        
        # Test semantic assessment
        print(f"\n🔍 TESTING SEMANTIC ASSESSMENT:")
        try:
            semantic_result = semantic_engine.calculate_detailed_semantic_score(
                candidate, job_id
            )
            print(f"   Semantic result type: {type(semantic_result)}")
            
            if isinstance(semantic_result, dict):
                overall_score = semantic_result.get('overall_score', 0)
                print(f"   Overall score: {overall_score}")
                
                # Check component scores
                components = ['education_relevance', 'experience_relevance', 'training_relevance']
                for comp in components:
                    score = semantic_result.get(comp, 0)
                    print(f"   {comp}: {score}")
                
                if overall_score == 0:
                    print("   ❌ Semantic assessment returning 0")
                else:
                    print("   ✅ Semantic assessment working")
            
        except Exception as e:
            print(f"   ❌ Semantic assessment error: {e}")
        
        # Test the actual API endpoint
        print(f"\n🌐 TESTING API ENDPOINT:")
        try:
            # Import app to test the actual endpoint logic
            import requests
            import time
            
            # Make sure server is running
            try:
                response = requests.get('http://127.0.0.1:5000/health', timeout=2)
                print("   ✅ Server is running")
                
                # Test the hybrid scoring endpoint
                api_url = f'http://127.0.0.1:5000/get_hybrid_scoring_analysis/{candidate_id}'
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   API success: {result.get('success', False)}")
                    
                    if 'assessment' in result:
                        assessment = result['assessment']
                        
                        # Check university assessment
                        univ = assessment.get('university_assessment', {})
                        univ_score = univ.get('total_score', 0)
                        print(f"   API University score: {univ_score}")
                        
                        # Check semantic analysis
                        semantic = assessment.get('semantic_analysis', {})
                        semantic_score = semantic.get('overall_score', 0)
                        print(f"   API Semantic score: {semantic_score}")
                        
                        # Check enhanced assessment
                        enhanced = assessment.get('enhanced_assessment', {})
                        enhanced_score = enhanced.get('recommended_score', 0)
                        print(f"   API Enhanced score: {enhanced_score}")
                        
                    else:
                        print("   ❌ No assessment data in API response")
                
                else:
                    print(f"   ❌ API error: {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    
            except requests.exceptions.RequestException:
                print("   ❌ Server not running or not accessible")
        
        except Exception as e:
            print(f"   ❌ API test error: {e}")
    
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_assessment_scores()