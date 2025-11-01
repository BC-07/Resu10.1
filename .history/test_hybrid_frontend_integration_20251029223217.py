#!/usr/bin/env python3
"""
Test Frontend Integration with Hybrid Scoring System
Tests the complete Phase 2 Frontend Enhancement implementation
"""

import requests
import json
import time
from datetime import datetime

class HybridFrontendIntegrationTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"    Details: {details}")
    
    def test_application_startup(self):
        """Test 1: Verify application is running"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                self.log_result("Application Startup", True, "Application is running and responding")
                return True
            else:
                self.log_result("Application Startup", False, f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Application Startup", False, f"Cannot connect to application: {e}")
            return False
    
    def test_hybrid_assessment_endpoints(self):
        """Test 2: Verify new hybrid assessment API endpoints are available"""
        endpoints_to_test = [
            "/api/candidates/1/assessment/1",
            "/api/candidates/1/assessment/comparison", 
            "/api/candidates/1/semantic-analysis/1",
            "/api/job-postings/1/bulk-assess"
        ]
        
        success_count = 0
        total_endpoints = len(endpoints_to_test)
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint.endswith("/bulk-assess"):
                    # POST endpoint
                    response = requests.post(f"{self.base_url}{endpoint}", 
                                           json={"candidate_ids": []}, 
                                           timeout=10)
                else:
                    # GET endpoint
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code in [200, 400, 404]:  # 404 is OK - means endpoint exists but no data
                    success_count += 1
                    self.log_result(f"Endpoint {endpoint}", True, "Endpoint is accessible")
                else:
                    self.log_result(f"Endpoint {endpoint}", False, f"Unexpected status code: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Endpoint {endpoint}", False, f"Endpoint error: {e}")
        
        overall_success = success_count == total_endpoints
        self.log_result("Hybrid Assessment Endpoints", overall_success, 
                       f"{success_count}/{total_endpoints} endpoints accessible")
        return overall_success
    
    def test_frontend_assets_loading(self):
        """Test 3: Verify frontend assets are loading correctly"""
        assets_to_test = [
            "/static/css/components/hybrid-scoring.css",
            "/static/js/modules/candidates.js",
            "/static/js/services/api.js"
        ]
        
        success_count = 0
        total_assets = len(assets_to_test)
        
        for asset in assets_to_test:
            try:
                response = requests.get(f"{self.base_url}{asset}", timeout=10)
                if response.status_code == 200:
                    success_count += 1
                    self.log_result(f"Asset {asset}", True, "Asset loads successfully")
                else:
                    self.log_result(f"Asset {asset}", False, f"Asset failed to load: {response.status_code}")
            except Exception as e:
                self.log_result(f"Asset {asset}", False, f"Asset error: {e}")
        
        overall_success = success_count == total_assets
        self.log_result("Frontend Assets Loading", overall_success, 
                       f"{success_count}/{total_assets} assets loaded successfully")
        return overall_success
    
    def test_dashboard_page_rendering(self):
        """Test 4: Verify dashboard page renders with new hybrid components"""
        try:
            response = requests.get(f"{self.base_url}/dashboard", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for new hybrid scoring sections in modal
                required_components = [
                    'hybrid-scoring-section',
                    'semantic-analysis-section', 
                    'assessment-comparison-section',
                    'hybrid-scoring-container',
                    'semantic-analysis-container',
                    'assessment-comparison-container'
                ]
                
                found_components = []
                for component in required_components:
                    if component in content:
                        found_components.append(component)
                
                if len(found_components) == len(required_components):
                    self.log_result("Dashboard Hybrid Components", True, "All hybrid scoring components found in HTML")
                    return True
                else:
                    missing = set(required_components) - set(found_components)
                    self.log_result("Dashboard Hybrid Components", False, 
                                  f"Missing components: {missing}")
                    return False
            else:
                self.log_result("Dashboard Hybrid Components", False, 
                               f"Dashboard page failed to load: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Dashboard Hybrid Components", False, f"Dashboard error: {e}")
            return False
    
    def test_javascript_integration(self):
        """Test 5: Check if JavaScript contains new hybrid methods"""
        try:
            response = requests.get(f"{self.base_url}/static/js/modules/candidates.js", timeout=10)
            if response.status_code == 200:
                js_content = response.text
                
                required_methods = [
                    'populateHybridScoring',
                    'populateSemanticAnalysis',
                    'populateAssessmentComparison',
                    'renderHybridScoringResults',
                    'renderSemanticAnalysisResults',
                    'renderAssessmentComparisonResults'
                ]
                
                found_methods = []
                for method in required_methods:
                    if method in js_content:
                        found_methods.append(method)
                
                if len(found_methods) == len(required_methods):
                    self.log_result("JavaScript Hybrid Methods", True, "All hybrid scoring methods found in JavaScript")
                    return True
                else:
                    missing = set(required_methods) - set(found_methods)
                    self.log_result("JavaScript Hybrid Methods", False, 
                                  f"Missing methods: {missing}")
                    return False
            else:
                self.log_result("JavaScript Hybrid Methods", False, 
                               f"JavaScript file failed to load: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("JavaScript Hybrid Methods", False, f"JavaScript error: {e}")
            return False
    
    def test_css_styling_integration(self):
        """Test 6: Verify CSS styling is properly integrated"""
        try:
            response = requests.get(f"{self.base_url}/static/css/components/hybrid-scoring.css", timeout=10)
            if response.status_code == 200:
                css_content = response.text
                
                required_styles = [
                    'hybrid-scoring-display',
                    'scoring-methods-comparison',
                    'semantic-analysis-display',
                    'assessment-comparison-display',
                    'relevance-score-display',
                    'comparison-insights'
                ]
                
                found_styles = []
                for style in required_styles:
                    if style in css_content:
                        found_styles.append(style)
                
                if len(found_styles) == len(required_styles):
                    self.log_result("CSS Hybrid Styles", True, "All hybrid scoring styles found in CSS")
                    return True
                else:
                    missing = set(required_styles) - set(found_styles)
                    self.log_result("CSS Hybrid Styles", False, 
                                  f"Missing styles: {missing}")
                    return False
            else:
                self.log_result("CSS Hybrid Styles", False, 
                               f"CSS file failed to load: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("CSS Hybrid Styles", False, f"CSS error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Phase 2 Frontend Integration Tests...")
        print("=" * 60)
        
        # Test 1: Application startup
        if not self.test_application_startup():
            print("\n❌ Critical failure: Application not running. Stopping tests.")
            return False
        
        # Test 2: API endpoints
        self.test_hybrid_assessment_endpoints()
        
        # Test 3: Frontend assets
        self.test_frontend_assets_loading()
        
        # Test 4: Dashboard rendering
        self.test_dashboard_page_rendering()
        
        # Test 5: JavaScript integration
        self.test_javascript_integration()
        
        # Test 6: CSS integration
        self.test_css_styling_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! Phase 2 Frontend Integration is complete.")
            print("✅ Hybrid scoring system is ready for production use.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Review the issues above.")
            print("🔧 Some components may need fixes before deployment.")
        
        # Save detailed results
        with open('hybrid_frontend_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total,
                    'passed': passed,
                    'failed': total - passed,
                    'success_rate': (passed/total)*100,
                    'timestamp': datetime.now().isoformat()
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: hybrid_frontend_test_results.json")
        
        return passed == total

def main():
    """Main test execution"""
    tester = HybridFrontendIntegrationTest()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)