#!/usr/bin/env python3
"""
Phase 2 Final Comparison and Analysis
Compare original vs enhanced extraction results
"""

import json
from datetime import datetime
from improved_pds_extractor import ImprovedPDSExtractor
from enhanced_pds_extractor import EnhancedPDSExtractor

def compare_extractors():
    """Compare original vs enhanced extractor performance"""
    
    print("🔍 Phase 2: Final Comparison Analysis")
    print("=" * 50)
    
    # Test file
    test_file = "Sample PDS New.xlsx"
    
    print(f"📁 Testing file: {test_file}")
    print("-" * 30)
    
    # Test original extractor
    print("\n📊 Original Extractor Results:")
    original_extractor = ImprovedPDSExtractor()
    original_result = original_extractor.extract_pds_data(test_file)
    
    original_stats = analyze_extraction_result(original_result, "Original")
    
    # Test enhanced extractor  
    print("\n🔧 Enhanced Extractor Results:")
    enhanced_extractor = EnhancedPDSExtractor()
    enhanced_result = enhanced_extractor.extract_pds_data(test_file)
    
    enhanced_stats = analyze_extraction_result(enhanced_result, "Enhanced")
    
    # Compare results
    print("\n📊 COMPARISON SUMMARY:")
    print("=" * 40)
    
    improvements = {}
    
    # Personal info comparison
    print("\n👤 Personal Information:")
    original_name = original_stats['personal_info']['has_name']
    enhanced_name = enhanced_stats['personal_info']['has_name']
    print(f"   Name extraction: {get_improvement_status(original_name, enhanced_name)}")
    improvements['name_extraction'] = enhanced_name > original_name
    
    original_phone = original_stats['personal_info']['has_phone']
    enhanced_phone = enhanced_stats['personal_info']['has_phone']
    print(f"   Phone extraction: {get_improvement_status(original_phone, enhanced_phone)}")
    improvements['phone_extraction'] = enhanced_phone > original_phone
    
    # Eligibility comparison
    print("\n✅ Civil Service Eligibility:")
    original_contamination = original_stats['eligibility']['contamination_rate']
    enhanced_contamination = enhanced_stats['eligibility']['contamination_rate']
    contamination_improved = enhanced_contamination < original_contamination
    print(f"   Contamination rate: {original_contamination:.1%} → {enhanced_contamination:.1%} {get_improvement_icon(contamination_improved)}")
    improvements['contamination_reduced'] = contamination_improved
    
    # References comparison
    print("\n👥 References:")
    original_ref_validity = original_stats['references']['validity_rate']
    enhanced_ref_validity = enhanced_stats['references']['validity_rate']
    ref_improved = enhanced_ref_validity > original_ref_validity
    print(f"   Validity rate: {original_ref_validity:.1%} → {enhanced_ref_validity:.1%} {get_improvement_icon(ref_improved)}")
    improvements['references_improved'] = ref_improved
    
    # Overall assessment
    total_improvements = sum(improvements.values())
    improvement_percentage = (total_improvements / len(improvements)) * 100
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    print(f"   Improvements made: {total_improvements}/{len(improvements)} areas")
    print(f"   Improvement rate: {improvement_percentage:.0f}%")
    
    if improvement_percentage >= 75:
        print("   Status: ✅ PHASE 2 SUCCESSFUL")
    elif improvement_percentage >= 50:
        print("   Status: ⚠️ PARTIAL SUCCESS - More work needed")
    else:
        print("   Status: ❌ PHASE 2 NEEDS REWORK")
    
    # Generate detailed report
    comparison_report = {
        'comparison_date': datetime.now().isoformat(),
        'test_file': test_file,
        'original_stats': original_stats,
        'enhanced_stats': enhanced_stats,
        'improvements': improvements,
        'improvement_percentage': improvement_percentage,
        'phase2_status': 'successful' if improvement_percentage >= 75 else 'partial' if improvement_percentage >= 50 else 'needs_rework',
        'next_steps': generate_next_steps(improvements, improvement_percentage)
    }
    
    with open('phase2_final_comparison.json', 'w') as f:
        json.dump(comparison_report, f, indent=2)
    
    print(f"\n📁 Detailed report saved: phase2_final_comparison.json")
    
    return comparison_report

def analyze_extraction_result(result, extractor_name):
    """Analyze extraction result quality"""
    
    if not result:
        print(f"❌ {extractor_name} extraction failed")
        return create_empty_stats()
    
    # Personal info analysis
    personal_info = result.get('personal_info', {})
    has_name = bool(personal_info.get('name') or personal_info.get('full_name'))
    has_phone = bool(personal_info.get('phone') or personal_info.get('mobile_no') or personal_info.get('telephone_no'))
    has_email = bool(personal_info.get('email'))
    
    print(f"   👤 Personal Info: Name={has_name}, Phone={has_phone}, Email={has_email}")
    
    # Eligibility analysis
    eligibility = result.get('civil_service_eligibility', [])
    clean_entries = 0
    eligibility_keywords = ['civil service', 'eligibility', 'exam', 'rating', 'board', 'licensure', 'professional']
    
    for entry in eligibility:
        if isinstance(entry, dict):
            eligibility_text = entry.get('eligibility', '').lower()
            if any(keyword in eligibility_text for keyword in eligibility_keywords):
                clean_entries += 1
    
    contamination_rate = (len(eligibility) - clean_entries) / max(len(eligibility), 1)
    print(f"   ✅ Eligibility: {len(eligibility)} entries, {contamination_rate:.1%} contamination")
    
    # References analysis
    references = result.get('other_information', {}).get('references', [])
    valid_refs = 0
    
    for ref in references:
        if isinstance(ref, dict):
            name = ref.get('name', '').strip()
            # Simple validation: at least 2 words, letters only
            if len(name.split()) >= 2 and name.replace(' ', '').replace('.', '').isalpha():
                valid_refs += 1
    
    ref_validity_rate = valid_refs / max(len(references), 1)
    print(f"   👥 References: {len(references)} total, {ref_validity_rate:.1%} valid")
    
    return {
        'personal_info': {
            'has_name': has_name,
            'has_phone': has_phone,
            'has_email': has_email
        },
        'eligibility': {
            'total_entries': len(eligibility),
            'clean_entries': clean_entries,
            'contamination_rate': contamination_rate
        },
        'references': {
            'total_references': len(references),
            'valid_references': valid_refs,
            'validity_rate': ref_validity_rate
        }
    }

def create_empty_stats():
    """Create empty stats for failed extraction"""
    return {
        'personal_info': {'has_name': False, 'has_phone': False, 'has_email': False},
        'eligibility': {'total_entries': 0, 'clean_entries': 0, 'contamination_rate': 1.0},
        'references': {'total_references': 0, 'valid_references': 0, 'validity_rate': 0.0}
    }

def get_improvement_status(original, enhanced):
    """Get improvement status string"""
    if enhanced and not original:
        return "❌ → ✅ FIXED"
    elif enhanced and original:
        return "✅ → ✅ Maintained"
    elif not enhanced and original:
        return "✅ → ❌ BROKEN"
    else:
        return "❌ → ❌ Still broken"

def get_improvement_icon(improved):
    """Get improvement icon"""
    return "✅ IMPROVED" if improved else "❌ No improvement"

def generate_next_steps(improvements, improvement_percentage):
    """Generate next steps based on results"""
    if improvement_percentage >= 75:
        return [
            "Phase 2 successful - ready for Phase 3",
            "Implement semantic relevance scoring system",
            "Train sentence-BERT model with synthetic dataset",
            "Integrate assessment engine with enhanced extractor"
        ]
    elif improvement_percentage >= 50:
        return [
            "Continue Phase 2 refinement",
            "Focus on remaining extraction issues",
            "Improve contamination filtering",
            "Enhance pattern recognition"
        ]
    else:
        return [
            "Rework Phase 2 extraction improvements",
            "Review and fix enhancement patterns",
            "Test with more diverse PDS samples",
            "Consider alternative extraction approaches"
        ]

def main():
    """Run final comparison"""
    comparison_report = compare_extractors()
    
    print("\n🚀 PHASE 2 COMPLETION:")
    if comparison_report['phase2_status'] == 'successful':
        print("✅ Ready to proceed to Phase 3: Semantic Model Development")
    else:
        print("⚠️ Phase 2 needs additional work before Phase 3")
    
    print("\n📋 Next Steps:")
    for step in comparison_report['next_steps']:
        print(f"   • {step}")

if __name__ == "__main__":
    main()