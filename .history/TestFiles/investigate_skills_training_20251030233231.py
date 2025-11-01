#!/usr/bin/env python3
"""
Investigate Skills vs Training Data Processing
"""

import sys
import os
# Add parent directory to path since we're in TestFiles subfolder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from semantic_engine import UniversitySemanticEngine

def investigate_skills_training_processing():
    """Investigate how skills vs training is processed"""
    try:
        print("🔍 Investigating Skills vs Training Data Processing...")
        
        # Create semantic engine instance
        semantic_engine = UniversitySemanticEngine()
        
        print("✅ Semantic engine created")
        
        # Sample PDS data with training but no skills
        sample_pds_data = {
            'educational_background': [
                {
                    'level': 'College',
                    'school_name': 'University Sample',
                    'course': 'Computer Science',
                    'year_graduated': '2020'
                }
            ],
            'work_experience': [
                {
                    'position_title': 'Developer',
                    'company': 'Tech Company',
                    'inclusive_dates_from': '2020-01-01',
                    'inclusive_dates_to': '2023-12-31'
                }
            ],
            'learning_development': [  # This is TRAINING data
                {
                    'title': 'Python Programming',
                    'training_provider': 'Online Academy',
                    'inclusive_dates_from': '2021-01-01',
                    'inclusive_dates_to': '2021-03-01'
                }
            ],
            # NOTE: NO 'skills' field exists in PDS
        }
        
        sample_job_data = {
            'title': 'Instructor I',
            'description': 'Teaching programming',
            'requirements': 'Programming skills required'
        }
        
        print(f"\n📋 PDS Data Keys: {list(sample_pds_data.keys())}")
        print(f"🏫 Learning Development Entries: {len(sample_pds_data['learning_development'])}")
        print(f"❌ Skills Field Present: {'skills' in sample_pds_data}")
        
        # Test semantic analysis
        print(f"\n🧪 Testing calculate_detailed_semantic_score...")
        semantic_result = semantic_engine.calculate_detailed_semantic_score(sample_pds_data, sample_job_data)
        
        print(f"\n📊 SEMANTIC ANALYSIS RESULTS:")
        print(f"  - overall_score: {semantic_result.get('overall_score')}")
        print(f"  - education_relevance: {semantic_result.get('education_relevance')}")
        print(f"  - experience_relevance: {semantic_result.get('experience_relevance')}")
        print(f"  - skills_relevance: {semantic_result.get('skills_relevance')}")
        print(f"  - training_relevance: {semantic_result.get('training_relevance')}")
        
        print(f"\n🔍 DETAILED BREAKDOWN:")
        print(json.dumps(semantic_result, indent=2))
        
        return semantic_result
        
    except Exception as e:
        print(f"❌ Error investigating skills/training: {e}")
        import traceback
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return None

def analyze_semantic_engine_methods():
    """Analyze how semantic engine processes skills vs training"""
    try:
        print(f"\n🔎 Analyzing Semantic Engine Methods...")
        
        # Look at the semantic engine code to understand skills processing
        semantic_engine = UniversitySemanticEngine()
        
        # Check if there are specific methods for skills vs training
        methods = [method for method in dir(semantic_engine) if not method.startswith('_')]
        print(f"📋 Public methods: {methods}")
        
        # Check the calculate_detailed_semantic_score method signature
        import inspect
        signature = inspect.signature(semantic_engine.calculate_detailed_semantic_score)
        print(f"🔧 Method signature: {signature}")
        
    except Exception as e:
        print(f"❌ Error analyzing methods: {e}")

if __name__ == "__main__":
    investigate_skills_training_processing()
    analyze_semantic_engine_methods()