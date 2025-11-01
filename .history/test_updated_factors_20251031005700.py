#!/usr/bin/env python3
"""
Test the updated assessment comparison factors
"""

import requests
import json
import time

def test_updated_factors():
    """Test the updated assessment comparison factors"""
    
    time.sleep(2)  # Give server time to be ready
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/candidates/484/assessment/comparison', timeout=10)
        print('=== COMPARISON RESPONSE ===')
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                comparison = data.get('data', {})
                print('\n=== UPDATED FACTORS ===')
                
                traditional = comparison.get('traditional_assessment', {})
                enhanced = comparison.get('enhanced_assessment', {})
                
                print(f'Traditional Method: {traditional.get("method", "N/A")}')
                print(f'Traditional Factors: {traditional.get("factors", [])}')
                print(f'Enhanced Method: {enhanced.get("method", "N/A")}')
                print(f'Enhanced Factors: {enhanced.get("factors", [])}')
                
                print(f'\n=== BREAKDOWN DATA ===')
                print(f'Traditional Keys: {list(traditional.keys())}')
                
                if 'education' in traditional:
                    print(f'Education: {traditional["education"]}')
                    print(f'Experience: {traditional["experience"]}')
                    print(f'Training: {traditional["training"]}')
                    print(f'Eligibility: {traditional["eligibility"]}')
                else:
                    print('❌ Breakdown fields missing')
                    
                print(f'\n=== IMPROVEMENTS ===')
                improvements = comparison.get('improvement_metrics', {})
                advantages = improvements.get('method_advantages', [])
                for i, advantage in enumerate(advantages, 1):
                    print(f'{i}. {advantage}')
                    
            else:
                print(f'API Error: {data}')
        else:
            print(f'HTTP Error: {response.text}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_factors()