#!/usr/bin/env python3
"""
Compare all three assessment systems to identify discrepancies
"""
import json
import sys
import os

# Add the current directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_assessment_systems():
    """Compare the three different assessment systems"""
    
    # Sample PDS data for testing
    sample_pds_data = {
        'educational_background': [
            {
                'level': 'GRADUATE STUDIES',
                'degree': 'Master of Science in Education',
                'school': 'Laguna State Polytechnic University',
                'year_graduated': '2020'
            }
        ],
        'work_experience': [
            {
                'position': 'Teacher III',
                'company': 'Department of Education',
                'from_date': '2018',
                'to_date': '2023'
            }
        ],
        'training_programs': [
            {
                'title': 'Educational Leadership Seminar',
                'hours': 40
            }
        ],
        'civil_service_eligibility': [
            {
                'eligibility': 'Professional Board Examination for Teachers',
                'rating': '85%',
                'date_conferment': '2018'
            }
        ]
    }
    
    # Sample job posting
    sample_job = {
        'position_title': 'Instructor I',
        'education_requirements': 'Master\'s degree in Education or related field',
        'experience_requirements': '3 years relevant teaching experience',
        'duties_responsibilities': 'Teaching and research duties'
    }
    
    print("🔍 COMPARING ALL THREE ASSESSMENT SYSTEMS")
    print("=" * 60)
    
    # SYSTEM 1: Official LSPU Assessment Engine 
    print("\n📋 SYSTEM 1: Official LSPU Assessment Engine (assessment_engine.py)")
    print("Expected percentages: Education (40%), Experience (20%), Training (10%), Eligibility (10%)")
    try:
        from assessment_engine import UniversityAssessmentEngine
        from database import DatabaseManager
        
        db = DatabaseManager()
        lspu_engine = UniversityAssessmentEngine(db)
        
        lspu_result = lspu_engine.assess_candidate_for_lspu_job(sample_pds_data, sample_job)
        
        print("LSPU Assessment Results:")
        for category, data in lspu_result.get('assessment_results', {}).items():
            if isinstance(data, dict) and 'score' in data:
                max_possible = data.get('max_possible', data.get('category_weight', 'Unknown'))
                print(f"  {category.title()}: {data['score']}/{max_possible}")
        
        total_score = lspu_result.get('total_automated_score', 0)
        print(f"  Total Automated Score: {total_score}")
        
    except Exception as e:
        print(f"❌ LSPU Assessment failed: {e}")
    
    # SYSTEM 2: Enhanced Assessment Engine
    print("\n🔧 SYSTEM 2: Enhanced Assessment Engine (enhanced_assessment_engine.py)")
    print("Uses different scoring system with variable max points")
    try:
        from enhanced_assessment_engine import EnhancedUniversityAssessmentEngine
        
        enhanced_engine = EnhancedUniversityAssessmentEngine()
        enhanced_result = enhanced_engine.assess_candidate_enhanced(
            sample_pds_data, sample_job, 
            include_semantic=False, 
            include_traditional=True
        )
        
        print("Enhanced Assessment Results:")
        traditional_breakdown = enhanced_result.get('traditional_breakdown', {})
        for category, score in traditional_breakdown.items():
            print(f"  {category.title()}: {score}")
        
        total_score = enhanced_result.get('traditional_score', 0)
        print(f"  Total Traditional Score: {total_score}")
        
    except Exception as e:
        print(f"❌ Enhanced Assessment failed: {e}")
    
    # SYSTEM 3: Legacy app.py scoring
    print("\n📱 SYSTEM 3: Legacy app.py scoring")
    print("Uses 40-point education scale: PhD=40, Masters=35, Bachelor=25")
    
    # Simulate the legacy education scoring from app.py
    education_levels = {
        'phd': 40, 'doctorate': 40, 'doctoral': 40,
        'master': 35, 'masters': 35, 'msc': 35, 'mba': 35,
        'graduate studies': 35,  # This matches our sample data
        'bachelor': 25, 'bachelors': 25, 'degree': 25, 'bsc': 25,
        'diploma': 15, 'associate': 15,
        'certificate': 10, 'high school': 5
    }
    
    max_education_score = 0
    for edu in sample_pds_data['educational_background']:
        edu_text = (edu.get('level', '') + ' ' + edu.get('degree', '')).lower()
        for level, points in education_levels.items():
            if level in edu_text:
                max_education_score = max(max_education_score, points)
                break
    
    print(f"Legacy App.py Results:")
    print(f"  Education: {max_education_score}/40 (found 'graduate studies' = 35 points)")
    
    print("\n🎯 ANALYSIS:")
    print("- The UI showing 35/40 education comes from the Legacy app.py system")
    print("- The official LSPU system should use different max points per category")
    print("- Enhanced system uses yet another scoring approach")
    print("- This explains why you see inconsistent calculations!")

if __name__ == "__main__":
    test_assessment_systems()