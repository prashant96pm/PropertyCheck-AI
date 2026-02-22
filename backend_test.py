#!/usr/bin/env python3

import requests
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

class PropertyCheckAPITester:
    def __init__(self, base_url="https://prop-intel-5.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        self.access_token = None
        self.user_data = None
        self.property_id = None
        self.document_id = None
        
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log(self, message, test_name=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {test_name}: {message}")

    def run_test(self, name, method, endpoint, expected_status=200, data=None, files=None, params=None):
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        
        self.tests_run += 1
        self.log(f"Testing {name}...", "TEST")
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                if files:
                    # For file uploads, don't set content-type header
                    headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
                    response = requests.post(url, files=files, data=data, headers=headers, cookies=self.session.cookies)
                else:
                    response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASSED - Status: {response.status_code}", "PASS")
                
                # Try to parse JSON response
                try:
                    return True, response.json()
                except:
                    return True, {"message": "Non-JSON response", "status_code": response.status_code}
            else:
                self.log(f"❌ FAILED - Expected {expected_status}, got {response.status_code}", "FAIL")
                self.log(f"Response: {response.text[:200]}", "FAIL")
                self.errors.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:500]
                })
                return False, {}

        except Exception as e:
            self.log(f"❌ FAILED - Error: {str(e)}", "ERROR")
            self.errors.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        self.log("=== TESTING HEALTH ENDPOINTS ===", "SECTION")
        
        # Test root endpoint
        success, _ = self.run_test("Root endpoint", "GET", "/", 200)
        
        # Test health endpoint
        success, _ = self.run_test("Health check", "GET", "/health", 200)
        
        return success

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.log("=== TESTING AUTHENTICATION ===", "SECTION")
        
        # Generate test user data
        test_id = uuid.uuid4().hex[:8]
        test_email = f"test_{test_id}@example.com"
        test_password = "TestPassword123!"
        test_name = f"Test User {test_id}"
        
        # Test user registration
        reg_data = {
            "email": test_email,
            "password": test_password,
            "name": test_name
        }
        
        success, response = self.run_test(
            "User registration",
            "POST",
            "/auth/register",
            200,
            data=reg_data
        )
        
        if success and response.get('access_token'):
            self.access_token = response['access_token']
            self.user_data = response.get('user', {})
            # Set auth header for subsequent requests
            self.session.headers['Authorization'] = f'Bearer {self.access_token}'
            self.log("✅ Registration successful, token obtained", "AUTH")
        
        # Test getting user profile
        if self.access_token:
            success, response = self.run_test(
                "Get user profile",
                "GET", 
                "/auth/me",
                200
            )
        
        # Test logout
        success, _ = self.run_test(
            "User logout",
            "POST",
            "/auth/logout",
            200
        )
        
        # Test login with same credentials
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        success, response = self.run_test(
            "User login",
            "POST",
            "/auth/login",
            200,
            data=login_data
        )
        
        if success and response.get('access_token'):
            self.access_token = response['access_token']
            self.session.headers['Authorization'] = f'Bearer {self.access_token}'
            self.log("✅ Login successful, token refreshed", "AUTH")
        
        return success

    def test_property_endpoints(self):
        """Test property management endpoints"""
        self.log("=== TESTING PROPERTY ENDPOINTS ===", "SECTION")
        
        if not self.access_token:
            self.log("❌ No auth token available for property tests", "ERROR")
            return False
        
        # Create a test property
        property_data = {
            "survey_no": f"TEST{uuid.uuid4().hex[:6]}",
            "khata_no": f"KH{uuid.uuid4().hex[:4]}",
            "state": "Karnataka",
            "district": "Bangalore Urban",
            "taluk": "Anekal",
            "village": "Sarjapur",
            "address": "Test Property Address"
        }
        
        success, response = self.run_test(
            "Create property",
            "POST",
            "/properties",
            200,
            data=property_data
        )
        
        if success and response.get('property_id'):
            self.property_id = response['property_id']
            self.log(f"✅ Property created with ID: {self.property_id}", "PROP")
        
        # Get all properties
        success, response = self.run_test(
            "Get all properties",
            "GET",
            "/properties",
            200
        )
        
        # Get specific property
        if self.property_id:
            success, response = self.run_test(
                "Get specific property",
                "GET",
                f"/properties/{self.property_id}",
                200
            )
        
        return success

    def test_document_endpoints(self):
        """Test document upload and OCR endpoints"""
        self.log("=== TESTING DOCUMENT ENDPOINTS ===", "SECTION")
        
        if not self.property_id:
            self.log("❌ No property ID available for document tests", "ERROR")
            return False
        
        # Create a test text file to simulate document upload
        test_content = """SALE DEED
        
        Survey Number: 123/4
        Owner Name: Test Owner
        Father Name: Test Father
        Registration Date: 2023-01-15
        Registration Number: REG123456
        Property Address: Test Village, Test Taluk, Test District
        """
        
        # Test document upload
        files = {
            'file': ('test_document.txt', test_content, 'text/plain')
        }
        
        upload_data = {
            'property_id': self.property_id,
            'doc_type': 'sale_deed'
        }
        
        success, response = self.run_test(
            "Document upload",
            "POST",
            f"/documents/upload?property_id={self.property_id}&doc_type=sale_deed",
            200,
            files=files
        )
        
        if success and response.get('document_id'):
            self.document_id = response['document_id']
            self.log(f"✅ Document uploaded with ID: {self.document_id}", "DOC")
        
        # Get documents for property
        if self.property_id:
            success, response = self.run_test(
                "Get property documents",
                "GET",
                f"/documents/{self.property_id}",
                200
            )
        
        return success

    def test_analysis_endpoints(self):
        """Test AI analysis endpoints"""
        self.log("=== TESTING ANALYSIS ENDPOINTS ===", "SECTION")
        
        if not self.property_id:
            self.log("❌ No property ID available for analysis tests", "ERROR")
            return False
        
        # Test property analysis
        success, response = self.run_test(
            "Run property analysis",
            "POST",
            f"/analyze/{self.property_id}",
            200
        )
        
        if success:
            self.log("✅ Property analysis completed", "ANALYSIS")
        
        return success

    def test_report_endpoints(self):
        """Test report generation endpoints"""
        self.log("=== TESTING REPORT ENDPOINTS ===", "SECTION")
        
        if not self.property_id:
            self.log("❌ No property ID available for report tests", "ERROR")
            return False
        
        # Get report
        success, response = self.run_test(
            "Get property report",
            "GET",
            f"/reports/{self.property_id}",
            200
        )
        
        # Test PDF download (expect binary response)
        try:
            url = f"{self.api_base}/reports/{self.property_id}/download"
            response = self.session.get(url)
            
            self.tests_run += 1
            if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                self.tests_passed += 1
                self.log("✅ PASSED - PDF report download", "PASS")
                success = True
            else:
                self.log(f"❌ FAILED - PDF download status: {response.status_code}", "FAIL")
                success = False
        except Exception as e:
            self.log(f"❌ FAILED - PDF download error: {e}", "ERROR")
            success = False
        
        return success

    def test_government_records(self):
        """Test government records endpoint"""
        self.log("=== TESTING GOVERNMENT RECORDS ===", "SECTION")
        
        # Test with mock survey number
        success, response = self.run_test(
            "Get government records",
            "GET",
            "/government-records/123456?state=Karnataka",
            200
        )
        
        return success

    def test_dashboard_endpoints(self):
        """Test dashboard statistics"""
        self.log("=== TESTING DASHBOARD ENDPOINTS ===", "SECTION")
        
        if not self.access_token:
            self.log("❌ No auth token available for dashboard tests", "ERROR")
            return False
        
        success, response = self.run_test(
            "Get dashboard stats",
            "GET",
            "/dashboard/stats",
            200
        )
        
        return success

    def test_pricing_endpoints(self):
        """Test pricing endpoints"""
        self.log("=== TESTING PRICING ENDPOINTS ===", "SECTION")
        
        success, response = self.run_test(
            "Get pricing packages",
            "GET",
            "/pricing",
            200
        )
        
        return success

    def run_all_tests(self):
        """Run complete test suite"""
        self.log("🚀 STARTING PROPERTYCHECK AI API TESTS", "START")
        self.log(f"Backend URL: {self.base_url}", "CONFIG")
        
        try:
            # Run test suites in order
            test_results = []
            
            test_results.append(("Health Check", self.test_health_check()))
            test_results.append(("Authentication", self.test_auth_endpoints()))
            test_results.append(("Properties", self.test_property_endpoints()))
            test_results.append(("Documents", self.test_document_endpoints()))
            test_results.append(("Analysis", self.test_analysis_endpoints()))
            test_results.append(("Reports", self.test_report_endpoints()))
            test_results.append(("Government Records", self.test_government_records()))
            test_results.append(("Dashboard", self.test_dashboard_endpoints()))
            test_results.append(("Pricing", self.test_pricing_endpoints()))
            
            # Print summary
            self.log("", "")
            self.log("=" * 60, "SUMMARY")
            self.log("TEST SUITE SUMMARY", "SUMMARY")
            self.log("=" * 60, "SUMMARY")
            
            for test_name, passed in test_results:
                status = "✅ PASSED" if passed else "❌ FAILED"
                self.log(f"{test_name:<20} {status}", "SUMMARY")
            
            self.log("", "")
            self.log(f"Total Tests: {self.tests_run}", "SUMMARY")
            self.log(f"Passed: {self.tests_passed}", "SUMMARY")
            self.log(f"Failed: {self.tests_run - self.tests_passed}", "SUMMARY")
            self.log(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%", "SUMMARY")
            
            # Print errors if any
            if self.errors:
                self.log("", "")
                self.log("FAILED TESTS DETAILS:", "ERRORS")
                for i, error in enumerate(self.errors, 1):
                    self.log(f"{i}. {error.get('test', 'Unknown')}", "ERRORS")
                    if 'error' in error:
                        self.log(f"   Error: {error['error']}", "ERRORS")
                    else:
                        self.log(f"   Expected: {error.get('expected')}, Got: {error.get('actual')}", "ERRORS")
                        if error.get('response'):
                            self.log(f"   Response: {error['response'][:200]}...", "ERRORS")
            
            return self.tests_passed == self.tests_run
            
        except Exception as e:
            self.log(f"❌ CRITICAL ERROR: {e}", "CRITICAL")
            return False

def main():
    """Main test execution"""
    tester = PropertyCheckAPITester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)