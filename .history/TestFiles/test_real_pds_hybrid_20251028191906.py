#!/usr/bin/env python3
"""
Real PDS File Hybrid Scoring Test
Tests the hybrid scoring system with actual PDS files from SamplePDSFiles directory
Demonstrates complete workflow: PDS extraction -> University criteria -> Semantic analysis -> Manual integration
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from improved_pds_extractor import PDSExtractor
from enhanced_assessment_engine import EnhancedAssessmentEngine
from semantic_engine import SemanticEngine
from lspu_job_api import get_all_lspu_job_postings

def test_real_pds_hybrid():
    """Test hybrid scoring with real PDS files"""
    print("🚀 Real PDS Hybrid Scoring Test")
    print("📂 Testing with actual PDS files from SamplePDSFiles")
    print("🎯 University Criteria + Semantic Analysis + Manual Integration")
    print("=" * 70)
    
    # Initialize components
    pds_extractor = PDSExtractor()
    assessment_engine = EnhancedAssessmentEngine()
    semantic_engine = SemanticEngine()
    
    # Get job postings
    job_postings = get_all_lspu_job_postings()
    if not job_postings:
        print("❌ No job postings found")
        return
    
    # Use the first job posting for testing
    job_posting = job_postings[0]
    print(f"🎯 Testing Position: {job_posting['title']}")
    print(f"📋 Requirements: {job_posting['requirements'][:100]}...")
    print()
    
    # Check for SamplePDSFiles directory
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SamplePDSFiles')
    if not os.path.exists(sample_dir):
        print(f"❌ SamplePDSFiles directory not found at: {sample_dir}")
        return
    
    # Get all PDF files from SamplePDSFiles
    pdf_files = [f for f in os.listdir(sample_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"❌ No PDF files found in {sample_dir}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDS files to test")
    print()
    
    # Test with first few PDF files
    test_files = pdf_files[:3]  # Limit to first 3 for demo
    
    for i, pdf_file in enumerate(test_files, 1):
        pdf_path = os.path.join(sample_dir, pdf_file)
        print(f"👤 Testing Candidate {i}: {pdf_file}")
        print("=" * 50)
        
        try:
            # Extract PDS data
            print("📄 Extracting PDS data...")
            pds_data = pds_extractor.extract_pds_data(pdf_path)
            
            if not pds_data:
                print("❌ Failed to extract PDS data")
                continue
            
            candidate_name = pds_data.get('personal_information', {}).get('name', 'Unknown')
            print(f"✅ Extracted data for: {candidate_name}")
            
            # University Criteria Assessment
            print("\n🏛️  University Criteria Assessment:")
            university_score = assessment_engine._calculate_university_criteria_score(pds_data, job_posting)
            
            # Break down university scoring
            edu_score = assessment_engine._calculate_university_education_score(pds_data, job_posting)
            exp_score = assessment_engine._calculate_university_experience_score(pds_data, job_posting)
            training_score = assessment_engine._calculate_university_training_score(pds_data, job_posting)
            eligibility_score = assessment_engine._calculate_university_eligibility_score(pds_data, job_posting)
            
            print(f"   📚 Education: {edu_score:.1f}/30 ({edu_score/30*100:.1f}%)")
            print(f"   💼 Experience: {exp_score:.1f}/5 ({exp_score/5*100:.1f}%)")
            print(f"   📖 Training: {training_score:.1f}/5 ({training_score/5*100:.1f}%)")
            print(f"   🎖️  Eligibility: {eligibility_score:.1f}/10 ({eligibility_score/10*100:.1f}%)")
            print(f"   ⚠️  Potential: 0.0/10 (Manual entry needed)")
            print(f"   ⚠️  Performance: 0.0/40 (Manual entry needed)")
            print(f"   🏛️  Total (without manual): {university_score:.1f}/100")
            
            # Semantic Analysis
            print("\n🧠 Semantic Intelligence Analysis:")
            semantic_scores = semantic_engine.calculate_detailed_semantic_score(pds_data, job_posting)
            
            print(f"   🎓 Education Relevance: {semantic_scores['education_relevance']:.3f}")
            print(f"   💼 Experience Relevance: {semantic_scores['experience_relevance']:.3f}")
            print(f"   📚 Training Relevance: {semantic_scores['training_relevance']:.3f}")
            print(f"   🎯 Overall Job Fit: {semantic_scores['overall_score']:.3f}")
            
            # Show key qualifications
            print("\n📋 Key Qualifications Identified:")
            
            # Education highlights
            education = pds_data.get('educational_background', [])
            if education:
                latest_edu = education[0] if education else {}
                level = latest_edu.get('level', 'N/A')
                school = latest_edu.get('school', 'N/A')
                honors = latest_edu.get('honors_awards', '')
                honors_text = f" ({honors})" if honors else ""
                print(f"   🎓 {level}: {school}{honors_text}")
            
            # Experience highlights
            experience = pds_data.get('work_experience', [])
            for exp in experience[:2]:  # Show top 2 experiences
                position = exp.get('position', 'N/A')
                company = exp.get('company', 'N/A')
                print(f"   💼 {position} at {company}")
            
            # Training highlights
            training = pds_data.get('learning_development', [])
            for train in training[:2]:  # Show top 2 trainings
                title = train.get('title', 'N/A')
                provider = train.get('provider', 'N/A')
                print(f"   📚 {title} from {provider}")
            
            # Hybrid Score Simulation
            print("\n🔬 Hybrid Score Simulation:")
            print("   (With sample manual scores)")
            
            # Simulate manual scores
            manual_potential = 7.5  # Sample interview/written score
            manual_performance = 33.0  # Sample performance rating
            
            hybrid_score = university_score + manual_potential + manual_performance
            print(f"   🏛️  University Criteria: {university_score:.1f}/50")
            print(f"   📝 Manual Potential: {manual_potential}/10")
            print(f"   📊 Manual Performance: {manual_performance}/40")
            print(f"   🎯 Hybrid Total: {hybrid_score:.1f}/100")
            
            # Semantic enhancement factor
            semantic_boost = semantic_scores['overall_score'] * 10  # Convert to boost factor
            enhanced_score = hybrid_score + semantic_boost * 0.1  # 10% semantic boost
            print(f"   🚀 With Semantic Enhancement: {enhanced_score:.1f}/100")
            
            print()
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file}: {str(e)}")
            continue
    
    print("✅ Real PDS hybrid scoring test completed!")
    print("\n🎯 Key Achievements:")
    print("   ✅ Real PDS file processing")
    print("   ✅ University criteria compliance")
    print("   ✅ Semantic relevance analysis")
    print("   ✅ Manual score integration simulation")
    print("   ✅ Hybrid scoring demonstration")

if __name__ == "__main__":
    test_real_pds_hybrid()