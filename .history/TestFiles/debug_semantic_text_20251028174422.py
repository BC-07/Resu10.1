#!/usr/bin/env python3
"""
Debug the semantic text extraction issue
Check what text is being generated and why semantic engine rejects it
"""

import os
import sys
import json
from datetime import datetime

# Import required modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from improved_pds_extractor import ImprovedPDSExtractor
    from semantic_engine import UniversitySemanticEngine
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

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

def debug_text_extraction():
    """Debug what text is being generated and why semantic engine rejects it"""
    print("🔍 Debug Text Extraction for Semantic Engine")
    print("=" * 60)
    
    extractor = ImprovedPDSExtractor()
    pds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SamplePDSFiles')
    
    # Process the first successful file
    file_path = os.path.join(pds_dir, 'Sample PDS Lenar.xlsx')
    print(f"📁 Processing: {file_path}")
    
    try:
        # Extract PDS data
        pds_data = extractor.extract_pds_data(file_path)
        
        if not pds_data:
            print("❌ No PDS data extracted")
            return
            
        # Get sections
        personal_info = pds_data.get('personal_info', {})
        educational_background = pds_data.get('educational_background', [])
        work_experience = pds_data.get('work_experience', [])
        learning_development = pds_data.get('learning_development', [])
        
        print(f"\n📊 Raw Data Summary:")
        print(f"   Education entries: {len(educational_background)}")
        print(f"   Experience entries: {len(work_experience)}")
        print(f"   Training entries: {len(learning_development)}")
        
        # Format sections
        education_text = format_education(educational_background)
        experience_text = format_experience(work_experience)
        training_text = format_training(learning_development)
        
        print(f"\n📝 Formatted Text Sections:")
        print(f"   Education text length: {len(education_text)}")
        print(f"   Experience text length: {len(experience_text)}")
        print(f"   Training text length: {len(training_text)}")
        
        # Show actual text content
        print(f"\n📋 Education Text:")
        print(f"   {education_text}")
        
        print(f"\n💼 Experience Text:")
        print(f"   {experience_text}")
        
        print(f"\n📚 Training Text:")
        print(f"   {training_text}")
        
        # Create combined text
        combined_text = f"""
        Education: {education_text}
        Experience: {experience_text}
        Training: {training_text}
        """.strip()
        
        print(f"\n🔗 Combined Text:")
        print(f"   Length: {len(combined_text)} characters")
        print(f"   Content:")
        print(f"   {combined_text}")
        
        # Test semantic engine directly
        print(f"\n🧠 Testing Semantic Engine Directly:")
        semantic_engine = UniversitySemanticEngine()
        
        # Test individual components
        print(f"   Testing education text encoding...")
        try:
            edu_embedding = semantic_engine.encode_text(education_text)
            print(f"   ✅ Education embedding shape: {edu_embedding.shape if edu_embedding is not None else 'None'}")
        except Exception as e:
            print(f"   ❌ Education embedding failed: {e}")
            
        print(f"   Testing experience text encoding...")
        try:
            exp_embedding = semantic_engine.encode_text(experience_text)
            print(f"   ✅ Experience embedding shape: {exp_embedding.shape if exp_embedding is not None else 'None'}")
        except Exception as e:
            print(f"   ❌ Experience embedding failed: {e}")
            
        print(f"   Testing training text encoding...")
        try:
            train_embedding = semantic_engine.encode_text(training_text)
            print(f"   ✅ Training embedding shape: {train_embedding.shape if train_embedding is not None else 'None'}")
        except Exception as e:
            print(f"   ❌ Training embedding failed: {e}")
            
        print(f"   Testing combined text encoding...")
        try:
            combined_embedding = semantic_engine.encode_text(combined_text)
            print(f"   ✅ Combined embedding shape: {combined_embedding.shape if combined_embedding is not None else 'None'}")
        except Exception as e:
            print(f"   ❌ Combined embedding failed: {e}")
        
        # Test full assessment with job posting
        job_text = """
        Assistant Professor Computer Science position requires PhD in Computer Science,
        programming experience, research background, and teaching skills.
        """
        
        print(f"\n🎯 Testing Full Semantic Assessment:")
        print(f"   Job text: {job_text}")
        
        try:
            result = semantic_engine.assess_semantic_relevance(
                candidate_text=combined_text,
                job_text=job_text
            )
            print(f"   ✅ Assessment result: {result}")
        except Exception as e:
            print(f"   ❌ Assessment failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function"""
    print("🔍 Semantic Text Extraction Debug")
    print("📋 Goal: Find why semantic engine rejects extracted text")
    print("=" * 60)
    
    debug_text_extraction()
    
    print(f"\n✅ Debug completed!")

if __name__ == "__main__":
    main()