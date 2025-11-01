#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
import json
import ast

def fix_missing_education_in_pds():
    """Fix missing educational_background in PDS data by using fallback education data"""
    
    print("🔧 FIXING MISSING EDUCATION IN PDS DATA")
    print("=" * 50)
    
    db = DatabaseManager()
    candidates = db.get_all_candidates()
    
    fixed_count = 0
    
    for candidate in candidates:
        candidate_id = candidate['id']
        full_name = candidate.get('full_name', 'Unknown')
        
        print(f"\n📋 Processing Candidate {candidate_id} - {full_name}")
        
        # Get PDS data
        pds_raw = candidate.get('pds_extracted_data')
        if not pds_raw:
            print("   ❌ No PDS data")
            continue
        
        # Parse PDS data
        try:
            if isinstance(pds_raw, str):
                pds_data = json.loads(pds_raw)
            else:
                pds_data = pds_raw
        except:
            print("   ❌ Failed to parse PDS data")
            continue
        
        # Check if educational_background is missing or empty
        edu_bg = pds_data.get('educational_background', {})
        
        # Handle both dict and list formats
        has_education = False
        if isinstance(edu_bg, dict):
            has_education = edu_bg.get('course') and edu_bg.get('school_name')
        elif isinstance(edu_bg, list):
            has_education = len(edu_bg) > 0 and any(
                item.get('course') or item.get('school_name') 
                for item in edu_bg if isinstance(item, dict)
            )
        
        if has_education:
            print("   ✅ Educational background already exists")
            continue
        
        # Get fallback education data
        education = candidate.get('education', '')
        if not education:
            print("   ❌ No fallback education data")
            continue
        
        try:
            # Parse education data (it's stored as a string representation of a list)
            if isinstance(education, str):
                education_list = ast.literal_eval(education)
            else:
                education_list = education
            
            if not isinstance(education_list, list) or len(education_list) == 0:
                print("   ❌ Invalid education data format")
                continue
            
            # Find highest education level
            college_edu = None
            high_school_edu = None
            
            for edu_item in education_list:
                if isinstance(edu_item, dict):
                    level = edu_item.get('level', '').lower()
                    if level == 'college' and edu_item.get('degree_course'):
                        college_edu = edu_item
                    elif level == 'secondary' and not college_edu:
                        high_school_edu = edu_item
            
            # Use college education if available, otherwise high school
            best_edu = college_edu or high_school_edu
            
            if best_edu:
                # Create educational_background from the best education entry
                educational_background = {
                    'course': best_edu.get('degree_course', 'Not specified'),
                    'school_name': best_edu.get('school', 'Not specified'),
                    'year_graduated': best_edu.get('year_graduated', 'Not specified'),
                    'level': best_edu.get('level', 'college')
                }
                
                # Update PDS data
                pds_data['educational_background'] = educational_background
                
                print(f"   ✅ Added education: {educational_background['course']} from {educational_background['school_name']}")
                
                # Save updated PDS data back to database
                try:
                    with db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE candidates 
                            SET pds_extracted_data = %s 
                            WHERE id = %s
                        """, (json.dumps(pds_data), candidate_id))
                        conn.commit()
                    
                    fixed_count += 1
                    print("   ✅ Updated in database")
                    
                except Exception as e:
                    print(f"   ❌ Database update failed: {e}")
            
            else:
                print("   ❌ No usable education data found")
        
        except Exception as e:
            print(f"   ❌ Error processing education data: {e}")
    
    print(f"\n🎉 SUMMARY: Fixed {fixed_count} candidates")
    return fixed_count

if __name__ == "__main__":
    fix_missing_education_in_pds()