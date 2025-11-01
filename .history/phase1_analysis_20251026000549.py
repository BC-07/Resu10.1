#!/usr/bin/env python3
"""
Phase 1: Comprehensive Analysis of Current System
- Analyze existing sentence-BERT model
- Analyze synthetic dataset
- Test current PDS extraction issues
- Generate recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
import os
import json
from utils import SemanticAnalyzer, PersonalDataSheetProcessor
from improved_pds_extractor import ImprovedPDSExtractor

class Phase1Analyzer:
    """Comprehensive analysis for semantic relevance system planning"""
    
    def __init__(self):
        self.results = {}
        print("🔍 Phase 1: Current System Analysis")
        print("=" * 50)
    
    def analyze_current_sentence_bert(self):
        """Analyze the existing sentence-BERT implementation"""
        print("\n📊 1. Current Sentence-BERT Model Analysis")
        print("-" * 40)
        
        try:
            # Test current semantic analyzer
            analyzer = SemanticAnalyzer()
            
            # Check model status
            has_sentence_model = analyzer.sentence_model is not None
            print(f"✅ Sentence-BERT Model Status: {'LOADED' if has_sentence_model else 'DISABLED'}")
            
            if not has_sentence_model:
                print("❌ Current sentence-BERT model is DISABLED")
                print("📝 Model was set to None in utils.py (line 60)")
                print("🔍 Intended model: 'all-MiniLM-L6-v2' (commented out)")
                print("📊 Assessment: GENERIC MODEL - not domain-specific for education")
                
                # Test if we can load the model
                try:
                    from sentence_transformers import SentenceTransformer
                    test_model = SentenceTransformer('all-MiniLM-L6-v2')
                    print("✅ all-MiniLM-L6-v2 can be loaded successfully")
                    
                    # Test basic functionality
                    test_texts = [
                        "Taught mathematics to undergraduate students",
                        "Instructor position in mathematics department", 
                        "Software developer at tech company"
                    ]
                    embeddings = test_model.encode(test_texts)
                    print(f"✅ Model produces embeddings: {embeddings.shape}")
                    
                    # Test similarity for education relevance
                    from sklearn.metrics.pairwise import cosine_similarity
                    sim_matrix = cosine_similarity(embeddings)
                    education_sim = sim_matrix[0][1]  # Teaching vs Instructor
                    non_education_sim = sim_matrix[0][2]  # Teaching vs Software dev
                    
                    print(f"📊 Teaching-Instructor similarity: {education_sim:.3f}")
                    print(f"📊 Teaching-Software Dev similarity: {non_education_sim:.3f}")
                    
                    if education_sim > non_education_sim:
                        print("✅ Model shows basic education domain awareness")
                    else:
                        print("⚠️ Model may not distinguish education context well")
                        
                except Exception as e:
                    print(f"❌ Cannot load model: {e}")
            
            self.results['sentence_bert'] = {
                'status': 'disabled',
                'intended_model': 'all-MiniLM-L6-v2',
                'domain_specific': False,
                'recommendation': 'Enable and fine-tune for education domain'
            }
            
        except Exception as e:
            print(f"❌ Error analyzing sentence-BERT: {e}")
            self.results['sentence_bert'] = {'error': str(e)}
    
    def analyze_synthetic_dataset(self):
        """Analyze the synthetic teaching dataset"""
        print("\n📊 2. Synthetic Dataset Analysis")
        print("-" * 40)
        
        try:
            # Load dataset
            df = pd.read_csv('synthetic_teaching_dataset_highquality.csv')
            print(f"✅ Dataset loaded: {len(df)} total entries")
            
            # Basic statistics
            print(f"📊 Columns: {list(df.columns)}")
            print(f"📊 Job titles: {df['job_title'].nunique()} unique positions")
            print(f"📊 Entry types: {df['type'].value_counts().to_dict()}")
            
            # Job title distribution
            job_counts = df['job_title'].value_counts()
            print(f"\n📈 Job Title Distribution:")
            for job, count in job_counts.items():
                print(f"   {job}: {count} entries")
            
            # Relevance score analysis
            print(f"\n📊 Relevance Score Statistics:")
            print(f"   Range: {df['relevance'].min():.2f} - {df['relevance'].max():.2f}")
            print(f"   Mean: {df['relevance'].mean():.3f}")
            print(f"   Std: {df['relevance'].std():.3f}")
            
            # Type vs relevance analysis
            print(f"\n📊 Type vs Relevance Analysis:")
            type_relevance = df.groupby('type')['relevance'].agg(['mean', 'std', 'count'])
            print(type_relevance)
            
            # High relevance entries analysis
            high_relevance = df[df['relevance'] >= 0.4]
            print(f"\n🎯 High Relevance Entries (≥0.4): {len(high_relevance)} entries")
            print("   Top patterns:")
            for i, (_, row) in enumerate(high_relevance.head(5).iterrows()):
                print(f"   {i+1}. {row['text'][:60]}... (Score: {row['relevance']:.2f})")
            
            # Low relevance entries analysis
            zero_relevance = df[df['relevance'] == 0.0]
            print(f"\n❌ Zero Relevance Entries: {len(zero_relevance)} entries")
            if len(zero_relevance) > 0:
                print("   Common patterns:")
                for i, (_, row) in enumerate(zero_relevance.head(3).iterrows()):
                    print(f"   {i+1}. {row['text'][:60]}...")
            
            # Text length analysis
            df['text_length'] = df['text'].str.len()
            print(f"\n📝 Text Length Analysis:")
            print(f"   Average length: {df['text_length'].mean():.1f} characters")
            print(f"   Range: {df['text_length'].min()} - {df['text_length'].max()} characters")
            
            # Keywords analysis for different job levels
            print(f"\n🔍 Keyword Analysis by Job Level:")
            for job_title in df['job_title'].unique():
                job_data = df[df['job_title'] == job_title]
                high_rel_texts = job_data[job_data['relevance'] >= 0.4]['text'].str.lower()
                
                # Extract common words
                words = []
                for text in high_rel_texts:
                    words.extend(text.split())
                
                common_words = Counter(words).most_common(5)
                print(f"   {job_title}: {[word for word, count in common_words]}")
            
            self.results['dataset'] = {
                'total_entries': len(df),
                'job_titles': list(job_counts.index),
                'job_distribution': job_counts.to_dict(),
                'relevance_stats': {
                    'min': df['relevance'].min(),
                    'max': df['relevance'].max(),
                    'mean': df['relevance'].mean(),
                    'std': df['relevance'].std()
                },
                'high_relevance_count': len(high_relevance),
                'zero_relevance_count': len(zero_relevance),
                'avg_text_length': df['text_length'].mean()
            }
            
        except Exception as e:
            print(f"❌ Error analyzing dataset: {e}")
            self.results['dataset'] = {'error': str(e)}
    
    def test_extraction_issues(self):
        """Test current PDS extraction to identify issues"""
        print("\n📊 3. PDS Extraction Issue Analysis")
        print("-" * 40)
        
        test_files = [
            "Sample PDS New.xlsx",
            "PDS-Sample Cabael.xlsx"
        ]
        
        extraction_results = []
        
        for filename in test_files:
            if os.path.exists(filename):
                print(f"\n🔍 Testing: {filename}")
                
                try:
                    # Test ImprovedPDSExtractor
                    extractor = ImprovedPDSExtractor()
                    result = extractor.extract_pds_data(filename)
                    
                    if result:
                        print(f"✅ Extraction successful")
                        print(f"📊 Sections extracted: {list(result.keys())}")
                        
                        # Analyze personal info extraction
                        personal_info = result.get('personal_info', {})
                        print(f"👤 Personal Info:")
                        print(f"   Name: {personal_info.get('name', 'NOT EXTRACTED')}")
                        print(f"   Email: {personal_info.get('email', 'NOT EXTRACTED')}")
                        print(f"   Phone: {personal_info.get('phone', 'NOT EXTRACTED')}")
                        
                        # Analyze section quality
                        education = result.get('educational_background', [])
                        work_exp = result.get('work_experience', [])
                        eligibility = result.get('civil_service_eligibility', [])
                        
                        print(f"🎓 Education entries: {len(education)}")
                        print(f"💼 Work experience entries: {len(work_exp)}")
                        print(f"✅ Civil service eligibility: {len(eligibility)}")
                        
                        # Check for contamination issues
                        contamination_issues = []
                        
                        # Check if work experience has eligibility data
                        for exp in work_exp:
                            if isinstance(exp, dict):
                                exp_text = str(exp).lower()
                                if any(keyword in exp_text for keyword in ['eligibility', 'civil service', 'prc license']):
                                    contamination_issues.append("Work experience contains eligibility data")
                                    break
                        
                        # Check if eligibility has work experience data
                        for elig in eligibility:
                            if isinstance(elig, dict):
                                elig_text = str(elig).lower()
                                if any(keyword in elig_text for keyword in ['company', 'position', 'salary', 'supervisor']):
                                    contamination_issues.append("Eligibility contains work experience data")
                                    break
                        
                        if contamination_issues:
                            print(f"⚠️ Contamination Issues Found:")
                            for issue in contamination_issues:
                                print(f"   - {issue}")
                        else:
                            print(f"✅ No obvious section contamination detected")
                        
                        extraction_results.append({
                            'filename': filename,
                            'success': True,
                            'sections': len(result),
                            'personal_info_quality': len([x for x in [personal_info.get('name'), personal_info.get('email'), personal_info.get('phone')] if x]),
                            'education_count': len(education),
                            'work_exp_count': len(work_exp),
                            'eligibility_count': len(eligibility),
                            'contamination_issues': contamination_issues
                        })
                        
                    else:
                        print(f"❌ Extraction failed - no result returned")
                        extraction_results.append({
                            'filename': filename,
                            'success': False,
                            'error': 'No result returned'
                        })
                        
                except Exception as e:
                    print(f"❌ Extraction error: {e}")
                    extraction_results.append({
                        'filename': filename,
                        'success': False,
                        'error': str(e)
                    })
            else:
                print(f"⚠️ File not found: {filename}")
        
        self.results['extraction'] = extraction_results
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("\n🎯 4. Recommendations & Implementation Plan")
        print("-" * 40)
        
        recommendations = []
        
        # Sentence-BERT recommendations
        if self.results.get('sentence_bert', {}).get('status') == 'disabled':
            recommendations.append({
                'category': 'Semantic Model',
                'priority': 'HIGH',
                'issue': 'Sentence-BERT model is disabled',
                'recommendation': 'Enable and fine-tune all-MiniLM-L6-v2 for education domain',
                'implementation': 'Create education-specific fine-tuning pipeline using synthetic dataset'
            })
        
        # Dataset recommendations
        dataset_info = self.results.get('dataset', {})
        if dataset_info.get('total_entries', 0) > 1000:
            recommendations.append({
                'category': 'Training Data',
                'priority': 'MEDIUM',
                'issue': 'Good dataset size but need to verify quality',
                'recommendation': 'Use dataset for fine-tuning with data augmentation',
                'implementation': 'Create training pipeline with proper train/val/test splits'
            })
        
        # Extraction recommendations
        extraction_results = self.results.get('extraction', [])
        contamination_found = any(
            result.get('contamination_issues', []) 
            for result in extraction_results if result.get('success', False)
        )
        
        if contamination_found:
            recommendations.append({
                'category': 'Extraction Quality',
                'priority': 'HIGH',
                'issue': 'Section contamination detected',
                'recommendation': 'Implement section-specific validation rules',
                'implementation': 'Add post-processing filters and validation logic'
            })
        
        personal_info_issues = any(
            result.get('personal_info_quality', 0) < 2
            for result in extraction_results if result.get('success', False)
        )
        
        if personal_info_issues:
            recommendations.append({
                'category': 'Personal Info Extraction',
                'priority': 'HIGH',
                'issue': 'Incomplete personal information extraction',
                'recommendation': 'Improve name, email, phone extraction patterns',
                'implementation': 'Enhance regex patterns and add fallback extraction methods'
            })
        
        print("📋 Prioritized Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['category']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Solution: {rec['recommendation']}")
            print(f"   Implementation: {rec['implementation']}")
        
        self.results['recommendations'] = recommendations
    
    def save_analysis_report(self):
        """Save comprehensive analysis report"""
        print("\n💾 5. Saving Analysis Report")
        print("-" * 40)
        
        # Save detailed JSON report
        with open('phase1_analysis_report.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print("✅ Detailed report saved: phase1_analysis_report.json")
        
        # Create summary report
        summary = {
            'analysis_date': str(pd.Timestamp.now()),
            'current_sentence_bert_status': self.results.get('sentence_bert', {}).get('status', 'unknown'),
            'dataset_size': self.results.get('dataset', {}).get('total_entries', 0),
            'extraction_success_rate': len([r for r in self.results.get('extraction', []) if r.get('success', False)]) / max(len(self.results.get('extraction', [])), 1),
            'priority_recommendations': len([r for r in self.results.get('recommendations', []) if r.get('priority') == 'HIGH']),
            'ready_for_phase2': True
        }
        
        with open('phase1_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("✅ Summary report saved: phase1_summary.json")
        print(f"📊 Analysis complete - {len(self.results.get('recommendations', []))} recommendations generated")

def main():
    """Run Phase 1 analysis"""
    analyzer = Phase1Analyzer()
    
    # Run all analysis components
    analyzer.analyze_current_sentence_bert()
    analyzer.analyze_synthetic_dataset()
    analyzer.test_extraction_issues()
    analyzer.generate_recommendations()
    analyzer.save_analysis_report()
    
    print(f"\n{'=' * 50}")
    print("🎉 Phase 1 Analysis Complete!")
    print("📁 Reports generated:")
    print("   - phase1_analysis_report.json (detailed)")
    print("   - phase1_summary.json (summary)")
    print("✅ Ready for Phase 2: Extraction Refinement")

if __name__ == "__main__":
    main()