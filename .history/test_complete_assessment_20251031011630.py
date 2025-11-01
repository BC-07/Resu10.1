#!/usr/bin/env python3
"""
Test the complete assessment system with candidate 4 to verify education fixes
"""

import json
import sqlite3
import os
import sys
sys.path.append('.')

from enhanced_assessment_engine import EnhancedUniversityAssessmentEngine

def test_complete_assessment():
    """Test the complete assessment system"""
    
    try:
        # Get candidate 4's data from database
        db_path = os.path.join(os.path.dirname(__file__), 'resume_screening.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, pds_extracted_data 
            FROM candidates 
            WHERE id = 4
        """)
        
        result = cursor.fetchone()
        if not result:
            print("❌ Candidate 4 not found")
            return
            
        name, pds_data_raw = result
        cursor.close()
        conn.close()
        
        if isinstance(pds_data_raw, str):
            pds_data = json.loads(pds_data_raw)
        else:
            pds_data = pds_data_raw
            
        print(f"=== TESTING ASSESSMENT FOR: {name} ===")
        
        # Sample job posting
        job_posting = {
            'title': 'LSPU Faculty Position',
            'requirements': 'Masters degree, professional experience, civil service eligibility',
            'description': 'University teaching and research position'
        }
        
        # Test enhanced assessment
        engine = EnhancedUniversityAssessmentEngine()
        
        print("\n=== INDIVIDUAL COMPONENT SCORES ===")
        edu_score = engine._calculate_university_education_score(pds_data)
        exp_score = engine._calculate_university_experience_score(pds_data)
        training_score = engine._calculate_university_training_score(pds_data)
        eligibility_score = engine._calculate_university_eligibility_score(pds_data)
        
        print(f"Education Score: {edu_score}/35")
        print(f"Experience Score: {exp_score}/20")
        print(f"Training Score: {training_score}/15")
        print(f"Eligibility Score: {eligibility_score}/10")
        
        total_traditional = edu_score + exp_score + training_score + eligibility_score
        print(f"Total Traditional Score: {total_traditional}/80")
        
        print("\n=== ENHANCED ASSESSMENT RESULT ===")
        result = engine.assess_candidate_enhanced(
            pds_data, job_posting,
            include_semantic=False,  # Skip semantic to avoid network issues
            include_traditional=True
        )
        
        traditional_breakdown = result.get('traditional_breakdown', {})
        print(f"Enhanced Education: {traditional_breakdown.get('education', 0)}")
        print(f"Enhanced Experience: {traditional_breakdown.get('experience', 0)}")
        print(f"Enhanced Training: {traditional_breakdown.get('training', 0)}")
        print(f"Enhanced Eligibility: {traditional_breakdown.get('eligibility', 0)}")
        print(f"Enhanced Total: {result.get('traditional_score', 0)}")
        
        print("\n=== VERIFICATION ===")
        if edu_score > 0:
            print("✅ Education calculation working")
        else:
            print("❌ Education calculation still broken")
            
        if exp_score > 0:
            print("✅ Experience calculation working")
        else:
            print("❌ Experience calculation still broken")
            
        if total_traditional > 0:
            print("✅ Overall traditional assessment working")
        else:
            print("❌ Overall traditional assessment still broken")
            
        # Simulate university_assessment response structure
        print("\n=== SIMULATED API RESPONSE ===")
        api_response = {
            'university_assessment': {
                'total_score': round(result.get('traditional_score', 0), 2),
                'detailed_scores': {
                    'education': round(traditional_breakdown.get('education', 0), 2),
                    'experience': round(traditional_breakdown.get('experience', 0), 2),
                    'training': round(traditional_breakdown.get('training', 0), 2),
                    'eligibility': round(traditional_breakdown.get('eligibility', 0), 2),
                    'performance': round(traditional_breakdown.get('performance', 0), 2),
                    'potential': round(traditional_breakdown.get('potential', 0), 2)
                }
            }
        }
        
        print(json.dumps(api_response, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_assessment()