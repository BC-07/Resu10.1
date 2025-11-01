#!/usr/bin/env python3
"""
Test traditional assessment directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_engine import UniversityAssessmentEngine
from database import DatabaseManager
import traceback

def test_traditional_assessment_simple():
    """Test traditional assessment with sample data"""
    try:
        print("🧪 Testing Traditional Assessment with Sample Data...")
        
        # Create assessment engine
        db_manager = DatabaseManager()
        assessment_engine = UniversityAssessmentEngine(db_manager)
        
        print("✅ Assessment engine created")
        
        # Sample PDS data structure (based on the keys we saw in debug)
        sample_pds_data = {
            'personal_info': {
                'first_name': 'John',
                'last_name': 'Doe',
                'middle_name': 'M'
            },
            'educational_background': [
                {
                    'level': 'College',
                    'school_name': 'University of the Philippines',
                    'course': 'Bachelor of Science in Computer Science',
                    'year_graduated': '2020',
                    'honors': 'Cum Laude'
                }
            ],
            'work_experience': [
                {
                    'position_title': 'Software Developer',
                    'company': 'Tech Company',
                    'salary': '50000',
                    'inclusive_dates_from': '2020-01-01',
                    'inclusive_dates_to': '2023-12-31'
                }
            ],
            'learning_development': [
                {
                    'title': 'Python Programming',
                    'training_provider': 'Online Academy',
                    'inclusive_dates_from': '2021-01-01',
                    'inclusive_dates_to': '2021-03-01'
                }
            ],
            'civil_service_eligibility': [
                {
                    'career_service': 'CS Professional',
                    'rating': '85.5',
                    'date_of_examination': '2020-10-15'
                }
            ],
            'voluntary_work': [],
            'family_background': {},
            'other_information': {},
            'extraction_metadata': {}
        }
        
        # Sample LSPU job data (based on what we saw in the logs)
        sample_job_data = {
            'id': 2,
            'position_title': 'Instructor I',
            'department': 'Computer Science',
            'salary_grade': '12',
            'description': 'Teaching position for computer science',
            'requirements': 'Bachelor degree in Computer Science or related field',
            'education': 'Bachelor',
            'experience': '0',
            'title': 'Instructor I'
        }
        
        print(f"📊 Testing with sample data...")
        print(f"  - Job: {sample_job_data['position_title']}")
        print(f"  - Education entries: {len(sample_pds_data['educational_background'])}")
        print(f"  - Work experience entries: {len(sample_pds_data['work_experience'])}")
        
        # Test traditional assessment
        result = assessment_engine.assess_candidate_for_lspu_job(sample_pds_data, sample_job_data)
        
        print(f"\n📊 Assessment result:")
        print(f"  - final_score: {result.get('final_score')}")
        print(f"  - education_score: {result.get('education_score')}")
        print(f"  - experience_score: {result.get('experience_score')}")
        print(f"  - training_score: {result.get('training_score')}")
        print(f"  - eligibility_score: {result.get('eligibility_score')}")
        print(f"  - performance_score: {result.get('performance_score')}")
        print(f"  - potential_score: {result.get('potential_score')}")
        
        if result.get('final_score', 0) == 0:
            print(f"\n❌ Traditional assessment is still returning 0")
            print(f"🔍 Debugging deeper...")
            
            # Let's check what the assessment engine is actually doing
            print(f"📋 Assessment result full data: {result}")
            
        else:
            print(f"\n✅ Traditional assessment working! Score: {result.get('final_score')}")
            
        return result
        
    except Exception as e:
        print(f"❌ Error testing traditional assessment: {e}")
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    test_traditional_assessment_simple()