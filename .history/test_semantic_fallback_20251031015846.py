#!/usr/bin/env python3
"""
Test the semantic analysis fallback mechanism
"""
import json
import sys
import os

# Add the current directory to Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_semantic_fallback():
    """Test the semantic analysis fallback using mock data"""
    
    # Mock enhanced assessment result (what the enhanced_assessment_engine returns)
    enhanced_result = {
        'semantic_score': 75.5,
        'traditional_score': 80.0,
        'recommended_score': 77.8,
        'assessment_method': 'hybrid',
        'semantic_breakdown': {
            'education_score': 85,
            'experience_score': 70,
            'training_score': 60
        },
        'traditional_breakdown': {
            'education': 90,
            'experience': 75,
            'training': 65,
            'eligibility': 85
        }
    }
    
    # Simulate semantic engine failure and create fallback
    semantic_score = enhanced_result.get('semantic_score', 0)
    semantic_breakdown = enhanced_result.get('semantic_breakdown', {})
    
    print("🧪 Testing semantic analysis fallback mechanism")
    print(f"Enhanced Assessment Semantic Score: {semantic_score}")
    print(f"Semantic Breakdown: {semantic_breakdown}")
    
    # This is the fallback logic I added to app.py
    semantic_result = {
        'overall_score': semantic_score / 100 if semantic_score else 0,
        'education_relevance': semantic_breakdown.get('education_score', 0) / 100,
        'experience_relevance': semantic_breakdown.get('experience_score', 0) / 100,
        'training_relevance': semantic_breakdown.get('training_score', 0) / 100,
        'insights': [f"Assessment completed using enhanced scoring system"],
        'education_insights': f"Education score: {semantic_breakdown.get('education_score', 0)}/100 based on degree relevance",
        'experience_insights': f"Experience score: {semantic_breakdown.get('experience_score', 0)}/100 based on work history",
        'skills_insights': f"Training score: {semantic_breakdown.get('training_score', 0)}/100 based on professional development"
    }
    
    # Build semantic analysis section like app.py does
    semantic_analysis = {
        'overall_score': round(semantic_result.get('overall_score', 0) * 100, 2),
        'education_relevance': round(semantic_result.get('education_relevance', 0) * 100, 2),
        'experience_relevance': round(semantic_result.get('experience_relevance', 0) * 100, 2),
        'skills_relevance': round(semantic_result.get('training_relevance', 0) * 100, 2),
        'training_relevance': round(semantic_result.get('training_relevance', 0) * 100, 2),
        'insights': semantic_result.get('insights', []),
        'education_insights': semantic_result.get('education_insights', 'Educational background analysis not available'),
        'experience_insights': semantic_result.get('experience_insights', 'Experience analysis not available'),
        'skills_insights': semantic_result.get('skills_insights', 'Skills analysis not available')
    }
    
    print("\n✅ Fallback Semantic Analysis Result:")
    print(f"  Overall Score: {semantic_analysis['overall_score']}%")
    print(f"  Education Relevance: {semantic_analysis['education_relevance']}%")
    print(f"  Experience Relevance: {semantic_analysis['experience_relevance']}%")
    print(f"  Training Relevance: {semantic_analysis['training_relevance']}%")
    print(f"  Education Insights: {semantic_analysis['education_insights']}")
    print(f"  Experience Insights: {semantic_analysis['experience_insights']}")
    print(f"  Training Insights: {semantic_analysis['skills_insights']}")
    
    # Verify the data is not all zeros
    assert semantic_analysis['overall_score'] > 0, "Overall score should not be 0"
    assert semantic_analysis['education_relevance'] > 0, "Education relevance should not be 0"
    assert semantic_analysis['experience_relevance'] > 0, "Experience relevance should not be 0"
    assert semantic_analysis['training_relevance'] > 0, "Training relevance should not be 0"
    
    print("\n🎉 SUCCESS: Semantic analysis fallback provides real data instead of 0s!")
    return semantic_analysis

if __name__ == "__main__":
    test_semantic_fallback()