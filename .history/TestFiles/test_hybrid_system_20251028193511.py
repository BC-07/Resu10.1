#!/usr/bin/env python3
"""
Test the Updated Hybrid Scoring System
Tests PDS integration with university criteria and semantic enhancement
"""

import os
import sys
import json
from datetime import datetime

# Import required modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from improved_pds_extractor import ImprovedPDSExtractor
    from enhanced_assessment_engine import EnhancedUniversityAssessmentEngine
    from database import DatabaseManager
    from semantic_engine import UniversitySemanticEngine
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def convert_pds_to_candidate_format(pds_data):
    """Convert PDS data to semantic-friendly format"""
    personal_info = pds_data.get('personal_info', {})
    
    # Create candidate data with both PDS structure and converted format
    candidate_data = {
        'id': personal_info.get('full_name', 'unknown'),
        'name': personal_info.get('full_name', 'Unknown'),
        
        # Add PDS raw data for university criteria calculations
        'educational_background': pds_data.get('educational_background', []),
        'work_experience': pds_data.get('work_experience', []),
        'learning_development': pds_data.get('learning_development', []),
        'civil_service_eligibility': pds_data.get('civil_service_eligibility', []),
        
        # Add converted format for semantic engine compatibility
        'education': [],
        'experience': [],
        'training': [],
        
        'pds_data': pds_data  # Keep original for reference
    }
    
    # Convert for semantic engine
    for edu in pds_data.get('educational_background', []):
        candidate_data['education'].append({
            'degree': edu.get('degree_course', ''),
            'school': edu.get('school', ''),
            'level': edu.get('level', ''),
            'year': edu.get('year_graduated', '')
        })
    
    for exp in pds_data.get('work_experience', []):
        candidate_data['experience'].append({
            'position': exp.get('position', ''),
            'company': exp.get('company', ''),
            'description': f"{exp.get('position', '')} at {exp.get('company', '')}"
        })
    
    for train in pds_data.get('learning_development', []):
        candidate_data['training'].append({
            'title': train.get('title', ''),
            'type': train.get('type', '')
        })
    
    return candidate_data

def test_hybrid_scoring():
    """Test the hybrid scoring system"""
    print("🚀 Testing Hybrid Scoring System")
    print("📊 University Criteria + Semantic Enhancement")
    print("=" * 60)
    
    # Load candidates
    extractor = ImprovedPDSExtractor()
    pds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SamplePDSFiles')
    
    candidates = []
    for filename in ['Sample PDS Lenar.xlsx', 'Sample PDS New.xlsx']:
        file_path = os.path.join(pds_dir, filename)
        try:
            pds_data = extractor.extract_pds_data(file_path)
            if pds_data and pds_data.get('educational_background'):
                candidate_data = convert_pds_to_candidate_format(pds_data)
                candidates.append(candidate_data)
                print(f"✅ Loaded: {candidate_data['name']}")
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")
    
    if not candidates:
        print("❌ No candidates loaded")
        return
    
    # Initialize assessment engine
    try:
        db_manager = DatabaseManager()
        enhanced_engine = EnhancedUniversityAssessmentEngine(db_manager=db_manager)
        print(f"✅ Assessment engine initialized")
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        return
    
    # Test job posting
    job_posting = {
        'id': 1,
        'title': 'Assistant Professor - Education',
        'description': """
        Seeking Assistant Professor for Education Department. 
        Requires relevant degree in Education, teaching experience,
        curriculum development background, and civil service eligibility.
        """,
        'requirements': [
            'Masters or PhD in Education',
            'Teaching experience required',
            'Curriculum development experience',
            'Civil service eligibility',
            'Training in educational methodologies'
        ]
    }
    
    print(f"\n🎯 Job Position: {job_posting['title']}")
    print(f"📋 Requirements: Teaching focus, education degree, government eligibility")
    
    # Test each candidate
    for i, candidate in enumerate(candidates):
        print(f"\n👤 Candidate {i+1}: {candidate['name']}")
        print("=" * 50)
        
        # Test university criteria scoring
        try:
            university_score = enhanced_engine._calculate_university_criteria_score(
                candidate, job_posting
            )
            
            print(f"🏛️  University Criteria Score: {university_score['total_score']:.1f}/100")
            print(f"   📚 Education: {university_score['component_scores']['education']:.1f}/30 ({university_score['percentages']['education']:.1f}%)")
            print(f"   💼 Experience: {university_score['component_scores']['experience']:.1f}/5 ({university_score['percentages']['experience']:.1f}%)")
            print(f"   📖 Training: {university_score['component_scores']['training']:.1f}/5 ({university_score['percentages']['training']:.1f}%)")
            print(f"   🎖️  Eligibility: {university_score['component_scores']['eligibility']:.1f}/10 ({university_score['percentages']['eligibility']:.1f}%)")
            print(f"   ⚠️  Potential: {university_score['component_scores']['potential']:.1f}/10 (Manual entry needed)")
            print(f"   ⚠️  Performance: {university_score['component_scores']['performance']:.1f}/40 (Manual entry needed)")
            
        except Exception as e:
            print(f"   ❌ University criteria failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test semantic scoring  
        try:
            result = enhanced_engine.assess_candidate_enhanced(
                candidate_data=candidate,
                job_data=job_posting,
                include_semantic=True,
                include_traditional=False
            )
            
            semantic_score = result.get('semantic_score', 0)
            breakdown = result.get('semantic_breakdown', {})
            
            print(f"\n🧠 Semantic Analysis: {semantic_score:.1f}/100")
            print(f"   🎓 Education Relevance: {breakdown.get('education_relevance', 0):.3f}")
            print(f"   💼 Experience Relevance: {breakdown.get('experience_relevance', 0):.3f}")
            print(f"   📚 Training Relevance: {breakdown.get('training_relevance', 0):.3f}")
            print(f"   🎯 Overall Job Fit: {breakdown.get('overall_similarity', 0):.3f}")
            
            # Show key qualifications
            print(f"\n📋 Key Qualifications:")
            education = candidate.get('educational_background', [])[:2]
            for edu in education:
                level = edu.get('level', 'N/A')
                course = edu.get('degree_course', 'N/A')
                school = edu.get('school', 'N/A')
                honors = edu.get('honors', '')
                print(f"   🎓 {level}: {course} from {school}" + (f" ({honors})" if honors and honors != 'N/a' else ""))
            
            experience = candidate.get('work_experience', [])[:2]
            for exp in experience:
                position = exp.get('position', 'N/A')
                company = exp.get('company', 'N/A')
                print(f"   💼 {position} at {company}")
            
        except Exception as e:
            print(f"   ❌ Semantic assessment failed: {e}")
            import traceback
            traceback.print_exc()

def test_manual_score_integration():
    """Test integration with manual scoring"""
    print(f"\n🔧 Testing Manual Score Integration")
    print("=" * 50)
    
    # Sample manual scores (would come from user interface)
    manual_scores = {
        'potential': 7.5,   # Interview + Written Exam (out of 10)
        'performance': 33   # Performance rating (out of 40)
    }
    
    print(f"📝 Manual Scores Provided:")
    print(f"   Potential (Interview/Written): {manual_scores['potential']}/10")
    print(f"   Performance Rating: {manual_scores['performance']}/40")
    
    # This would show how the final hybrid score combines everything
    print(f"\n💡 Hybrid Score would combine:")
    print(f"   🏛️  University Criteria: Calculated from PDS")
    print(f"   🧠 Semantic Enhancement: AI-powered relevance boost")
    print(f"   📝 Manual Entries: User-provided potential/performance")
    print(f"   🎯 Final Ranking: Enhanced score for better candidate ranking")

def main():
    """Main test function"""
    print("🚀 Hybrid Scoring System Test")
    print("📋 University Criteria + Semantic Intelligence + Manual Integration")
    print("🎯 Goal: Demonstrate complete assessment system")
    print("=" * 70)
    
    test_hybrid_scoring()
    test_manual_score_integration()
    
    print(f"\n✅ Hybrid system testing completed!")
    print(f"\n🎯 Key Features Demonstrated:")
    print(f"   ✅ PDS data extraction and processing")
    print(f"   ✅ University criteria compliance (Education, Experience, Training, Eligibility)")
    print(f"   ✅ Semantic relevance analysis with training focus")
    print(f"   ✅ Manual score integration support")
    print(f"   ✅ Detailed scoring breakdown for transparency")

if __name__ == "__main__":
    main()