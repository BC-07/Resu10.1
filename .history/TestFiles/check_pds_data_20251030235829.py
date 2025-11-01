#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
import json

def check_pds_data():
    """Check if candidates have proper PDS data for assessment"""
    
    print("🔍 CHECKING PDS DATA AVAILABILITY")
    print("=" * 40)
    
    db = DatabaseManager()
    candidates = db.get_all_candidates()
    
    if not candidates:
        print("❌ No candidates found")
        return
    
    # Check first few candidates
    for i, candidate in enumerate(candidates[:3]):
        candidate_id = candidate['id']
        full_name = candidate.get('full_name', 'Unknown')
        
        print(f"\n📋 CANDIDATE {i+1}: ID {candidate_id} - {full_name}")
        
        # Check PDS extracted data
        pds_raw = candidate.get('pds_extracted_data')
        if pds_raw:
            print(f"   ✅ Has pds_extracted_data: {type(pds_raw)}")
            print(f"   Data length: {len(str(pds_raw))} chars")
            
            try:
                # Parse PDS data
                if isinstance(pds_raw, str):
                    pds_data = json.loads(pds_raw)
                    print("   ✅ Successfully parsed JSON string")
                elif isinstance(pds_raw, dict):
                    pds_data = pds_raw
                    print("   ✅ Already a dictionary")
                else:
                    print(f"   ❌ Unexpected data type: {type(pds_raw)}")
                    continue
                
                # Check key sections
                if isinstance(pds_data, dict):
                    print("   📊 PDS SECTIONS:")
                    
                    # Educational background
                    edu = pds_data.get('educational_background', {})
                    if edu and isinstance(edu, dict):
                        course = edu.get('course', 'None')
                        school = edu.get('school_name', 'None')
                        print(f"      Education: {course} at {school}")
                    else:
                        print("      Education: Missing or empty")
                    
                    # Work experience
                    exp = pds_data.get('work_experience', [])
                    if exp and isinstance(exp, list) and len(exp) > 0:
                        print(f"      Work Experience: {len(exp)} entries")
                        if exp[0]:
                            first_job = exp[0]
                            position = first_job.get('position_title', 'Unknown')
                            company = first_job.get('company_name', 'Unknown')
                            print(f"        First: {position} at {company}")
                    else:
                        print("      Work Experience: Empty or missing")
                    
                    # Learning & Development
                    training = pds_data.get('learning_development', [])
                    if training and isinstance(training, list) and len(training) > 0:
                        print(f"      Training: {len(training)} entries")
                        if training[0]:
                            first_train = training[0]
                            title = first_train.get('title', 'Unknown')
                            print(f"        First: {title}")
                    else:
                        print("      Training: Empty or missing")
                    
                    # Civil Service Eligibility
                    eligibility = pds_data.get('civil_service_eligibility', [])
                    if eligibility and isinstance(eligibility, list) and len(eligibility) > 0:
                        print(f"      Eligibility: {len(eligibility)} entries")
                    else:
                        print("      Eligibility: Empty or missing")
                
                else:
                    print("   ❌ PDS data is not a dictionary")
            
            except Exception as e:
                print(f"   ❌ Error parsing PDS data: {e}")
        
        else:
            print("   ❌ No pds_extracted_data found")
            
            # Check fallback fields
            education = candidate.get('education', '')
            work_exp = candidate.get('work_experience', '')
            learning_dev = candidate.get('learning_development', '')
            
            print("   📋 FALLBACK DATA:")
            print(f"      Education: {len(education)} chars")
            print(f"      Work Experience: {len(work_exp)} chars") 
            print(f"      Learning Development: {len(learning_dev)} chars")

if __name__ == "__main__":
    check_pds_data()