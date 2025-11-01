#!/usr/bin/env python3
"""
Simple Real-World Semantic Test with Improved PDS Extraction
Focuses on getting the PDS extraction working correctly first
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

def test_pds_extraction():
    """Test PDS extraction with improved extractor"""
    print("🔍 Testing PDS Extraction with ImprovedPDSExtractor")
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
                
                if pds_data:
                    print(f"   ✅ Extraction successful")
                    
                    # Show what was extracted
                    personal_info = pds_data.get('personal_info', {})
                    education = pds_data.get('education', [])
                    experience = pds_data.get('experience', [])
                    training = pds_data.get('training', [])
                    
                    print(f"   👤 Name: {personal_info.get('name', personal_info.get('full_name', 'Not found'))}")
                    print(f"   🎓 Education entries: {len(education)}")
                    print(f"   💼 Experience entries: {len(experience)}")
                    print(f"   📚 Training entries: {len(training)}")
                    
                    # Show sample education data
                    if education:
                        edu_sample = education[0]
                        print(f"   📋 Sample Education: {edu_sample.get('level', 'N/A')} - {edu_sample.get('school', 'N/A')}")
                    
                    # Show sample experience data
                    if experience:
                        exp_sample = experience[0]
                        print(f"   📋 Sample Experience: {exp_sample.get('position', 'N/A')} at {exp_sample.get('company', 'N/A')}")
                    
                    # Show sample training data
                    if training:
                        train_sample = training[0]
                        print(f"   📋 Sample Training: {train_sample.get('title', 'N/A')}")
                    
                    candidates.append({
                        'filename': filename,
                        'pds_data': pds_data,
                        'extraction_success': True
                    })
                    
                else:
                    print(f"   ❌ No data extracted")
                    candidates.append({
                        'filename': filename,
                        'pds_data': {},
                        'extraction_success': False
                    })
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                candidates.append({
                    'filename': filename,
                    'pds_data': {},
                    'extraction_success': False,
                    'error': str(e)
                })
    
    return candidates

def test_semantic_scoring(candidates):
    """Test semantic scoring with extracted PDS data"""
    print(f"\n🧠 Testing Semantic Scoring")
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
            # Convert PDS data to candidate format
            pds_data = candidate['pds_data']
            personal_info = pds_data.get('personal_info', {})
            
            # Create detailed candidate text
            education_text = format_education(pds_data.get('education', []))
            experience_text = format_experience(pds_data.get('experience', []))
            training_text = format_training(pds_data.get('training', []))
            
            candidate_data = {
                'id': candidate['filename'],
                'name': personal_info.get('name', personal_info.get('full_name', candidate['filename'])),
                'extracted_text': f"""
                Education: {education_text}
                Experience: {experience_text}
                Training: {training_text}
                """,
                'education': education_text,
                'experience': experience_text,
                'training': training_text
            }
            
            print(f"   📝 Candidate: {candidate_data['name']}")
            
            # Test semantic scoring only
            result = enhanced_engine.assess_candidate_enhanced(
                candidate_data=candidate_data,
                job_data=job_posting,
                include_semantic=True,
                include_traditional=False
            )
            
            semantic_score = result.get('semantic_score', 0)
            print(f"   🧠 Semantic Score: {semantic_score:.1f}")
            
            # Show breakdown if available
            breakdown = result.get('semantic_breakdown', {})
            if breakdown:
                print(f"      Education Relevance: {breakdown.get('education_relevance', 0):.3f}")
                print(f"      Experience Relevance: {breakdown.get('experience_relevance', 0):.3f}")
                print(f"      Skills Relevance: {breakdown.get('skills_relevance', 0):.3f}")
                print(f"      Overall Similarity: {breakdown.get('overall_similarity', 0):.3f}")
            
        except Exception as e:
            print(f"   ❌ Assessment failed: {e}")
            import traceback
            traceback.print_exc()

def format_education(education_list):
    """Format education entries"""
    if not education_list:
        return "No education information available"
    
    formatted = []
    for edu in education_list:
        level = edu.get('level', edu.get('education_level', 'Unknown'))
        school = edu.get('school', edu.get('institution', 'Unknown Institution'))
        course = edu.get('course', edu.get('degree', ''))
        
        entry = f"{level}: {school}"
        if course:
            entry += f" - {course}"
        formatted.append(entry)
    
    return '; '.join(formatted)

def format_experience(experience_list):
    """Format experience entries"""
    if not experience_list:
        return "No work experience available"
    
    formatted = []
    for exp in experience_list:
        position = exp.get('position', exp.get('job_title', 'Unknown Position'))
        company = exp.get('company', exp.get('employer', 'Unknown Company'))
        
        entry = f"{position} at {company}"
        formatted.append(entry)
    
    return '; '.join(formatted)

def format_training(training_list):
    """Format training entries"""
    if not training_list:
        return "No training information available"
    
    formatted = []
    for train in training_list:
        title = train.get('title', train.get('course_title', 'Unknown Training'))
        type_info = train.get('type', '')
        
        entry = title
        if type_info:
            entry += f" ({type_info})"
        formatted.append(entry)
    
    return '; '.join(formatted)

def main():
    """Main test function"""
    print("🚀 Simple Real-World Semantic Test")
    print("📋 Focus: PDS Extraction + Semantic Scoring")
    print("🎯 Goal: Verify improved PDS extractor works with semantic engine")
    print("=" * 70)
    
    # Step 1: Test PDS extraction
    candidates = test_pds_extraction()
    
    successful_extractions = [c for c in candidates if c['extraction_success']]
    print(f"\n📊 Extraction Summary:")
    print(f"   Total files processed: {len(candidates)}")
    print(f"   Successful extractions: {len(successful_extractions)}")
    print(f"   Failed extractions: {len(candidates) - len(successful_extractions)}")
    
    if successful_extractions:
        # Step 2: Test semantic scoring
        test_semantic_scoring(successful_extractions)
    else:
        print("❌ No successful extractions - cannot proceed with semantic testing")
    
    print(f"\n✅ Simple test completed!")

if __name__ == "__main__":
    main()