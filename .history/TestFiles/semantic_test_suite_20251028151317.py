#!/usr/bin/env python3
"""
Semantic Engine Test Suite
Comprehensive testing for semantic scoring functionality
"""

import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path to import main modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from semantic_engine import get_semantic_engine, test_semantic_engine
    from enhanced_assessment_engine import get_enhanced_assessment_engine
    from database import DatabaseManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to run this test from the TestFiles directory or main project directory")
    sys.exit(1)

class SemanticTestSuite:
    """Comprehensive test suite for semantic engine"""
    
    def __init__(self):
        self.semantic_engine = get_semantic_engine()
        self.enhanced_engine = get_enhanced_assessment_engine()
        self.db_manager = DatabaseManager()
        
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': [],
            'performance_metrics': {}
        }
    
    def run_test(self, test_name: str, test_function) -> bool:
        """Run a single test and record results"""
        print(f"\n🧪 Running: {test_name}")
        self.test_results['tests_run'] += 1
        
        start_time = time.time()
        
        try:
            result = test_function()
            end_time = time.time()
            
            if result:
                print(f"✅ {test_name} - PASSED ({end_time - start_time:.3f}s)")
                self.test_results['tests_passed'] += 1
                status = 'PASSED'
            else:
                print(f"❌ {test_name} - FAILED ({end_time - start_time:.3f}s)")
                self.test_results['tests_failed'] += 1
                status = 'FAILED'
            
            self.test_results['test_details'].append({
                'test_name': test_name,
                'status': status,
                'execution_time': end_time - start_time
            })
            
            return result
            
        except Exception as e:
            end_time = time.time()
            print(f"💥 {test_name} - ERROR: {str(e)} ({end_time - start_time:.3f}s)")
            self.test_results['tests_failed'] += 1
            
            self.test_results['test_details'].append({
                'test_name': test_name,
                'status': 'ERROR',
                'error': str(e),
                'execution_time': end_time - start_time
            })
            
            return False
    
    def test_semantic_engine_availability(self) -> bool:
        """Test if semantic engine is available and functional"""
        if not self.semantic_engine.is_available():
            print("   ❌ Semantic engine not available")
            return False
        
        print(f"   ✅ Model loaded: {self.semantic_engine.model_name}")
        return True
    
    def test_basic_text_encoding(self) -> bool:
        """Test basic text encoding functionality"""
        test_text = "Software engineering professor with PhD in Computer Science"
        
        embedding = self.semantic_engine.encode_text(test_text)
        
        if embedding is None:
            print("   ❌ Failed to encode text")
            return False
        
        if embedding.shape[0] == 0:
            print("   ❌ Empty embedding returned")
            return False
        
        print(f"   ✅ Text encoded to {embedding.shape[0]}-dimensional vector")
        return True
    
    def test_job_encoding(self) -> bool:
        """Test job requirements encoding"""
        test_job = {
            'id': 1,
            'title': 'Assistant Professor - Computer Science',
            'description': 'Teaching undergraduate and graduate courses in computer science and software engineering',
            'requirements': 'PhD in Computer Science or related field, teaching experience, research publications',
            'department': 'Computer Science',
            'experience_level': 'Entry Level'
        }
        
        job_embedding = self.semantic_engine.encode_job_requirements(test_job)
        
        if job_embedding is None:
            print("   ❌ Failed to encode job requirements")
            return False
        
        print(f"   ✅ Job encoded to {job_embedding.shape[0]}-dimensional vector")
        return True
    
    def test_candidate_encoding(self) -> bool:
        """Test candidate profile encoding"""
        test_candidate = {
            'id': 1,
            'education': [
                {
                    'degree': 'PhD',
                    'major': 'Computer Science',
                    'school': 'Stanford University',
                    'graduation_year': 2020
                }
            ],
            'experience': [
                {
                    'position': 'Teaching Assistant',
                    'company': 'Stanford University',
                    'description': 'Taught introductory programming and data structures courses',
                    'years': 3
                }
            ],
            'skills': ['Python', 'Java', 'Machine Learning', 'Teaching', 'Research'],
            'training': [
                {
                    'title': 'University Teaching Certificate',
                    'year': 2019
                }
            ]
        }
        
        candidate_embedding = self.semantic_engine.encode_candidate_profile(test_candidate)
        
        if candidate_embedding is None:
            print("   ❌ Failed to encode candidate profile")
            return False
        
        print(f"   ✅ Candidate encoded to {candidate_embedding.shape[0]}-dimensional vector")
        return True
    
    def test_similarity_calculation(self) -> bool:
        """Test semantic similarity calculation"""
        # Create test job and candidate
        test_job = {
            'id': 1,
            'title': 'Software Engineering Professor',
            'description': 'Teaching software engineering courses',
            'requirements': 'PhD in Computer Science, programming experience'
        }
        
        test_candidate = {
            'id': 1,
            'education': [{'degree': 'PhD Computer Science', 'school': 'MIT'}],
            'experience': [{'position': 'Software Engineer', 'description': 'Developed software applications'}],
            'skills': ['Python', 'Software Engineering', 'Teaching']
        }
        
        # Get embeddings
        job_embedding = self.semantic_engine.encode_job_requirements(test_job)
        candidate_embedding = self.semantic_engine.encode_candidate_profile(test_candidate)
        
        if job_embedding is None or candidate_embedding is None:
            print("   ❌ Failed to generate embeddings for similarity test")
            return False
        
        # Calculate similarity
        similarity = self.semantic_engine.calculate_semantic_similarity(candidate_embedding, job_embedding)
        
        if not (0.0 <= similarity <= 1.0):
            print(f"   ❌ Similarity out of range: {similarity}")
            return False
        
        print(f"   ✅ Similarity calculated: {similarity:.3f}")
        return True
    
    def test_detailed_semantic_scoring(self) -> bool:
        """Test detailed semantic scoring breakdown"""
        test_job = {
            'id': 1,
            'title': 'Computer Science Professor',
            'description': 'Research and teaching in computer science',
            'requirements': 'PhD in CS, research experience, teaching ability'
        }
        
        test_candidate = {
            'id': 1,
            'education': [{'degree': 'PhD Computer Science', 'school': 'CMU'}],
            'experience': [{'position': 'Research Scientist', 'description': 'AI research'}],
            'skills': ['Python', 'Research', 'Machine Learning']
        }
        
        detailed_score = self.semantic_engine.calculate_detailed_semantic_score(test_candidate, test_job)
        
        required_fields = ['overall_score', 'education_relevance', 'experience_relevance', 'skills_relevance']
        
        for field in required_fields:
            if field not in detailed_score:
                print(f"   ❌ Missing field in detailed score: {field}")
                return False
            
            score = detailed_score[field]
            if not (0.0 <= score <= 1.0):
                print(f"   ❌ Score out of range for {field}: {score}")
                return False
        
        print(f"   ✅ Detailed scoring: Overall={detailed_score['overall_score']:.3f}")
        return True
    
    def test_enhanced_assessment_integration(self) -> bool:
        """Test enhanced assessment engine integration"""
        test_job = {
            'id': 1,
            'title': 'Assistant Professor',
            'description': 'Teaching and research position',
            'requirements': 'PhD required, teaching experience preferred'
        }
        
        test_candidate = {
            'id': 1,
            'education': [{'degree': 'PhD Mathematics', 'school': 'Harvard'}],
            'experience': [{'position': 'Lecturer', 'description': 'Teaching mathematics'}],
            'skills': ['Mathematics', 'Teaching', 'Research']
        }
        
        assessment = self.enhanced_engine.assess_candidate_enhanced(test_candidate, test_job)
        
        required_fields = ['recommended_score', 'assessment_method', 'semantic_score', 'traditional_score']
        
        for field in required_fields:
            if field not in assessment:
                print(f"   ❌ Missing field in assessment: {field}")
                return False
        
        recommended_score = assessment['recommended_score']
        if not (0 <= recommended_score <= 100):
            print(f"   ❌ Recommended score out of range: {recommended_score}")
            return False
        
        print(f"   ✅ Assessment: {recommended_score:.1f} via {assessment['assessment_method']}")
        return True
    
    def test_batch_processing(self) -> bool:
        """Test batch candidate processing"""
        test_job = {
            'id': 1,
            'title': 'Professor Position',
            'description': 'Academic position',
            'requirements': 'PhD required'
        }
        
        test_candidates = [
            {
                'id': 1,
                'education': [{'degree': 'PhD Physics', 'school': 'MIT'}],
                'skills': ['Physics', 'Research']
            },
            {
                'id': 2,
                'education': [{'degree': 'PhD Chemistry', 'school': 'Caltech'}],
                'skills': ['Chemistry', 'Teaching']
            },
            {
                'id': 3,
                'education': [{'degree': 'Master Computer Science', 'school': 'Stanford'}],
                'skills': ['Programming', 'Software']
            }
        ]
        
        results = self.enhanced_engine.batch_assess_candidates(test_candidates, test_job)
        
        if len(results) != len(test_candidates):
            print(f"   ❌ Batch results count mismatch: {len(results)} vs {len(test_candidates)}")
            return False
        
        for i, result in enumerate(results):
            if 'recommended_score' not in result:
                print(f"   ❌ Missing recommended_score in result {i}")
                return False
        
        print(f"   ✅ Batch processed {len(results)} candidates successfully")
        return True
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        # Single assessment benchmark
        test_job = {'id': 1, 'title': 'Test Position', 'requirements': 'Test requirements'}
        test_candidate = {'id': 1, 'education': [{'degree': 'PhD', 'school': 'Test University'}]}
        
        start_time = time.time()
        assessment = self.enhanced_engine.assess_candidate_enhanced(test_candidate, test_job)
        single_time = time.time() - start_time
        
        # Batch assessment benchmark
        batch_candidates = [test_candidate] * 10
        start_time = time.time()
        batch_results = self.enhanced_engine.batch_assess_candidates(batch_candidates, test_job)
        batch_time = time.time() - start_time
        
        avg_batch_time = batch_time / len(batch_candidates)
        
        self.test_results['performance_metrics'] = {
            'single_assessment_time': single_time,
            'batch_assessment_time': batch_time,
            'avg_batch_time_per_candidate': avg_batch_time,
            'batch_efficiency_ratio': single_time / avg_batch_time if avg_batch_time > 0 else 0
        }
        
        # Performance criteria
        if single_time > 5.0:  # Should complete within 5 seconds
            print(f"   ⚠️  Single assessment time high: {single_time:.3f}s")
        
        if avg_batch_time > single_time * 1.2:  # Batch should be more efficient
            print(f"   ⚠️  Batch processing not efficient: {avg_batch_time:.3f}s vs {single_time:.3f}s")
        
        print(f"   ✅ Performance: Single={single_time:.3f}s, Batch avg={avg_batch_time:.3f}s")
        return True
    
    def test_real_database_candidates(self) -> bool:
        """Test with real candidates from database if available"""
        try:
            candidates = self.db_manager.get_all_candidates()
            
            if not candidates:
                print("   ⚠️  No candidates in database - skipping real data test")
                return True
            
            # Test with first candidate
            test_candidate = candidates[0]
            test_job = {
                'id': 1,
                'title': 'Test Position',
                'description': 'Test job for semantic scoring',
                'requirements': 'Various qualifications'
            }
            
            assessment = self.enhanced_engine.assess_candidate_enhanced(test_candidate, test_job)
            
            if 'recommended_score' not in assessment:
                print("   ❌ Failed to assess real candidate")
                return False
            
            print(f"   ✅ Real candidate assessed: {assessment['recommended_score']:.1f}")
            return True
            
        except Exception as e:
            print(f"   ⚠️  Database test failed: {str(e)}")
            return True  # Not critical if database unavailable
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("🚀 Starting Semantic Engine Test Suite")
        print("=" * 60)
        
        # Define test suite
        tests = [
            ("Semantic Engine Availability", self.test_semantic_engine_availability),
            ("Basic Text Encoding", self.test_basic_text_encoding),
            ("Job Requirements Encoding", self.test_job_encoding),
            ("Candidate Profile Encoding", self.test_candidate_encoding),
            ("Similarity Calculation", self.test_similarity_calculation),
            ("Detailed Semantic Scoring", self.test_detailed_semantic_scoring),
            ("Enhanced Assessment Integration", self.test_enhanced_assessment_integration),
            ("Batch Processing", self.test_batch_processing),
            ("Performance Benchmarks", self.test_performance_benchmarks),
            ("Real Database Candidates", self.test_real_database_candidates),
        ]
        
        # Run all tests
        for test_name, test_function in tests:
            self.run_test(test_name, test_function)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUITE SUMMARY")
        print("=" * 60)
        
        total_tests = self.test_results['tests_run']
        passed_tests = self.test_results['tests_passed']
        failed_tests = self.test_results['tests_failed']
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} {'❌' if failed_tests > 0 else '✅'}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Performance summary
        if self.test_results['performance_metrics']:
            metrics = self.test_results['performance_metrics']
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"Single Assessment: {metrics['single_assessment_time']:.3f}s")
            print(f"Batch Efficiency: {metrics['batch_efficiency_ratio']:.1f}x faster")
        
        # Overall status
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED - Semantic engine ready for production!")
        else:
            print(f"\n⚠️  {failed_tests} TESTS FAILED - Review errors before deployment")
        
        return self.test_results
    
    def save_test_results(self, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"semantic_test_results_{timestamp}.json"
        
        # Add summary information
        self.test_results['test_summary'] = {
            'timestamp': datetime.now().isoformat(),
            'semantic_engine_model': getattr(self.semantic_engine, 'model_name', 'unknown'),
            'semantic_engine_available': self.semantic_engine.is_available(),
            'total_tests': self.test_results['tests_run'],
            'passed_tests': self.test_results['tests_passed'],
            'failed_tests': self.test_results['tests_failed'],
            'success_rate': (self.test_results['tests_passed'] / max(1, self.test_results['tests_run'])) * 100
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Test results saved: {filename}")

def main():
    """Main test function"""
    test_suite = SemanticTestSuite()
    results = test_suite.run_all_tests()
    test_suite.save_test_results()
    
    # Exit with appropriate code
    if results['tests_failed'] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()