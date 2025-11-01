#!/usr/bin/env python3
"""
Enhanced Assessment Engine for ResuAI
Integrates semantic scoring with traditional assessment methods
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Import existing assessment engine
from assessment_engine import UniversityAssessmentEngine

# Import semantic engine
from semantic_engine import get_semantic_engine

logger = logging.getLogger(__name__)

class EnhancedUniversityAssessmentEngine(UniversityAssessmentEngine):
    """
    Enhanced assessment engine that combines traditional and semantic scoring
    Provides dual scoring system with semantic relevance as default
    """
    
    def __init__(self, db_manager=None):
        """Initialize enhanced assessment engine"""
        # Initialize database manager if not provided
        if db_manager is None:
            from database import DatabaseManager
            db_manager = DatabaseManager()
        
        super().__init__(db_manager)
        self.semantic_engine = get_semantic_engine()
        
        # Semantic scoring weights (updated for PDS structure and university criteria)
        self.semantic_weights = {
            'education_relevance': 0.35,    # Matches university education emphasis
            'experience_relevance': 0.45,   # Strong weight for experience relevance  
            'training_relevance': 0.15,     # Replaces skills - uses learning_development
            'overall_quality_bonus': 0.05   # Small bonus for overall job fit
        }
        
        # University criteria weights (from official scoring sheet)
        self.university_weights = {
            'potential': 0.10,      # Interview + Written Exam (manually entered)
            'education': 0.30,      # Education background
            'experience': 0.05,     # Experience/Outstanding Accomplishment  
            'training': 0.05,       # Training programs
            'eligibility': 0.10,    # Civil Service Eligibility
            'performance': 0.40     # Performance ratings (manually entered)
        }
        
        # Performance tracking
        self.assessment_stats = {
            'total_assessments': 0,
            'semantic_assessments': 0,
            'traditional_assessments': 0,
            'fallback_to_traditional': 0
        }
    
    def assess_candidate_enhanced(self, candidate_data: Dict, job_data: Dict, 
                                 include_semantic: bool = True, 
                                 include_traditional: bool = True) -> Dict:
        """
        Enhanced candidate assessment with dual scoring system
        
        Args:
            candidate_data: Candidate information
            job_data: Job requirements
            include_semantic: Whether to calculate semantic scores
            include_traditional: Whether to calculate traditional scores
            
        Returns:
            Dictionary with both semantic and traditional assessment results
        """
        assessment_start = datetime.now()
        
        # Initialize result structure
        result = {
            'candidate_id': candidate_data.get('id'),
            'job_id': job_data.get('id'),
            'assessment_timestamp': assessment_start.isoformat(),
            'semantic_score': None,
            'traditional_score': None,
            'recommended_score': None,  # The score to use for ranking
            'assessment_method': 'hybrid',
            'semantic_breakdown': {},
            'traditional_breakdown': {},
            'performance_metrics': {},
            'errors': []
        }
        
        # Calculate semantic scores (default method)
        if include_semantic and self.semantic_engine.is_available():
            try:
                semantic_result = self._calculate_semantic_assessment(candidate_data, job_data)
                result['semantic_score'] = semantic_result['final_score']
                result['semantic_breakdown'] = semantic_result['breakdown']
                result['recommended_score'] = semantic_result['final_score']
                result['assessment_method'] = 'semantic'
                
                self.assessment_stats['semantic_assessments'] += 1
                
            except Exception as e:
                error_msg = f"Semantic assessment failed: {str(e)}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
                
                # Fallback to traditional if semantic fails
                if include_traditional:
                    include_traditional = True
                    result['assessment_method'] = 'traditional_fallback'
                    self.assessment_stats['fallback_to_traditional'] += 1
        
        # Calculate traditional scores (for comparison or fallback)
        if include_traditional:
            try:
                traditional_result = self.assess_candidate(candidate_data, job_data)
                result['traditional_score'] = traditional_result.get('final_score', 0)
                result['traditional_breakdown'] = {
                    'education_score': traditional_result.get('education_score', 0),
                    'experience_score': traditional_result.get('experience_score', 0),
                    'training_score': traditional_result.get('training_score', 0),
                    'eligibility_score': traditional_result.get('eligibility_score', 0),
                    'accomplishments_score': traditional_result.get('accomplishments_score', 0)
                }
                
                # Use traditional as recommended if semantic not available
                if result['recommended_score'] is None:
                    result['recommended_score'] = traditional_result.get('final_score', 0)
                    result['assessment_method'] = 'traditional'
                
                self.assessment_stats['traditional_assessments'] += 1
                
            except Exception as e:
                error_msg = f"Traditional assessment failed: {str(e)}"
                result['errors'].append(error_msg)
                logger.error(error_msg)
        
        # Calculate performance metrics
        assessment_end = datetime.now()
        assessment_time = (assessment_end - assessment_start).total_seconds()
        
        result['performance_metrics'] = {
            'assessment_time_seconds': round(assessment_time, 3),
            'semantic_available': self.semantic_engine.is_available(),
            'model_used': getattr(self.semantic_engine, 'model_name', 'N/A')
        }
        
        # Ensure we have a recommended score
        if result['recommended_score'] is None:
            result['recommended_score'] = 0
            result['assessment_method'] = 'failed'
            result['errors'].append("No assessment method succeeded")
        
        self.assessment_stats['total_assessments'] += 1
        
        return result
    
    def _calculate_semantic_assessment(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """
        Calculate semantic assessment scores with detailed breakdown
        
        Args:
            candidate_data: Candidate information
            job_data: Job requirements
            
        Returns:
            Dictionary with semantic scores and breakdown
        """
        # Get detailed semantic scores
        semantic_details = self.semantic_engine.calculate_detailed_semantic_score(
            candidate_data, job_data
        )
        
        if 'error' in semantic_details:
            raise Exception(semantic_details['error'])
        
        # Extract component scores
        education_relevance = semantic_details.get('education_relevance', 0.0)
        experience_relevance = semantic_details.get('experience_relevance', 0.0)
        training_relevance = semantic_details.get('training_relevance', 0.0)
        overall_score = semantic_details.get('overall_score', 0.0)
        
        # Calculate weighted semantic score
        weighted_score = (
            education_relevance * self.semantic_weights['education_relevance'] +
            experience_relevance * self.semantic_weights['experience_relevance'] +
            training_relevance * self.semantic_weights['training_relevance']
        )
        
        # Apply overall quality bonus
        quality_bonus = overall_score * self.semantic_weights['overall_quality_bonus']
        
        # Final semantic score (scale to 0-100)
        final_semantic_score = (weighted_score + quality_bonus) * 100
        final_semantic_score = max(0, min(100, final_semantic_score))  # Clamp to 0-100
        
        # Create detailed breakdown
        breakdown = {
            'education_relevance': round(education_relevance, 3),
            'experience_relevance': round(experience_relevance, 3),
            'training_relevance': round(training_relevance, 3),
            'overall_similarity': round(overall_score, 3),
            'weighted_components': {
                'education_weighted': round(education_relevance * self.semantic_weights['education_relevance'], 3),
                'experience_weighted': round(experience_relevance * self.semantic_weights['experience_relevance'], 3),
                'training_weighted': round(training_relevance * self.semantic_weights['training_relevance'], 3),
                'quality_bonus': round(quality_bonus, 3)
            },
            'final_calculation': {
                'base_weighted_score': round(weighted_score, 3),
                'quality_bonus': round(quality_bonus, 3),
                'final_score_0_1': round((weighted_score + quality_bonus), 3),
                'final_score_0_100': round(final_semantic_score, 1)
            },
            'weights_used': self.semantic_weights.copy(),
            'model_info': {
                'model_name': semantic_details.get('model_used', 'unknown'),
                'similarity_threshold': semantic_details.get('similarity_threshold', 0.3)
            }
        }
        
        return {
            'final_score': round(final_semantic_score, 1),
            'breakdown': breakdown
        }
    
    def batch_assess_candidates(self, candidates_data: List[Dict], job_data: Dict, 
                              include_semantic: bool = True) -> List[Dict]:
        """
        Assess multiple candidates efficiently
        
        Args:
            candidates_data: List of candidate dictionaries
            job_data: Job requirements
            include_semantic: Whether to use semantic scoring
            
        Returns:
            List of assessment results
        """
        logger.info(f"Starting batch assessment of {len(candidates_data)} candidates")
        
        results = []
        
        # Pre-compute job embedding for efficiency
        if include_semantic and self.semantic_engine.is_available():
            try:
                job_embedding = self.semantic_engine.encode_job_requirements(job_data)
                logger.info("Job embedding pre-computed for batch processing")
            except Exception as e:
                logger.warning(f"Failed to pre-compute job embedding: {e}")
                job_embedding = None
        else:
            job_embedding = None
        
        # Process candidates
        for i, candidate_data in enumerate(candidates_data):
            try:
                assessment = self.assess_candidate_enhanced(
                    candidate_data, job_data, 
                    include_semantic=include_semantic,
                    include_traditional=True
                )
                results.append(assessment)
                
                # Log progress for large batches
                if len(candidates_data) > 20 and (i + 1) % 10 == 0:
                    logger.info(f"Assessed {i + 1}/{len(candidates_data)} candidates")
                    
            except Exception as e:
                error_result = {
                    'candidate_id': candidate_data.get('id', f'unknown_{i}'),
                    'job_id': job_data.get('id'),
                    'recommended_score': 0,
                    'assessment_method': 'failed',
                    'errors': [f"Assessment failed: {str(e)}"]
                }
                results.append(error_result)
                logger.error(f"Failed to assess candidate {candidate_data.get('id', i)}: {e}")
        
        logger.info(f"Batch assessment completed: {len(results)} results")
        return results
    
    def get_assessment_statistics(self) -> Dict:
        """Get assessment engine performance statistics"""
        return {
            'assessment_stats': self.assessment_stats.copy(),
            'semantic_engine_available': self.semantic_engine.is_available(),
            'semantic_model': getattr(self.semantic_engine, 'model_name', 'N/A'),
            'semantic_weights': self.semantic_weights.copy()
        }
    
    def update_semantic_weights(self, new_weights: Dict):
        """Update semantic scoring weights"""
        # Validate weights
        required_keys = ['education_relevance', 'experience_relevance', 'skills_relevance', 'overall_quality_bonus']
        
        for key in required_keys:
            if key not in new_weights:
                raise ValueError(f"Missing required weight: {key}")
        
        # Check if weights sum to reasonable total (allowing for bonus)
        total_weight = sum(new_weights[key] for key in required_keys[:3])  # Exclude bonus
        if total_weight < 0.8 or total_weight > 1.2:
            logger.warning(f"Semantic weights sum to {total_weight}, expected ~1.0")
        
        self.semantic_weights.update(new_weights)
        logger.info(f"Updated semantic weights: {self.semantic_weights}")
    
    def compare_scoring_methods(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """
        Compare semantic vs traditional scoring for analysis
        
        Args:
            candidate_data: Candidate information
            job_data: Job requirements
            
        Returns:
            Comparison analysis dictionary
        """
        # Get both assessments
        assessment = self.assess_candidate_enhanced(
            candidate_data, job_data,
            include_semantic=True,
            include_traditional=True
        )
        
        semantic_score = assessment.get('semantic_score', 0)
        traditional_score = assessment.get('traditional_score', 0)
        
        # Calculate comparison metrics
        score_difference = semantic_score - traditional_score
        relative_difference = (score_difference / max(traditional_score, 1)) * 100
        
        # Categorize the difference
        if abs(score_difference) < 5:
            difference_category = "similar"
        elif score_difference > 10:
            difference_category = "semantic_higher"
        elif score_difference < -10:
            difference_category = "traditional_higher"
        else:
            difference_category = "moderate_difference"
        
        return {
            'candidate_id': candidate_data.get('id'),
            'job_id': job_data.get('id'),
            'semantic_score': semantic_score,
            'traditional_score': traditional_score,
            'score_difference': round(score_difference, 1),
            'relative_difference_percent': round(relative_difference, 1),
            'difference_category': difference_category,
            'semantic_breakdown': assessment.get('semantic_breakdown', {}),
            'traditional_breakdown': assessment.get('traditional_breakdown', {}),
            'assessment_time': assessment.get('performance_metrics', {}).get('assessment_time_seconds', 0)
        }

# Global enhanced assessment engine instance
_enhanced_engine = None

def get_enhanced_assessment_engine() -> EnhancedUniversityAssessmentEngine:
    """Get global enhanced assessment engine instance"""
    global _enhanced_engine
    if _enhanced_engine is None:
        _enhanced_engine = EnhancedUniversityAssessmentEngine()
    return _enhanced_engine

# Convenience functions for compatibility
def assess_candidate_with_semantic(candidate_data: Dict, job_data: Dict) -> Dict:
    """Assess candidate using enhanced engine with semantic scoring"""
    engine = get_enhanced_assessment_engine()
    return engine.assess_candidate_enhanced(candidate_data, job_data)

def assess_candidates_batch(candidates_data: List[Dict], job_data: Dict) -> List[Dict]:
    """Batch assess candidates using enhanced engine"""
    engine = get_enhanced_assessment_engine()
    return engine.batch_assess_candidates(candidates_data, job_data)

if __name__ == "__main__":
    # Test enhanced assessment engine
    print("🧪 Testing Enhanced Assessment Engine...")
    
    engine = get_enhanced_assessment_engine()
    
    # Test data
    test_job = {
        'id': 1,
        'title': 'Assistant Professor - Computer Science',
        'description': 'Teaching undergraduate and graduate courses in computer science',
        'requirements': 'PhD in Computer Science, teaching experience, research publications',
        'department': 'Computer Science',
        'experience_level': 'Entry Level'
    }
    
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
                'description': 'Taught introductory programming courses',
                'years': 2
            }
        ],
        'skills': ['Python', 'Machine Learning', 'Research', 'Teaching'],
        'training': [
            {
                'title': 'Pedagogy Training Certificate',
                'year': 2019
            }
        ]
    }
    
    # Test enhanced assessment
    result = engine.assess_candidate_enhanced(test_candidate, test_job)
    
    print(f"✅ Assessment completed:")
    print(f"   Recommended Score: {result['recommended_score']}")
    print(f"   Assessment Method: {result['assessment_method']}")
    print(f"   Semantic Score: {result['semantic_score']}")
    print(f"   Traditional Score: {result['traditional_score']}")
    print(f"   Assessment Time: {result['performance_metrics']['assessment_time_seconds']}s")
    
    if result['errors']:
        print(f"   Errors: {result['errors']}")
    
    # Test comparison
    comparison = engine.compare_scoring_methods(test_candidate, test_job)
    print(f"\n📊 Scoring Comparison:")
    print(f"   Score Difference: {comparison['score_difference']}")
    print(f"   Difference Category: {comparison['difference_category']}")
    
    # Test statistics
    stats = engine.get_assessment_statistics()
    print(f"\n📈 Engine Statistics: {stats}")
    
    print("\n✅ Enhanced Assessment Engine test completed!")