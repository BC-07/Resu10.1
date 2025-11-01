#!/usr/bin/env python3
"""
Corrected Real-World Semantic Test with Proper PDS Field Names
Uses the correct field names based on diagnostic results
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
    """Test PDS extraction with corrected field names"""
    print("🔍 Testing PDS Extraction with Corrected Field Names")
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
                    
                    # Show what was extracted using CORRECT field names
                    personal_info = pds_data.get('personal_info', {})
                    educational_background = pds_data.get('educational_background', [])  # Correct field name
                    work_experience = pds_data.get('work_experience', [])              # Correct field name
                    learning_development = pds_data.get('learning_development', [])    # Correct field name
                    
                    print(f"   👤 Name: {personal_info.get('full_name', personal_info.get('name', 'Not found'))}")
                    print(f"   🎓 Education entries: {len(educational_background)}")
                    print(f"   💼 Experience entries: {len(work_experience)}")
                    print(f"   📚 Training entries: {len(learning_development)}")
                    
                    # Show sample education data
                    if educational_background:
                        edu_sample = educational_background[0]
                        print(f"   📋 Sample Education: {edu_sample.get('level', 'N/A')} - {edu_sample.get('school', 'N/A')}")
                    
                    # Show sample experience data  
                    if work_experience:
                        exp_sample = work_experience[0]
                        print(f"   📋 Sample Experience: {exp_sample.get('position', 'N/A')} at {exp_sample.get('company', 'N/A')}")
                    
                    # Show sample training data
                    if learning_development:
                        train_sample = learning_development[0]
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
            # Convert PDS data to candidate format using CORRECT field names
            pds_data = candidate['pds_data']
            personal_info = pds_data.get('personal_info', {})
            
            # Create detailed candidate text with corrected field names
            education_text = format_education(pds_data.get('educational_background', []))
            experience_text = format_experience(pds_data.get('work_experience', []))
            training_text = format_training(pds_data.get('learning_development', []))
            
            candidate_data = {
                'id': candidate['filename'],
                'name': personal_info.get('full_name', personal_info.get('name', candidate['filename'])),
                'extracted_text': f"""
                Education: {education_text}
                Experience: {experience_text}
                Training: {training_text}
                """.strip(),
                'education': education_text,
                'experience': experience_text,
                'training': training_text
            }
            
            print(f"   📝 Candidate: {candidate_data['name']}")
            print(f"   📄 Text Length: {len(candidate_data['extracted_text'])} characters")
            
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

def format_education(educational_background):
    """Format education entries using correct field names from diagnostic"""
    if not educational_background:
        return "No education information available"
    
    formatted = []
    for edu in educational_background:
        level = edu.get('level', 'Unknown Level')
        school = edu.get('school', 'Unknown Institution')
        course = edu.get('degree_course', '')
        
        entry = f"{level}: {school}"
        if course and course != 'N/a':
            entry += f" - {course}"
        formatted.append(entry)
    
    return '; '.join(formatted)

def format_experience(work_experience):
    """Format experience entries using correct field names from diagnostic"""
    if not work_experience:
        return "No work experience available"
    
    formatted = []
    for exp in work_experience:
        position = exp.get('position', 'Unknown Position')
        company = exp.get('company', 'Unknown Company')
        
        entry = f"{position} at {company}"
        formatted.append(entry)
    
    return '; '.join(formatted)

def format_training(learning_development):
    """Format training entries using correct field names from diagnostic"""
    if not learning_development:
        return "No training information available"
    
    formatted = []
    for train in learning_development:
        title = train.get('title', 'Unknown Training')
        type_info = train.get('type', '')
        
        entry = title
        if type_info and type_info != 'N/a':
            entry += f" ({type_info})"
        formatted.append(entry)
    
    return '; '.join(formatted)

def test_traditional_vs_semantic(candidates):
    """Compare traditional vs semantic scoring"""
    print(f"\n⚖️ Comparing Traditional vs Semantic Scoring")
    print("=" * 60)
    
    # Initialize components
    try:
        db_manager = DatabaseManager()
        enhanced_engine = EnhancedUniversityAssessmentEngine(db_manager=db_manager)
        
        print("✅ Enhanced engine initialized for comparison testing")
    except Exception as e:
        print(f"❌ Component initialization failed: {e}")
        return
    
    # Sample job posting focused on education and experience
    job_posting = {
        'id': 1,
        'title': 'Education Program Specialist',
        'description': """
        Seeking an Education Program Specialist to develop and implement educational programs.
        The role requires strong educational background, curriculum development experience,
        and training in modern educational methodologies. Government service experience preferred.
        """,
        'requirements': [
            'Masters degree in Education or related field',
            'Curriculum development experience',
            'Training in educational methodologies',
            'Government service experience preferred',
            'Project management skills'
        ]
    }
    
    print(f"\n🎯 Job: {job_posting['title']}")
    print(f"📋 Focus: Education relevance, curriculum experience, training background")
    
    for i, candidate in enumerate(candidates):
        if not candidate['extraction_success']:
            continue
            
        print(f"\n👤 Candidate {i+1}: {candidate['filename']}")
        
        try:
            # Convert PDS data to candidate format using CORRECT field names
            pds_data = candidate['pds_data']
            personal_info = pds_data.get('personal_info', {})
            
            # Create detailed candidate text with corrected field names
            education_text = format_education(pds_data.get('educational_background', []))
            experience_text = format_experience(pds_data.get('work_experience', []))
            training_text = format_training(pds_data.get('learning_development', []))
            
            candidate_data = {
                'id': candidate['filename'],
                'name': personal_info.get('full_name', personal_info.get('name', candidate['filename'])),
                'extracted_text': f"""
                Education: {education_text}
                Experience: {experience_text}
                Training: {training_text}
                """.strip(),
                'education': education_text,
                'experience': experience_text,
                'training': training_text
            }
            
            print(f"   📝 Candidate: {candidate_data['name']}")
            
            # Test traditional scoring only
            traditional_result = enhanced_engine.assess_candidate_enhanced(
                candidate_data=candidate_data,
                job_data=job_posting,
                include_semantic=False,
                include_traditional=True
            )
            
            # Test semantic scoring only
            semantic_result = enhanced_engine.assess_candidate_enhanced(
                candidate_data=candidate_data,
                job_data=job_posting,
                include_semantic=True,
                include_traditional=False
            )
            
            # Compare results
            traditional_score = traditional_result.get('total_score', 0)
            semantic_score = semantic_result.get('semantic_score', 0)
            
            print(f"   📊 Traditional Score: {traditional_score:.1f}")
            print(f"   🧠 Semantic Score: {semantic_score:.1f}")
            print(f"   📈 Difference: {semantic_score - traditional_score:.1f}")
            
            # Show detailed breakdown
            print(f"   📋 Education Sample: {education_text[:100]}...")
            print(f"   💼 Experience Sample: {experience_text[:100]}...")
            print(f"   📚 Training Sample: {training_text[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Assessment failed: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main test function"""
    print("🚀 Corrected Real-World Semantic Test")
    print("📋 Focus: PDS Extraction + Semantic Scoring with Correct Field Names")
    print("🎯 Goal: Test real-world semantic scoring and compare with traditional")
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
        
        # Step 3: Compare traditional vs semantic
        test_traditional_vs_semantic(successful_extractions)
    else:
        print("❌ No successful extractions - cannot proceed with semantic testing")
    
    print(f"\n✅ Corrected test completed!")

if __name__ == "__main__":
    main()