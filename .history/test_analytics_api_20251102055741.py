#!/usr/bin/env python3
"""
Quick test server for analytics API endpoints
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class AnalyticsAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        print(f"📡 Request: {path}")
        
        if path == '/api/analytics/assessment-trends':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'success': True,
                'labels': ['2025-11-02', '2025-11-01', '2025-10-31', '2025-10-30'],
                'scores': [75.0, 72.5, 81.1, 69.8],
                'trends': {
                    'daily_assessments': [
                        {'assessment_date': '2025-11-02', 'total_assessments': 5, 'avg_score': 75.0, 'shortlisted_count': 3},
                        {'assessment_date': '2025-11-01', 'total_assessments': 8, 'avg_score': 72.5, 'shortlisted_count': 4},
                        {'assessment_date': '2025-10-31', 'total_assessments': 6, 'avg_score': 81.1, 'shortlisted_count': 5},
                        {'assessment_date': '2025-10-30', 'total_assessments': 4, 'avg_score': 69.8, 'shortlisted_count': 2}
                    ],
                    'processing_type_trends': [
                        {'processing_type': 'pds', 'count': 15, 'avg_score': 75.0},
                        {'processing_type': 'resume', 'count': 8, 'avg_score': 68.5}
                    ],
                    'period_days': 30,
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            print(f"✅ Sent assessment trends data with labels: {response_data['labels']}")
            
        elif path == '/api/analytics/assessment-insights':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'success': True,
                'insights': {
                    'performance_summary': {
                        'total_candidates': 23,
                        'avg_overall_score': 72.5,
                        'top_performing_category': 'Academic',
                        'period_days': 30
                    },
                    'category_performance': [
                        {'category': 'Academic', 'total_candidates': 12, 'avg_score': 78.2, 'success_count': 8},
                        {'category': 'Administrative', 'total_candidates': 6, 'avg_score': 71.3, 'success_count': 3},
                        {'category': 'Technical', 'total_candidates': 5, 'avg_score': 65.8, 'success_count': 2}
                    ],
                    'quality_distribution': [
                        {'quality_level': 'Excellent', 'count': 3},
                        {'quality_level': 'Very Good', 'count': 8},
                        {'quality_level': 'Good', 'count': 12},
                        {'quality_level': 'Fair', 'count': 0}
                    ],
                    'recommendations': [
                        'Focus on improving candidates in lower-scoring categories',
                        'Continue successful practices from top-performing categories'
                    ],
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            print(f"✅ Sent assessment insights data")
            
        elif path == '/api/test-university-analytics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                'success': True,
                'analytics': {
                    'summary': {
                        'total_candidates': 17,
                        'completed_assessments': 15,
                        'pending_assessments': 2,
                        'avg_overall_score': 75.0,
                        'processing_rate': 88.2
                    }
                }
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            print(f"✅ Sent university analytics data")
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 5000), AnalyticsAPIHandler)
    print("🚀 Analytics API test server running on http://localhost:5000")
    print("📡 Available endpoints:")
    print("   - /api/analytics/assessment-trends")
    print("   - /api/analytics/assessment-insights")
    print("   - /api/test-university-analytics")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")