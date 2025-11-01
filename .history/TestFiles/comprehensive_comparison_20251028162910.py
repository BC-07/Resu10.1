#!/usr/bin/env python3
"""
Comprehensive Traditional vs Semantic Scoring Comparison
Demonstrates the difference between traditional assessment and semantic understanding
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

def load_candidates():
    """Load and convert PDS candidates"""
    print("📥 Loading Candidate Data from PDS Files")
    print("=" * 50)
    
    extractor = ImprovedPDSExtractor()
    pds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SamplePDSFiles')
    
    candidates = []
    
    for filename in os.listdir(pds_dir):
        if filename.endswith(('.xlsx', '.xls', '.pdf')):
            file_path = os.path.join(pds_dir, filename)
            
            try:
                pds_data = extractor.extract_pds_data(file_path)
                
                if pds_data and pds_data.get('educational_background'):
                    candidate_data = convert_pds_to_semantic_format(pds_data)
                    candidates.append({
                        'filename': filename,
                        'candidate_data': candidate_data
                    })
                    print(f"✅ Loaded: {candidate_data['name']}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")
    
    print(f"\n📊 Total candidates loaded: {len(candidates)}")
    return candidates

def compare_scoring_methods(candidates):
    """Compare traditional vs semantic scoring for different job types"""
    print(f"\n⚖️ Traditional vs Semantic Scoring Comparison")
    print("=" * 60)
    
    # Initialize engine
    try:
        db_manager = DatabaseManager()
        enhanced_engine = EnhancedUniversityAssessmentEngine(db_manager=db_manager)
        print("✅ Assessment engine initialized")
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        return
    
    # Define different job types for comparison
    job_scenarios = [
        {
            'name': 'Computer Science Professor',
            'job_data': {
                'id': 1,
                'title': 'Assistant Professor - Computer Science',
                'description': """
                University seeks Assistant Professor for Computer Science Department.
                Research in AI, machine learning, software engineering. Teaching CS courses.
                PhD in Computer Science required, programming expertise essential.
                """,
                'requirements': [
                    'PhD in Computer Science',
                    'Programming expertise',
                    'Research experience in AI/ML',
                    'Teaching experience'
                ]
            }
        },
        {
            'name': 'Education Specialist',
            'job_data': {
                'id': 2,
                'title': 'Education Program Specialist',
                'description': """
                Education specialist to develop curriculum and manage educational programs.
                Requires education background, curriculum development experience,
                educational administration skills, and program management.
                """,
                'requirements': [
                    'Masters in Education',
                    'Curriculum development',
                    'Educational administration',
                    'Program management'
                ]
            }
        },
        {
            'name': 'Data Analyst',
            'job_data': {
                'id': 3,
                'title': 'Senior Data Analyst',
                'description': """
                Data analyst position requiring statistical analysis, data visualization,
                database management, and analytical thinking. Government data experience preferred.
                """,
                'requirements': [
                    'Data analysis experience',
                    'Statistical skills',
                    'Database management',
                    'Government sector experience'
                ]
            }
        }
    ]
    
    # Compare each candidate against each job
    for scenario in job_scenarios:
        print(f"\n🎯 Job Scenario: {scenario['name']}")
        print(f"📋 {scenario['job_data']['title']}")
        print("-" * 50)
        
        for i, candidate in enumerate(candidates):
            candidate_data = candidate['candidate_data']
            
            print(f"\n👤 Candidate {i+1}: {candidate_data['name']}")
            
            try:
                # Traditional scoring (simplified - just using semantic=False)
                traditional_result = enhanced_engine.assess_candidate_enhanced(
                    candidate_data=candidate_data,
                    job_data=scenario['job_data'],
                    include_semantic=False,
                    include_traditional=True
                )
                
                # Semantic scoring
                semantic_result = enhanced_engine.assess_candidate_enhanced(
                    candidate_data=candidate_data,
                    job_data=scenario['job_data'],
                    include_semantic=True,
                    include_traditional=False
                )
                
                # Extract scores
                traditional_score = traditional_result.get('total_score', 0)
                semantic_score = semantic_result.get('semantic_score', 0)
                
                # Show comparison
                print(f"   📊 Traditional Score: {traditional_score:.1f}")
                print(f"   🧠 Semantic Score:    {semantic_score:.1f}")
                
                difference = semantic_score - traditional_score
                if difference > 0:
                    print(f"   📈 Semantic Higher by: {difference:.1f} points")
                elif difference < 0:
                    print(f"   📉 Traditional Higher by: {abs(difference):.1f} points")
                else:
                    print(f"   ⚖️  Scores Equal")
                
                # Show semantic breakdown
                breakdown = semantic_result.get('semantic_breakdown', {})
                if breakdown:
                    print(f"       🎓 Education Relevance: {breakdown.get('education_relevance', 0):.3f}")
                    print(f"       💼 Experience Relevance: {breakdown.get('experience_relevance', 0):.3f}")
                    print(f"       🎯 Overall Similarity: {breakdown.get('overall_similarity', 0):.3f}")
                
            except Exception as e:
                print(f"   ❌ Assessment failed: {e}")

def analyze_education_experience_relevance(candidates):
    """Detailed analysis of how semantic scoring evaluates education and experience"""
    print(f"\n🔍 Detailed Education & Experience Relevance Analysis")
    print("=" * 60)
    
    # Initialize semantic engine directly
    try:
        semantic_engine = UniversitySemanticEngine()
        print("✅ Semantic engine initialized for detailed analysis")
    except Exception as e:
        print(f"❌ Semantic engine initialization failed: {e}")
        return
    
    # Test job focused on different aspects
    test_jobs = [
        {
            'focus': 'Computer Science & Technology',
            'job_data': {
                'title': 'Computer Science Faculty',
                'description': 'Computer science professor with programming and software development expertise',
                'requirements': ['Computer Science degree', 'Programming skills', 'Software development']
            }
        },
        {
            'focus': 'Education & Curriculum',
            'job_data': {
                'title': 'Curriculum Developer',
                'description': 'Education specialist for curriculum design and educational program development',
                'requirements': ['Education degree', 'Curriculum development', 'Educational administration']
            }
        },
        {
            'focus': 'Government & Administration',
            'job_data': {
                'title': 'Government Program Manager',
                'description': 'Program manager for government initiatives and administrative programs',
                'requirements': ['Government experience', 'Program management', 'Administrative skills']
            }
        }
    ]
    
    for job_test in test_jobs:
        print(f"\n🎯 Testing Relevance for: {job_test['focus']}")
        print("-" * 40)
        
        for i, candidate in enumerate(candidates):
            candidate_data = candidate['candidate_data']
            print(f"\n👤 {candidate_data['name']}:")
            
            try:
                # Calculate detailed semantic scores
                semantic_details = semantic_engine.calculate_detailed_semantic_score(
                    candidate_data, job_test['job_data']
                )
                
                if 'error' not in semantic_details:
                    print(f"   📊 Education Relevance: {semantic_details.get('education_relevance', 0):.3f}")
                    print(f"   💼 Experience Relevance: {semantic_details.get('experience_relevance', 0):.3f}")
                    print(f"   🎯 Overall Score: {semantic_details.get('overall_score', 0):.3f}")
                    
                    # Show top education entries
                    education = candidate_data.get('education', [])[:3]
                    print(f"   🎓 Key Education:")
                    for edu in education:
                        degree = edu.get('degree', 'N/A')
                        school = edu.get('school', 'N/A')
                        print(f"      - {degree} ({school})")
                    
                    # Show top experience entries
                    experience = candidate_data.get('experience', [])[:3]
                    print(f"   💼 Key Experience:")
                    for exp in experience:
                        position = exp.get('position', 'N/A')
                        company = exp.get('company', 'N/A')
                        print(f"      - {position} ({company})")
                
                else:
                    print(f"   ❌ Error: {semantic_details['error']}")
                    
            except Exception as e:
                print(f"   ❌ Analysis failed: {e}")

def main():
    """Main comparison function"""
    print("🚀 Comprehensive Traditional vs Semantic Scoring Analysis")
    print("📊 Demonstrates the power of semantic understanding in candidate assessment")
    print("🎯 Shows how semantic scoring captures relevance that traditional methods miss")
    print("=" * 80)
    
    # Load candidates
    candidates = load_candidates()
    
    if not candidates:
        print("❌ No candidates loaded - cannot proceed")
        return
    
    # Show candidate summaries
    print(f"\n👥 Candidate Profiles Summary:")
    for i, candidate in enumerate(candidates):
        cd = candidate['candidate_data']
        print(f"   {i+1}. {cd['name']}")
        print(f"      🎓 Education: {len(cd['education'])} entries")
        print(f"      💼 Experience: {len(cd['experience'])} entries")
        print(f"      📚 Training: {len(cd['training'])} entries")
    
    # Run comprehensive comparison
    compare_scoring_methods(candidates)
    
    # Detailed relevance analysis
    analyze_education_experience_relevance(candidates)
    
    print(f"\n✅ Comprehensive scoring comparison completed!")
    print(f"\n🎯 Key Insights:")
    print(f"   • Semantic scoring understands context and relevance")
    print(f"   • Traditional scoring may miss nuanced qualifications")
    print(f"   • Education and experience relevance varies by job focus")
    print(f"   • Semantic analysis provides detailed breakdown of fit")

if __name__ == "__main__":
    main()