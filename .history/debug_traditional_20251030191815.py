#!/usr/bin/env python3
"""
Debug traditional assessment scoring
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from assessment_engine import UniversityAssessmentEngine
from database import DatabaseManager
import traceback

def debug_traditional_assessment():
    """Debug why traditional assessment is returning 0"""
    try:
        print("🔍 Debugging Traditional Assessment...")
        
        # Create assessment engine
        db_manager = DatabaseManager()
        assessment_engine = UniversityAssessmentEngine(db_manager)
        
        print("✅ Assessment engine created")
        
        # Get the same data that was used in the test
        candidate_id = 469
        
        # Get candidate data
        candidate_raw = db_manager.get_candidate(candidate_id)
        
        if not candidate_raw:
            print(f"❌ No candidate found with ID {candidate_id}")
            return
            
        print(f"✅ Found candidate: {candidate_raw.get('first_name')} {candidate_raw.get('last_name')}")
        
        # Get PDS data
        pds_candidate = db_manager.get_pds_candidate(candidate_id)
        
        if not pds_candidate or not pds_candidate.get('pds_data'):
            print(f"❌ No PDS data found for candidate {candidate_id}")
            return
            
        pds_data = pds_candidate['pds_data']
        print(f"✅ PDS data found with keys: {list(pds_data.keys())}")
        
        # Get job data from LSPU job postings
        job_id = 2
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM lspu_job_postings WHERE id = %s", (job_id,))
                job_result = cursor.fetchone()
        
        if not job_result:
            print(f"❌ No job found with ID {job_id}")
            return
            
        # Convert to dict if it's a tuple
        if job_result:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'lspu_job_postings'")
            columns = [row[0] for row in cursor.fetchall()]
            job_data = dict(zip(columns, job_result))
        
        print(f"✅ Found job: {job_data.get('position_title')}")
        
        # Test traditional assessment directly
        print(f"\n🧪 Testing assess_candidate_for_lspu_job...")
        result = assessment_engine.assess_candidate_for_lspu_job(pds_data, job_data)
        
        print(f"📊 Assessment result:")
        print(f"  - final_score: {result.get('final_score')}")
        print(f"  - education_score: {result.get('education_score')}")
        print(f"  - experience_score: {result.get('experience_score')}")
        print(f"  - training_score: {result.get('training_score')}")
        print(f"  - eligibility_score: {result.get('eligibility_score')}")
        print(f"  - performance_score: {result.get('performance_score')}")
        print(f"  - potential_score: {result.get('potential_score')}")
        
        # Check educational background specifically
        education_bg = pds_data.get('educational_background', [])
        print(f"\n📚 Educational background ({len(education_bg)} entries):")
        for i, edu in enumerate(education_bg[:3]):  # Show first 3
            print(f"  [{i+1}] Level: {edu.get('level')}, School: {edu.get('school_name')}, Course: {edu.get('course')}")
        
        # Check work experience
        work_exp = pds_data.get('work_experience', [])
        print(f"\n💼 Work experience ({len(work_exp)} entries):")
        for i, exp in enumerate(work_exp[:3]):  # Show first 3
            print(f"  [{i+1}] Position: {exp.get('position_title')}, Company: {exp.get('company')}")
            
        return result
        
    except Exception as e:
        print(f"❌ Error debugging traditional assessment: {e}")
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return None

if __name__ == "__main__":
    debug_traditional_assessment()