#!/usr/bin/env python3
"""
Test the enhanced assessment engine with real PDS data
"""

import json
import sys
sys.path.append('.')

from enhanced_assessment_engine import EnhancedUniversityAssessmentEngine

def test_assessment_engine():
    """Test the assessment engine with real PDS data"""
    
    # Sample PDS data structure from our database
    pds_data = {
        'personal_info': {'name': 'Juan Dela Cruz'},
        'educational_background': [
            {
                'level': 'ELEMENTARY',
                'school': 'Manila Elementary School',
                'degree': 'Elementary',
                'year_graduated': '1997',
                'highest_level': 'Graduated',
                'honors': ''
            },
            {
                'level': 'SECONDARY',
                'school': 'Manila High School',
                'degree': 'High School',
                'year_graduated': '2001',
                'highest_level': 'Graduated',
                'honors': 'With Honors'
            },
            {
                'level': 'COLLEGE',
                'school': 'University of the Philippines',
                'degree': 'Bachelor of Science in Computer Science',
                'year_graduated': '2005',
                'highest_level': 'Graduated',
                'honors': 'Cum Laude'
            },
            {
                'level': 'GRADUATE STUDIES',
                'school': 'Laguna State Polytechnic University',
                'degree': 'Master of Science in Information Technology',
                'year_graduated': '2010',
                'highest_level': 'Graduated',
                'honors': 'Magna Cum Laude'
            }
        ],
        'work_experience': [
            {
                'position': 'Software Developer',
                'company': 'Tech Solutions Inc.',
                'salary': '₱45,000',
                'date_from': '2005-06',
                'date_to': '2008-12',
                'status': 'Permanent',
                'duties': 'Developed web applications and systems'
            }
        ],
        'training_programs': [
            {
                'title': 'Advanced Programming',
                'type': 'Technical Training',
                'hours': '40',
                'date': '2020-01-15'
            }
        ],
        'civil_service_eligibility': [
            {
                'eligibility': 'Professional Civil Service Eligibility',
                'rating': '85.5',
                'date': '2005-03-15',
                'place': 'Manila'
            }
        ],
        'other_info': {}
    }
    
    # Sample job posting
    job_posting = {
        'title': 'Assistant Professor',
        'requirements': 'Masters degree, teaching experience',
        'description': 'University teaching position'
    }
    
    try:
        engine = EnhancedUniversityAssessmentEngine()
        
        print("=== TESTING INDIVIDUAL SCORE CALCULATIONS ===")
        
        # Test education calculation
        edu_score = engine._calculate_university_education_score(pds_data)
        print(f"Education Score: {edu_score}")
        
        # Test experience calculation
        exp_score = engine._calculate_university_experience_score(pds_data)
        print(f"Experience Score: {exp_score}")
        
        # Test training calculation
        training_score = engine._calculate_university_training_score(pds_data)
        print(f"Training Score: {training_score}")
        
        # Test eligibility calculation
        eligibility_score = engine._calculate_university_eligibility_score(pds_data)
        print(f"Eligibility Score: {eligibility_score}")
        
        print(f"\n=== TOTAL SCORES ===")
        total = edu_score + exp_score + training_score + eligibility_score
        print(f"Total University Score: {total}")
        
        print(f"\n=== TESTING FULL ASSESSMENT ===")
        result = engine.assess_candidate_enhanced(
            pds_data, job_posting,
            include_semantic=False,  # Skip semantic to avoid network issues
            include_traditional=True
        )
        
        print(f"Enhanced Assessment Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_assessment_engine()