#!/usr/bin/env python3
"""
Final Real-World Semantic Test with Proper Data Structure
Converts PDS data to the format expected by the semantic engine
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

def convert_pds_to_semantic_format(pds_data):
    """Convert PDS data to the format expected by semantic engine"""
    personal_info = pds_data.get('personal_info', {})
    educational_background = pds_data.get('educational_background', [])
    work_experience = pds_data.get('work_experience', [])
    learning_development = pds_data.get('learning_development', [])
    
    # Convert education data
    education = []
    for edu in educational_background:
        education_entry = {
            'degree': edu.get('degree_course', edu.get('level', '')),
            'school': edu.get('school', ''),
            'year': edu.get('year_graduated', ''),
            'level': edu.get('level', '')
        }
        education.append(education_entry)
    
    # Convert experience data
    experience = []
    for exp in work_experience:
        experience_entry = {
            'position': exp.get('position', ''),
            'company': exp.get('company', ''),
            'date_from': exp.get('date_from', ''),
            'date_to': exp.get('date_to', ''),
            'description': f"{exp.get('position', '')} at {exp.get('company', '')}"
        }
        experience.append(experience_entry)
    
    # Convert training data  
    training = []
    for train in learning_development:
        training_entry = {
            'title': train.get('title', ''),
            'type': train.get('type', ''),
            'hours': train.get('hours', ''),
            'conductor': train.get('conductor', '')
        }
        training.append(training_entry)
    
    # Create semantic-friendly candidate data
    candidate_data = {
        'id': personal_info.get('full_name', 'unknown'),
        'name': personal_info.get('full_name', 'Unknown'),
        'education': education,
        'experience': experience,
        'training': training,
        'skills': [],  # Would need to extract from text analysis
        'pds_data': pds_data  # Keep original for reference
    }
    
    return candidate_data

def test_pds_extraction_and_conversion():
    """Test PDS extraction and conversion to semantic format"""
    print("🔍 Testing PDS Extraction and Semantic Conversion")
    print("=" * 60)
    
    extractor = ImprovedPDSExtractor()
    pds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SamplePDSFiles')
    
    if not os.path.exists(pds_dir):
        print(f"❌ PDS directory not found: {pds_dir}")
        return []
    
    candidates = []
    
    for filename in os.listdir(pds_dir):
        if filename.endswith(('.xlsx', '.xls', '.pdf')):
            file_path = os.path.join(pds_dir, filename)
            print(f"\n📁 Processing: {filename}")
            
            try:
                # Extract PDS data
                pds_data = extractor.extract_pds_data(file_path)
                
                if pds_data and pds_data.get('educational_background'):
                    print(f"   ✅ Extraction successful")
                    
                    # Convert to semantic format
                    candidate_data = convert_pds_to_semantic_format(pds_data)
                    
                    # Show what was converted
                    print(f"   👤 Name: {candidate_data['name']}")
                    print(f"   🎓 Education entries: {len(candidate_data['education'])}")
                    print(f"   💼 Experience entries: {len(candidate_data['experience'])}")
                    print(f"   📚 Training entries: {len(candidate_data['training'])}")
                    
                    # Show sample data
                    if candidate_data['education']:
                        edu_sample = candidate_data['education'][0]
                        print(f"   📋 Sample Education: {edu_sample.get('degree', 'N/A')} from {edu_sample.get('school', 'N/A')}")
                    
                    if candidate_data['experience']:
                        exp_sample = candidate_data['experience'][0]
                        print(f"   📋 Sample Experience: {exp_sample.get('position', 'N/A')} at {exp_sample.get('company', 'N/A')}")
                    
                    if candidate_data['training']:
                        train_sample = candidate_data['training'][0]
                        print(f"   📋 Sample Training: {train_sample.get('title', 'N/A')}")
                    
                    candidates.append({
                        'filename': filename,
                        'candidate_data': candidate_data,
                        'extraction_success': True
                    })
                    
                else:
                    print(f"   ❌ No meaningful data extracted")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    return candidates

def test_semantic_scoring(candidates):
    """Test semantic scoring with properly formatted data"""
    print(f"\n🧠 Testing Semantic Scoring with Proper Data Format")
    print("=" * 60)
    
    # Initialize components
    try:
        db_manager = DatabaseManager()
        enhanced_engine = EnhancedUniversityAssessmentEngine(db_manager=db_manager)
        semantic_engine = UniversitySemanticEngine()
        
        print("✅ All components initialized successfully")
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return
    
    # Sample job posting
    job_posting = {
        'id': 1,
        'title': 'Assistant Professor - Computer Science',
        'description': """
        The University seeks a qualified Assistant Professor for the Computer Science Department.
        The successful candidate will teach undergraduate and graduate courses in computer science,
        conduct research in areas such as artificial intelligence, machine learning, or software engineering,
        and contribute to departmental service activities.
        """,
        'requirements': [
            'PhD in Computer Science or related field',
            'Strong programming background',
            'Research experience in computer science',
            'Teaching experience preferred',
            'Strong communication skills'
        ]
    }
    
    print(f"\n🎯 Job: {job_posting['title']}")
    
    for i, candidate in enumerate(candidates):
        if not candidate['extraction_success']:
            continue
            
        print(f"\n👤 Candidate {i+1}: {candidate['filename']}")
        
        try:
            candidate_data = candidate['candidate_data']
            
            print(f"   📝 Candidate: {candidate_data['name']}")
            
            # Test semantic scoring only
            result = enhanced_engine.assess_candidate_enhanced(
                candidate_data=candidate_data,
                job_data=job_posting,
                include_semantic=True,
                include_traditional=False
            )
            
            semantic_score = result.get('semantic_score')
            if semantic_score is not None:
                print(f"   🧠 Semantic Score: {semantic_score:.1f}")
                
                # Show breakdown if available
                breakdown = result.get('semantic_breakdown', {})
                if breakdown:
                    print(f"      Education Relevance: {breakdown.get('education_relevance', 0):.3f}")
                    print(f"      Experience Relevance: {breakdown.get('experience_relevance', 0):.3f}")
                    print(f"      Skills Relevance: {breakdown.get('skills_relevance', 0):.3f}")
                    print(f"      Overall Similarity: {breakdown.get('overall_similarity', 0):.3f}")
            else:
                print(f"   ❌ Semantic Score: None (assessment failed)")
                
            # Show assessment details
            if 'error' in result:
                print(f"   ⚠️ Error: {result['error']}")
            
        except Exception as e:
            print(f"   ❌ Assessment failed: {e}")
            import traceback
            traceback.print_exc()

def test_education_position_match():
    """Test with education-focused position to see clear relevance"""
    print(f"\n🎓 Testing Education-Focused Position Match")
    print("=" * 60)
    
    # Get candidates
    candidates = test_pds_extraction_and_conversion()
    
    if not candidates:
        print("❌ No candidates to test")
        return
    
    # Initialize components
    try:
        db_manager = DatabaseManager()
        enhanced_engine = EnhancedUniversityAssessmentEngine(db_manager=db_manager)
        
        print("✅ Enhanced engine initialized")
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return
    
    # Education-focused job posting
    education_job = {
        'id': 2,
        'title': 'Education Program Specialist',
        'description': """
        Seeking an Education Program Specialist to develop and implement educational programs.
        Requires strong educational background in education or curriculum development,
        experience in educational administration, and training in educational methodologies.
        """,
        'requirements': [
            'Masters degree in Education',
            'Curriculum development experience', 
            'Educational administration background',
            'Training in educational methodologies',
            'Program management skills'
        ]
    }
    
    print(f"\n🎯 Job: {education_job['title']}")
    print(f"📋 Focus: Education relevance should score highly for education candidates")
    
    for i, candidate in enumerate(candidates):
        if not candidate['extraction_success']:
            continue
            
        print(f"\n👤 Candidate {i+1}: {candidate['filename']}")
        
        try:
            candidate_data = candidate['candidate_data']
            
            print(f"   📝 Candidate: {candidate_data['name']}")
            
            # Show education background
            education = candidate_data.get('education', [])
            if education:
                print(f"   🎓 Education Background:")
                for edu in education[:3]:  # Show first 3
                    degree = edu.get('degree', 'N/A')
                    school = edu.get('school', 'N/A')
                    print(f"      - {degree} from {school}")
            
            # Test semantic scoring
            result = enhanced_engine.assess_candidate_enhanced(
                candidate_data=candidate_data,
                job_data=education_job,
                include_semantic=True,
                include_traditional=False
            )
            
            semantic_score = result.get('semantic_score')
            if semantic_score is not None:
                print(f"   🧠 Semantic Score: {semantic_score:.1f}")
                
                # Show detailed breakdown
                breakdown = result.get('semantic_breakdown', {})
                if breakdown:
                    print(f"      📊 Education Relevance: {breakdown.get('education_relevance', 0):.3f} ⭐")
                    print(f"      💼 Experience Relevance: {breakdown.get('experience_relevance', 0):.3f}")
                    print(f"      🔧 Skills Relevance: {breakdown.get('skills_relevance', 0):.3f}")
                    print(f"      🎯 Overall Similarity: {breakdown.get('overall_similarity', 0):.3f}")
            else:
                print(f"   ❌ Semantic Score: None")
                
        except Exception as e:
            print(f"   ❌ Assessment failed: {e}")

def main():
    """Main test function"""
    print("🚀 Final Real-World Semantic Test")
    print("📋 Focus: Proper Data Format for Semantic Engine")
    print("🎯 Goal: Complete semantic scoring with actual PDS data")
    print("=" * 70)
    
    # Step 1: Test extraction and conversion
    candidates = test_pds_extraction_and_conversion()
    
    successful_extractions = [c for c in candidates if c['extraction_success']]
    print(f"\n📊 Extraction Summary:")
    print(f"   Total files processed: {len(candidates)}")
    print(f"   Successful extractions: {len(successful_extractions)}")
    
    if successful_extractions:
        # Step 2: Test semantic scoring with CS position
        test_semantic_scoring(successful_extractions)
        
        # Step 3: Test with education-focused position
        print(f"\n" + "="*70)
        test_education_position_match()
    else:
        print("❌ No successful extractions - cannot proceed with semantic testing")
    
    print(f"\n✅ Final semantic test completed!")

if __name__ == "__main__":
    main()