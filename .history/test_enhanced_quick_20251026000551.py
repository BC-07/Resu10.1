#!/usr/bin/env python3
"""Quick test of enhanced extractor"""

from enhanced_pds_extractor import EnhancedPDSExtractor

def test_enhanced():
    extractor = EnhancedPDSExtractor()
    result = extractor.extract_pds_data('Sample PDS New.xlsx')
    
    if result:
        personal = result.get('personal_info', {})
        print('✅ Enhanced extraction successful')
        print(f'Name: {personal.get("name", "Not found")}')
        print(f'Full Name: {personal.get("full_name", "Not found")}')
        print(f'Phone: {personal.get("phone", "Not found")}')
        print(f'Mobile: {personal.get("mobile_no", "Not found")}')
        print(f'Email: {personal.get("email", "Not found")}')
        
        eligibility = result.get('civil_service_eligibility', [])
        print(f'Civil Service entries: {len(eligibility)}')
        
        # Check for contamination
        clean_entries = 0
        for entry in eligibility:
            if isinstance(entry, dict):
                eligibility_text = entry.get('eligibility', '').lower()
                if any(keyword in eligibility_text for keyword in ['civil service', 'eligibility', 'exam', 'rating', 'board']):
                    clean_entries += 1
        
        contamination_rate = (len(eligibility) - clean_entries) / max(len(eligibility), 1)
        print(f'Eligibility contamination rate: {contamination_rate:.1%}')
        
        references = result.get('other_information', {}).get('references', [])
        print(f'References: {len(references)}')
        
        # Check reference validity
        valid_refs = 0
        for ref in references:
            if isinstance(ref, dict):
                name = ref.get('name', '')
                if len(name.split()) >= 2:
                    valid_refs += 1
        
        print(f'Valid references: {valid_refs}/{len(references)}')
        
        print('\n🔧 Enhancement Summary:')
        print(f'   Personal info extracted: {bool(personal.get("name") or personal.get("full_name"))}')
        print(f'   Contact info extracted: {bool(personal.get("phone") or personal.get("mobile_no"))}')
        print(f'   Eligibility clean rate: {(clean_entries/max(len(eligibility), 1)):.1%}')
        print(f'   Reference validity rate: {(valid_refs/max(len(references), 1)):.1%}')
        
    else:
        print('❌ Enhanced extraction failed')

if __name__ == "__main__":
    test_enhanced()