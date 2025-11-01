#!/usr/bin/env python3
"""
Real-World Semantic Scoring Test with Improved PDS Extraction
Compares traditional assessment engine scores vs semantic understanding scores
Uses actual PDS files and real job postings for comprehensive evaluation
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# Import required modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from improved_pds_extractor import ImprovedPDSExtractor
    from enhanced_assessment_engine import EnhancedUniversityAssessmentEngine
    from assessment_engine import UniversityAssessmentEngine
    from database import DatabaseManager
    from semantic_engine import UniversitySemanticEngine
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

class RealWorldSemanticTest:
    """Test semantic scoring with real PDS files and job postings"""
    
    def __init__(self):
        self.pds_extractor = ImprovedPDSExtractor()
        self.db_manager = DatabaseManager()
        self.enhanced_engine = EnhancedUniversityAssessmentEngine(db_manager=self.db_manager)
        self.traditional_engine = UniversityAssessmentEngine(db_manager=self.db_manager)
        self.semantic_engine = UniversitySemanticEngine()
        
        # Sample job postings for testing
        self.job_postings = {
            'academic_cs': {
                'id': 1,
                'title': 'Assistant Professor - Computer Science',
                'description': """
                The University seeks a qualified Assistant Professor for the Computer Science Department.
                The successful candidate will teach undergraduate and graduate courses in computer science,
                conduct research in areas such as artificial intelligence, machine learning, software engineering,
                or data science, and contribute to departmental service activities.
                """,
                'requirements': [
                    'PhD in Computer Science or related field',
                    'Strong background in programming languages (Python, Java, C++)',
                    'Experience in software development and system design',
                    'Research experience in AI, ML, or software engineering',
                    'Teaching experience at university level preferred',
                    'Strong communication and presentation skills',
                    'Ability to work collaboratively in academic environment'
                ],
                'position_type_id': 1
            },
            'engineering_faculty': {
                'id': 2,
                'title': 'Associate Professor - Electrical Engineering',
                'description': """
                The Engineering Department is seeking an Associate Professor in Electrical Engineering
                to join our faculty. The position involves teaching electrical engineering courses,
                supervising student projects, conducting research in power systems, electronics,
                or telecommunications, and participating in university service.
                """,
                'requirements': [
                    'PhD in Electrical Engineering or related field',
                    'Professional Engineering (PE) license preferred',
                    'Industry experience in electrical systems design',
                    'Research background in power systems or electronics',
                    'Strong mathematical and analytical skills',
                    'Experience with electrical design software',
                    'Published research in peer-reviewed journals'
                ],
                'position_type_id': 2
            },
            'administrative_role': {
                'id': 3,
                'title': 'University Registrar',
                'description': """
                We are seeking an experienced University Registrar to oversee student records,
                academic scheduling, graduation processes, and ensure compliance with
                academic policies and regulations. The role requires strong organizational
                skills and experience in higher education administration.
                """,
                'requirements': [
                    'Masters degree in Education Administration or related field',
                    'Minimum 5 years experience in university administration',
                    'Knowledge of student information systems',
                    'Strong organizational and leadership skills',
                    'Experience with academic policy development',
                    'Excellent communication and interpersonal skills',
                    'Understanding of FERPA and academic regulations'
                ],
                'position_type_id': 3
            }
        }
    
    def extract_pds_files(self, pds_directory: str) -> List[Dict]:
        """Extract data from all PDS files in the specified directory"""
        print("📁 Extracting PDS files using ImprovedPDSExtractor...")
        
        pds_files = []
        pds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), pds_directory)
        
        if not os.path.exists(pds_dir):
            print(f"❌ PDS directory not found: {pds_dir}")
            return []
        
        for filename in os.listdir(pds_dir):
            if filename.endswith(('.xlsx', '.xls', '.pdf')):
                file_path = os.path.join(pds_dir, filename)
                print(f"   Processing: {filename}")
                
                try:
                    # Extract PDS data using improved extractor
                    pds_data = self.pds_extractor.extract_pds_data(file_path)
                    
                    if pds_data:
                        # Convert to candidate format for assessment
                        candidate_data = self._convert_pds_to_candidate(pds_data, filename)
                        candidate_data['source_file'] = filename
                        candidate_data['pds_raw_data'] = pds_data
                        pds_files.append(candidate_data)
                        print(f"      ✅ Extracted: {candidate_data.get('name', 'Unknown')}")
                        
                        # Show extraction summary
                        print(f"         Education entries: {candidate_data.get('pds_education_entries', 0)}")
                        print(f"         Experience entries: {candidate_data.get('pds_experience_entries', 0)}")
                        print(f"         Training entries: {candidate_data.get('pds_training_entries', 0)}")
                    else:
                        print(f"      ❌ Failed to extract data from {filename}")
                        
                except Exception as e:
                    print(f"      ❌ Error processing {filename}: {e}")
                    import traceback
                    traceback.print_exc()
        
        print(f"   📊 Total candidates extracted: {len(pds_files)}")
        return pds_files
    
    def _convert_pds_to_candidate(self, pds_data: Dict, filename: str) -> Dict:
        """Convert PDS data to candidate format for assessment"""
        
        # Extract personal information
        personal_info = pds_data.get('personal_info', {})
        name = personal_info.get('name', personal_info.get('full_name', f"Candidate from {filename}"))
        
        # Extract and format education
        education_list = pds_data.get('education', [])
        education_text = self._format_education(education_list)
        
        # Extract and format experience
        experience_list = pds_data.get('experience', [])
        experience_text = self._format_experience(experience_list)
        
        # Extract and format training
        training_list = pds_data.get('training', [])
        training_text = self._format_training(training_list)
        
        # Extract skills and other relevant info
        skills_text = self._extract_skills(pds_data)
        
        # Combine all text for semantic analysis
        full_text = f"""
        Name: {name}
        
        Education Background:
        {education_text}
        
        Work Experience:
        {experience_text}
        
        Training and Professional Development:
        {training_text}
        
        Skills and Qualifications:
        {skills_text}
        
        Additional Information:
        {self._extract_additional_info(pds_data)}
        """
        
        return {
            'id': filename,  # Use filename as ID for testing
            'name': name,
            'extracted_text': full_text.strip(),
            'education': education_text,
            'experience': experience_text,
            'training': training_text,
            'skills': skills_text,
            'email': personal_info.get('email', ''),
            'phone': personal_info.get('phone', ''),
            'pds_education_entries': len(education_list),
            'pds_experience_entries': len(experience_list),
            'pds_training_entries': len(training_list)
        }
    
    def _format_education(self, education_list: List[Dict]) -> str:
        """Format education entries into readable text"""
        if not education_list:
            return "No education information provided"
        
        formatted = []
        for edu in education_list:
            level = edu.get('level', edu.get('education_level', 'Unknown Level'))
            school = edu.get('school', edu.get('institution', 'Unknown Institution'))
            course = edu.get('course', edu.get('degree', ''))
            period_from = str(edu.get('period_from', edu.get('year_from', '')))
            period_to = str(edu.get('period_to', edu.get('year_to', '')))
            honors = edu.get('honors', edu.get('awards', ''))
            
            entry = f"{level.title()}: {school}"
            if course:
                entry += f" - {course}"
            if period_from or period_to:
                entry += f" ({period_from} to {period_to})"
            if honors:
                entry += f" - {honors}"
                
            formatted.append(entry)
        
        return '; '.join(formatted)
    
    def _format_experience(self, experience_list: List[Dict]) -> str:
        """Format work experience entries into readable text"""
        if not experience_list:
            return "No work experience provided"
        
        formatted = []
        for exp in experience_list:
            position = exp.get('position', exp.get('job_title', 'Unknown Position'))
            company = exp.get('company', exp.get('employer', 'Unknown Company'))
            from_date = str(exp.get('from_date', exp.get('start_date', '')))
            to_date = str(exp.get('to_date', exp.get('end_date', '')))
            salary = exp.get('salary', exp.get('compensation', ''))
            status = exp.get('status', exp.get('employment_status', ''))
            
            entry = f"{position} at {company}"
            if from_date or to_date:
                entry += f" ({from_date} to {to_date})"
            if status:
                entry += f" - Status: {status}"
            if salary:
                entry += f" - Salary: {salary}"
                
            formatted.append(entry)
        
        return '; '.join(formatted)
    
    def _format_training(self, training_list: List[Dict]) -> str:
        """Format training and certification entries into readable text"""
        if not training_list:
            return "No training or certifications provided"
        
        formatted = []
        for training in training_list:
            title = training.get('title', training.get('course_title', 'Unknown Training'))
            type_info = training.get('type', training.get('training_type', ''))
            hours = training.get('hours', training.get('duration', ''))
            date_from = str(training.get('date_from', training.get('start_date', '')))
            date_to = str(training.get('date_to', training.get('end_date', '')))
            
            entry = f"{title}"
            if type_info:
                entry += f" ({type_info})"
            if hours:
                entry += f" - {hours} hours"
            if date_from or date_to:
                entry += f" ({date_from} to {date_to})"
                
            formatted.append(entry)
        
        return '; '.join(formatted)
    
    def _extract_skills(self, pds_data: Dict) -> str:
        """Extract and format skills from various PDS sections"""
        skills = []
        
        # From eligibility/licenses
        eligibility = pds_data.get('eligibility', [])
        for elig in eligibility:
            eligibility_name = elig.get('eligibility', elig.get('license', ''))
            if eligibility_name:
                skills.append(f"Licensed: {eligibility_name}")
        
        # From training titles (can indicate skills)
        training = pds_data.get('training', [])
        for train in training:
            title = train.get('title', train.get('course_title', ''))
            if title:
                skills.append(f"Training: {title}")
        
        # From awards
        awards = pds_data.get('awards', [])
        for award in awards:
            award_name = award.get('award', award.get('title', ''))
            if award_name:
                skills.append(f"Award: {award_name}")
        
        return '; '.join(skills) if skills else "No specific skills information provided"
    
    def _extract_additional_info(self, pds_data: Dict) -> str:
        """Extract additional relevant information"""
        additional = []
        
        # Languages
        languages = pds_data.get('languages', [])
        if languages:
            lang_list = [lang.get('language', '') for lang in languages if lang.get('language')]
            if lang_list:
                additional.append(f"Languages: {', '.join(lang_list)}")
        
        # Volunteer work
        volunteer = pds_data.get('volunteer_work', [])
        if volunteer:
            vol_list = [vol.get('organization', '') for vol in volunteer if vol.get('organization')]
            if vol_list:
                additional.append(f"Volunteer Work: {', '.join(vol_list)}")
        
        return '; '.join(additional) if additional else "No additional information"
    
    def run_assessment_comparison(self, candidates: List[Dict], job_posting: Dict) -> Dict:
        """Run both traditional and semantic assessments for comparison"""
        
        print(f"\n🎯 Assessing candidates for: {job_posting['title']}")
        print("=" * 60)
        
        results = {
            'job_posting': job_posting,
            'candidates': [],
            'summary': {
                'total_candidates': len(candidates),
                'semantic_avg': 0,
                'traditional_avg': 0,
                'successful_assessments': 0
            }
        }
        
        semantic_scores = []
        traditional_scores = []
        
        for i, candidate in enumerate(candidates):
            print(f"\n👤 Candidate {i+1}: {candidate['name']}")
            print(f"   Source: {candidate.get('source_file', 'Unknown')}")
            print(f"   PDS Data: {candidate['pds_education_entries']} edu, {candidate['pds_experience_entries']} exp, {candidate['pds_training_entries']} training")
            
            candidate_result = {
                'name': candidate['name'],
                'source_file': candidate.get('source_file', ''),
                'education_entries': candidate.get('pds_education_entries', 0),
                'experience_entries': candidate.get('pds_experience_entries', 0),
                'training_entries': candidate.get('pds_training_entries', 0),
                'semantic_score': None,
                'traditional_score': None,
                'semantic_breakdown': None,
                'traditional_breakdown': None,
                'errors': []
            }
            
            # Run semantic assessment
            try:
                semantic_result = self.enhanced_engine.assess_candidate_enhanced(
                    candidate_data=candidate,
                    job_data=job_posting,
                    assessment_mode='semantic_only'
                )
                
                candidate_result['semantic_score'] = semantic_result.get('semantic_score', 0)
                candidate_result['semantic_breakdown'] = semantic_result.get('semantic_breakdown', {})
                semantic_scores.append(candidate_result['semantic_score'])
                
                print(f"   🧠 Semantic Score: {candidate_result['semantic_score']:.1f}")
                
                # Show semantic breakdown
                breakdown = candidate_result['semantic_breakdown']
                if breakdown:
                    print(f"      Education Relevance: {breakdown.get('education_relevance', 0):.3f}")
                    print(f"      Experience Relevance: {breakdown.get('experience_relevance', 0):.3f}")
                    print(f"      Skills/Training Relevance: {breakdown.get('skills_relevance', 0):.3f}")
                    print(f"      Overall Similarity: {breakdown.get('overall_similarity', 0):.3f}")
                
            except Exception as e:
                error_msg = f"Semantic assessment failed: {e}"
                candidate_result['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
                import traceback
                traceback.print_exc()
            
            # Run traditional assessment comparison
            try:
                # Use the enhanced engine in traditional mode for comparison
                traditional_result = self.enhanced_engine.assess_candidate_enhanced(
                    candidate_data=candidate,
                    job_data=job_posting,
                    assessment_mode='traditional_only'
                )
                
                candidate_result['traditional_score'] = traditional_result.get('traditional_score')
                candidate_result['traditional_breakdown'] = traditional_result.get('traditional_breakdown', {})
                
                if candidate_result['traditional_score'] is not None:
                    traditional_scores.append(candidate_result['traditional_score'])
                    print(f"   🔧 Traditional Score: {candidate_result['traditional_score']:.1f}")
                else:
                    print(f"   🔧 Traditional Score: N/A (requires full database integration)")
                    
            except Exception as e:
                error_msg = f"Traditional assessment failed: {e}"
                candidate_result['errors'].append(error_msg)
                print(f"   ❌ {error_msg}")
            
            results['candidates'].append(candidate_result)
            
            if candidate_result['semantic_score'] is not None:
                results['summary']['successful_assessments'] += 1
        
        # Calculate averages
        if semantic_scores:
            results['summary']['semantic_avg'] = sum(semantic_scores) / len(semantic_scores)
        
        if traditional_scores:
            results['summary']['traditional_avg'] = sum(traditional_scores) / len(traditional_scores)
        
        return results
    
    def print_comparison_summary(self, all_results: List[Dict]):
        """Print comprehensive comparison summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ASSESSMENT COMPARISON SUMMARY")
        print("=" * 80)
        print("🎯 Focus: Education, Experience, and Training Relevance Assessment")
        print("🔄 Comparison: Improved PDS Extraction vs Semantic Understanding")
        
        for result in all_results:
            job_title = result['job_posting']['title']
            summary = result['summary']
            
            print(f"\n🎯 Job: {job_title}")
            print(f"   Candidates Assessed: {summary['total_candidates']}")
            print(f"   Successful Assessments: {summary['successful_assessments']}")
            print(f"   Average Semantic Score: {summary['semantic_avg']:.1f}")
            if summary['traditional_avg'] > 0:
                print(f"   Average Traditional Score: {summary['traditional_avg']:.1f}")
                print(f"   Score Difference: {summary['semantic_avg'] - summary['traditional_avg']:.1f}")
            else:
                print(f"   Traditional Score: Not available")
            
            # Show top candidates by semantic score
            candidates = sorted(result['candidates'], 
                              key=lambda x: x['semantic_score'] or 0, 
                              reverse=True)
            
            print(f"   📈 Top Candidate: {candidates[0]['name']} (Score: {candidates[0]['semantic_score']:.1f})")
            
            # Show most relevant components for top candidate
            best_candidate = candidates[0]
            if best_candidate['semantic_breakdown']:
                breakdown = best_candidate['semantic_breakdown']
                print(f"      🎓 Education Relevance: {breakdown.get('education_relevance', 0):.3f}")
                print(f"      💼 Experience Relevance: {breakdown.get('experience_relevance', 0):.3f}")
                print(f"      🎯 Skills/Training Relevance: {breakdown.get('skills_relevance', 0):.3f}")
        
        print(f"\n✅ Assessment comparison complete!")
        print(f"📊 Semantic scoring successfully evaluated education, experience, and training relevance")
    
    def save_detailed_results(self, all_results: List[Dict], filename: str = None):
        """Save detailed results to JSON file"""
        if filename is None:
            filename = f"real_world_assessment_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Clean up results for JSON serialization
        clean_results = []
        for result in all_results:
            clean_result = {
                'job_posting': {
                    'title': result['job_posting']['title'],
                    'description': result['job_posting']['description'],
                    'requirements': result['job_posting']['requirements']
                },
                'summary': result['summary'],
                'candidates': []
            }
            
            for candidate in result['candidates']:
                clean_candidate = {
                    'name': candidate['name'],
                    'source_file': candidate['source_file'],
                    'pds_entries': {
                        'education': candidate['education_entries'],
                        'experience': candidate['experience_entries'],
                        'training': candidate['training_entries']
                    },
                    'scores': {
                        'semantic': candidate['semantic_score'],
                        'traditional': candidate['traditional_score']
                    },
                    'semantic_breakdown': candidate['semantic_breakdown'],
                    'errors': candidate['errors']
                }
                clean_result['candidates'].append(clean_candidate)
            
            clean_results.append(clean_result)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Detailed results saved: {filename}")

def main():
    """Main test function"""
    print("🚀 Real-World Semantic Scoring Test with Improved PDS Extraction")
    print("=" * 70)
    print("📋 Testing: Education, Experience, and Training Relevance Assessment")
    print("🔄 Comparing: Traditional Assessment vs Semantic Understanding")
    print("📁 Using: ImprovedPDSExtractor for accurate candidate data extraction")
    print("=" * 70)
    
    # Initialize test
    test = RealWorldSemanticTest()
    
    # Extract PDS files using improved extractor
    candidates = test.extract_pds_files('SamplePDSFiles')
    
    if not candidates:
        print("❌ No candidates extracted. Please check the SamplePDSFiles directory.")
        return
    
    # Run assessments for different job types
    all_results = []
    
    # Test with academic position (should favor education and research)
    print("\n" + "="*50)
    print("🎓 TESTING ACADEMIC POSITION")
    print("="*50)
    academic_job = test.job_postings['academic_cs']
    academic_results = test.run_assessment_comparison(candidates, academic_job)
    all_results.append(academic_results)
    
    # Test with engineering position (should favor technical experience)
    print("\n" + "="*50)
    print("⚙️ TESTING ENGINEERING POSITION")
    print("="*50)
    engineering_job = test.job_postings['engineering_faculty']
    engineering_results = test.run_assessment_comparison(candidates, engineering_job)
    all_results.append(engineering_results)
    
    # Test with administrative role (should favor management experience)
    print("\n" + "="*50)
    print("📋 TESTING ADMINISTRATIVE POSITION")
    print("="*50)
    admin_job = test.job_postings['administrative_role']
    admin_results = test.run_assessment_comparison(candidates, admin_job)
    all_results.append(admin_results)
    
    # Print comprehensive summary
    test.print_comparison_summary(all_results)
    
    # Save detailed results
    test.save_detailed_results(all_results)
    
    print(f"\n🎉 Real-world semantic scoring test completed successfully!")
    print(f"📊 Results demonstrate semantic understanding of education, experience, and training")
    print(f"🔄 Comparison shows semantic vs traditional assessment differences")
    print(f"📁 Detailed results saved for further analysis")

if __name__ == "__main__":
    main()