#!/usr/bin/env python3
"""
PDS Data Structure Diagnostic
Shows the raw extracted data structure to understand what's being extracted
"""

import os
import sys
import json

# Import required modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from improved_pds_extractor import ImprovedPDSExtractor
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

def diagnose_pds_extraction():
    """Diagnose what the PDS extractor is actually extracting"""
    print("🔍 PDS Data Structure Diagnostic")
    print("=" * 50)
    
    extractor = ImprovedPDSExtractor()
    pds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SamplePDSFiles')
    
    if not os.path.exists(pds_dir):
        print(f"❌ PDS directory not found: {pds_dir}")
        return
    
    for filename in os.listdir(pds_dir):
        if filename.endswith(('.xlsx', '.xls')):  # Focus on Excel files first
            file_path = os.path.join(pds_dir, filename)
            print(f"\n📁 Analyzing: {filename}")
            print("-" * 40)
            
            try:
                # Extract raw PDS data
                pds_data = extractor.extract_pds_data(file_path)
                
                if pds_data:
                    print("✅ Raw PDS Data Structure:")
                    
                    # Show top-level keys
                    print(f"📋 Top-level sections: {list(pds_data.keys())}")
                    
                    # Examine each section
                    for section, data in pds_data.items():
                        if isinstance(data, dict):
                            print(f"\n📂 {section.upper()} (dict):")
                            for key, value in data.items():
                                value_preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                                print(f"   {key}: {value_preview}")
                        
                        elif isinstance(data, list):
                            print(f"\n📂 {section.upper()} (list with {len(data)} items):")
                            if data:
                                for i, item in enumerate(data[:3]):  # Show first 3 items
                                    print(f"   Item {i+1}: {item}")
                                if len(data) > 3:
                                    print(f"   ... and {len(data) - 3} more items")
                            else:
                                print("   (empty list)")
                        
                        else:
                            value_preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
                            print(f"\n📂 {section.upper()}: {value_preview}")
                    
                    # Save full data for detailed analysis
                    debug_filename = f"pds_debug_{filename.replace('.xlsx', '.json')}"
                    with open(debug_filename, 'w', encoding='utf-8') as f:
                        json.dump(pds_data, f, indent=2, ensure_ascii=False, default=str)
                    print(f"\n💾 Full data saved to: {debug_filename}")
                    
                else:
                    print("❌ No data extracted")
                    
                # Check if there are any errors
                if hasattr(extractor, 'errors') and extractor.errors:
                    print(f"\n⚠️  Extraction Errors:")
                    for error in extractor.errors:
                        print(f"   - {error}")
                
                if hasattr(extractor, 'warnings') and extractor.warnings:
                    print(f"\n⚠️  Extraction Warnings:")
                    for warning in extractor.warnings:
                        print(f"   - {warning}")
                        
            except Exception as e:
                print(f"❌ Error analyzing {filename}: {e}")
                import traceback
                traceback.print_exc()

def main():
    """Main diagnostic function"""
    print("🔍 PDS EXTRACTOR DIAGNOSTIC TOOL")
    print("🎯 Goal: Understand what data is being extracted from PDS files")
    print("📊 This will show the raw data structure and identify missing sections")
    print("=" * 70)
    
    diagnose_pds_extraction()
    
    print(f"\n✅ Diagnostic complete!")
    print(f"📋 Check the generated JSON files for detailed data structure analysis")

if __name__ == "__main__":
    main()