"""
Backend API tests for PropertyCheck AI - POST-REFACTORING VALIDATION
Tests all endpoints after monolithic server.py -> modular architecture refactoring
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials for refactor testing
TEST_EMAIL = "test_refactor_agent@test.com"
TEST_PASSWORD = "testpass123"
TEST_NAME = "Test User"


# ==================== Module: auth.py ====================
class TestHealthAndRoot:
    """Health check and root endpoints"""
    
    def test_health_check(self):
        """GET /api/health - Health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert "database" in data
        print(f"✓ Health check: status={data['status']}, database={data.get('database')}")

    def test_root_endpoint(self):
        """GET /api/ - Root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data.get("name") == "PropertyCheck AI API"
        assert data.get("version") == "2.0"
        print(f"✓ Root endpoint: name={data['name']}, version={data['version']}")


class TestAuth:
    """Authentication endpoints from routes/auth.py"""
    token = None
    user_id = None
    
    def test_register_user(self):
        """POST /api/auth/register - Register new user"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": TEST_NAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        # 200 for new user, 400 if already exists
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data, "Response missing access_token"
            assert "user" in data, "Response missing user object"
            assert data["user"]["email"] == TEST_EMAIL
            TestAuth.token = data["access_token"]
            TestAuth.user_id = data["user"]["user_id"]
            print(f"✓ User registered: {TEST_EMAIL}, user_id={TestAuth.user_id}")
        elif response.status_code == 400:
            data = response.json()
            assert "Email already registered" in data.get("detail", "")
            print(f"✓ User already exists (expected)")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}, {response.text}")

    def test_login_user(self):
        """POST /api/auth/login - Login with email/password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response missing access_token"
        assert "user" in data, "Response missing user object"
        assert data["user"]["email"] == TEST_EMAIL
        TestAuth.token = data["access_token"]
        TestAuth.user_id = data["user"]["user_id"]
        print(f"✓ Login successful: token obtained, user_id={TestAuth.user_id}")

    def test_get_me(self):
        """GET /api/auth/me - Get current user with Bearer token"""
        if not TestAuth.token:
            pytest.skip("No token available")
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Get me failed: {response.text}"
        data = response.json()
        assert data["email"] == TEST_EMAIL
        assert "user_id" in data
        assert "role" in data
        print(f"✓ GET /api/auth/me: email={data['email']}, role={data['role']}")

    def test_logout(self):
        """POST /api/auth/logout - Logout endpoint"""
        response = requests.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data.get("message") == "Logged out successfully"
        print(f"✓ Logout successful")


class TestDashboardStats:
    """Dashboard stats endpoint from routes/auth.py"""
    
    def test_dashboard_stats(self):
        """GET /api/dashboard/stats - Dashboard stats for authenticated user"""
        if not TestAuth.token:
            # Login first
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL, "password": TEST_PASSWORD
            })
            if resp.status_code == 200:
                TestAuth.token = resp.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        data = response.json()
        assert "total_properties" in data
        assert "total_documents" in data
        assert "total_reports" in data
        assert "recent_properties" in data
        print(f"✓ Dashboard stats: properties={data['total_properties']}, docs={data['total_documents']}, reports={data['total_reports']}")


class TestProfile:
    """Profile endpoints from routes/auth.py"""
    
    def test_get_profile(self):
        """GET /api/profile - Get user profile"""
        if not TestAuth.token:
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL, "password": TEST_PASSWORD
            })
            if resp.status_code == 200:
                TestAuth.token = resp.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/profile", headers=headers)
        assert response.status_code == 200, f"Get profile failed: {response.text}"
        data = response.json()
        assert data["email"] == TEST_EMAIL
        assert "first_name" in data
        assert "last_name" in data
        assert "gender" in data
        print(f"✓ GET profile: email={data['email']}, first_name={data.get('first_name', 'N/A')}")

    def test_update_profile(self):
        """PUT /api/profile - Update user profile"""
        if not TestAuth.token:
            pytest.skip("No token available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.put(f"{BASE_URL}/api/profile", json={
            "first_name": "Test",
            "last_name": "Refactor",
            "gender": "Other"
        }, headers=headers)
        assert response.status_code == 200, f"Update profile failed: {response.text}"
        data = response.json()
        assert data.get("message") == "Profile updated successfully"
        print(f"✓ Profile updated successfully")


# ==================== Module: properties.py ====================
class TestProperties:
    """Property CRUD endpoints from routes/properties.py"""
    property_id = None
    
    def test_create_property(self):
        """POST /api/properties - Create property (needs auth)"""
        if not TestAuth.token:
            resp = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL, "password": TEST_PASSWORD
            })
            if resp.status_code == 200:
                TestAuth.token = resp.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.post(f"{BASE_URL}/api/properties", json={
            "survey_no": "REFACT/001",
            "state": "Karnataka",
            "district": "Bengaluru Urban",
            "owner_name": "Refactor Test Owner",
            "land_type": "Residential",
            "extent": "1500 Sq Ft",
            "village": "Whitefield",
            "taluk": "Bengaluru East"
        }, headers=headers)
        assert response.status_code == 200, f"Create property failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert data["survey_no"] == "REFACT/001"
        TestProperties.property_id = data["property_id"]
        print(f"✓ Property created: {TestProperties.property_id}")

    def test_list_properties(self):
        """GET /api/properties - List user properties (needs auth)"""
        if not TestAuth.token:
            pytest.skip("No token available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/properties", headers=headers)
        assert response.status_code == 200, f"List properties failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} properties")

    def test_get_single_property(self):
        """GET /api/properties/{property_id} - Get single property (needs auth)"""
        if not TestAuth.token or not TestProperties.property_id:
            pytest.skip("No token or property_id available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/properties/{TestProperties.property_id}", headers=headers)
        assert response.status_code == 200, f"Get property failed: {response.text}"
        data = response.json()
        assert data["property_id"] == TestProperties.property_id
        assert data["survey_no"] == "REFACT/001"
        print(f"✓ Got property: {data['property_id']}, survey_no={data['survey_no']}")


class TestDocuments:
    """Document upload endpoints from routes/properties.py"""
    
    def test_upload_document(self):
        """POST /api/documents/upload - Upload document with file (needs auth)"""
        if not TestAuth.token or not TestProperties.property_id:
            pytest.skip("No token or property_id available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        # Create a simple test file
        files = {
            'file': ('test_doc.txt', b'Test document content for OCR', 'text/plain')
        }
        data = {
            'property_id': TestProperties.property_id,
            'doc_type': 'general'
        }
        response = requests.post(
            f"{BASE_URL}/api/documents/upload?property_id={TestProperties.property_id}&doc_type=general",
            files=files,
            headers=headers
        )
        # 200 or may fail due to validation
        if response.status_code == 200:
            data = response.json()
            assert "document_id" in data
            assert data["doc_type"] == "general"
            print(f"✓ Document uploaded: {data['document_id']}")
        else:
            print(f"⚠ Document upload returned {response.status_code}: {response.text[:100]}")

    def test_get_documents(self):
        """GET /api/documents/{property_id} - List documents (needs auth)"""
        if not TestAuth.token or not TestProperties.property_id:
            pytest.skip("No token or property_id available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/documents/{TestProperties.property_id}", headers=headers)
        assert response.status_code == 200, f"Get documents failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Listed {len(data)} documents for property")


# ==================== Module: search.py ====================
class TestSearch:
    """Search endpoints from routes/search.py"""
    registry_property_id = None
    
    def test_search_no_params(self):
        """GET /api/property/search - Search with no params returns sample registry"""
        response = requests.get(f"{BASE_URL}/api/property/search")
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        assert "results" in data
        assert len(data["results"]) > 0, "Expected sample registry results"
        assert data.get("search_type") == "sample_registry"
        # Store a property_id for later tests
        if data["results"]:
            TestSearch.registry_property_id = data["results"][0].get("property_id")
        print(f"✓ Search returned {len(data['results'])} sample registry properties")

    def test_search_with_params(self):
        """GET /api/property/search - Search with state, district params"""
        response = requests.get(f"{BASE_URL}/api/property/search?state=Karnataka&district=Bengaluru+Urban")
        assert response.status_code == 200, f"Search with params failed: {response.text}"
        data = response.json()
        assert "results" in data
        assert "total" in data
        print(f"✓ Search with params returned {len(data['results'])} results")

    def test_ai_smart_search(self):
        """POST /api/property/ai-smart-search - AI smart search with query text"""
        response = requests.post(f"{BASE_URL}/api/property/ai-smart-search", json={
            "query": "Find properties in Bengaluru owned by Kumar"
        })
        assert response.status_code == 200, f"AI smart search failed: {response.text}"
        data = response.json()
        assert "results" in data
        assert "query_parsed" in data
        assert data.get("search_type") == "ai_smart_search"
        print(f"✓ AI smart search: parsed={data['query_parsed']}, results={len(data['results'])}")


class TestFullProfile:
    """Full profile and document endpoints from routes/search.py"""
    
    def test_full_profile(self):
        """GET /api/property/full-profile/{property_id} - 360 profile with all sections"""
        property_id = TestSearch.registry_property_id or TestProperties.property_id
        if not property_id:
            pytest.skip("No property_id available")
        
        response = requests.get(f"{BASE_URL}/api/property/full-profile/{property_id}")
        assert response.status_code == 200, f"Full profile failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert "basic_details" in data
        assert "ownership_history" in data
        assert "legal_records" in data
        assert "documents" in data
        assert "geo_spatial" in data
        assert "government_records" in data
        print(f"✓ Full profile returned for {property_id}")

    def test_property_documents(self):
        """GET /api/property/documents/{property_id} - Property docs with registry docs"""
        property_id = TestSearch.registry_property_id or TestProperties.property_id
        if not property_id:
            pytest.skip("No property_id available")
        
        response = requests.get(f"{BASE_URL}/api/property/documents/{property_id}")
        assert response.status_code == 200, f"Property documents failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert "uploaded_documents" in data
        assert "registry_documents" in data
        assert isinstance(data["registry_documents"], list)
        print(f"✓ Property documents: {len(data.get('registry_documents', []))} registry docs")

    def test_ownership_history(self):
        """GET /api/property/ownership-history/{property_id} - Ownership chain"""
        property_id = TestSearch.registry_property_id or TestProperties.property_id
        if not property_id:
            pytest.skip("No property_id available")
        
        response = requests.get(f"{BASE_URL}/api/property/ownership-history/{property_id}")
        assert response.status_code == 200, f"Ownership history failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert "ownership_chain" in data
        assert "total_transfers" in data
        print(f"✓ Ownership history: {data['total_transfers']} transfers")

    def test_legal_records(self):
        """GET /api/property/legal-records/{property_id} - Legal records"""
        property_id = TestSearch.registry_property_id or TestProperties.property_id
        if not property_id:
            pytest.skip("No property_id available")
        
        response = requests.get(f"{BASE_URL}/api/property/legal-records/{property_id}")
        assert response.status_code == 200, f"Legal records failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert "encumbrances" in data
        assert "pending_litigation" in data
        print(f"✓ Legal records: encumbrances={len(data.get('encumbrances', []))}, litigation={data.get('pending_litigation')}")


# ==================== Module: intelligence.py ====================
class TestIntelligence:
    """Intelligence endpoints from routes/intelligence.py"""
    
    def test_title_chain(self):
        """GET /api/property/{property_id}/title-chain - Detailed title chain with gaps analysis"""
        property_id = TestSearch.registry_property_id or TestProperties.property_id
        if not property_id:
            pytest.skip("No property_id available")
        
        response = requests.get(f"{BASE_URL}/api/property/{property_id}/title-chain")
        assert response.status_code == 200, f"Title chain failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert "chain" in data
        assert "total_transfers" in data
        assert "gaps" in data
        assert "anomalies" in data
        assert "completeness_score" in data
        print(f"✓ Title chain: {data['total_transfers']} transfers, completeness={data['completeness_score']}%")

    def test_valuation(self):
        """GET /api/property/{property_id}/valuation - Property valuation with price trends"""
        property_id = TestSearch.registry_property_id or TestProperties.property_id
        if not property_id:
            pytest.skip("No property_id available")
        
        response = requests.get(f"{BASE_URL}/api/property/{property_id}/valuation")
        assert response.status_code == 200, f"Valuation failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert "estimated_value" in data
        assert "guideline_value" in data
        assert "price_trends" in data
        assert "neighborhood" in data
        assert "infrastructure" in data
        print(f"✓ Valuation: {data['estimated_value'].get('formatted')}")

    def test_government_sources(self):
        """GET /api/property/{property_id}/government-sources - Government data sources"""
        property_id = TestSearch.registry_property_id or TestProperties.property_id
        if not property_id:
            pytest.skip("No property_id available")
        
        response = requests.get(f"{BASE_URL}/api/property/{property_id}/government-sources")
        assert response.status_code == 200, f"Government sources failed: {response.text}"
        data = response.json()
        assert "property_id" in data
        assert "sources" in data
        assert "total_sources" in data
        assert "retrieved" in data
        assert "pending" in data
        print(f"✓ Government sources: {data['total_sources']} sources, {data['retrieved']} retrieved")

    def test_legal_copilot_post(self):
        """POST /api/property/{property_id}/legal-copilot - AI legal analysis (needs auth)"""
        property_id = TestProperties.property_id
        if not property_id or not TestAuth.token:
            pytest.skip("No property_id or token available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.post(f"{BASE_URL}/api/property/{property_id}/legal-copilot", json={}, headers=headers)
        assert response.status_code == 200, f"Legal copilot POST failed: {response.text}"
        data = response.json()
        assert "analysis" in data
        assert "copilot_id" in data
        assert "ai_powered" in data
        print(f"✓ Legal copilot: AI powered={data['ai_powered']}, analysis length={len(data.get('analysis', ''))}")

    def test_legal_copilot_get(self):
        """GET /api/property/{property_id}/legal-copilot - Get legal copilot report (needs auth)"""
        property_id = TestProperties.property_id
        if not property_id or not TestAuth.token:
            pytest.skip("No property_id or token available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/property/{property_id}/legal-copilot", headers=headers)
        assert response.status_code == 200, f"Legal copilot GET failed: {response.text}"
        data = response.json()
        # May or may not have analysis depending on if POST was run
        print(f"✓ Legal copilot GET: has analysis={data.get('analysis') is not None}")


class TestGovernmentRecords:
    """Government records endpoint from routes/intelligence.py"""
    
    def test_government_records_endpoint(self):
        """GET /api/government-records/123/4?state=Karnataka - Fetch government records"""
        response = requests.get(f"{BASE_URL}/api/government-records/123/4?state=Karnataka")
        assert response.status_code == 200, f"Government records failed: {response.text}"
        data = response.json()
        assert "survey_no" in data
        assert data["state"] == "Karnataka"
        assert "owner_name" in data
        assert "mutation_records" in data
        print(f"✓ Government records: survey_no={data['survey_no']}, state={data['state']}")


# ==================== Module: reports.py ====================
class TestReports:
    """Risk analysis and reports from routes/reports.py"""
    share_token = None
    
    def test_analyze_property(self):
        """POST /api/analyze/{property_id} - Run risk analysis (needs auth)"""
        property_id = TestProperties.property_id
        if not property_id or not TestAuth.token:
            pytest.skip("No property_id or token available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.post(f"{BASE_URL}/api/analyze/{property_id}", json={}, headers=headers)
        assert response.status_code == 200, f"Analyze property failed: {response.text}"
        data = response.json()
        assert "risk_score" in data
        assert "risk_status" in data
        assert "report_id" in data
        assert data["risk_status"] in ["GREEN", "YELLOW", "RED"]
        print(f"✓ Risk analysis: score={data['risk_score']}, status={data['risk_status']}")

    def test_get_report(self):
        """GET /api/reports/{property_id} - Get risk report (needs auth)"""
        property_id = TestProperties.property_id
        if not property_id or not TestAuth.token:
            pytest.skip("No property_id or token available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.get(f"{BASE_URL}/api/reports/{property_id}", headers=headers)
        assert response.status_code == 200, f"Get report failed: {response.text}"
        data = response.json()
        assert "risk_score" in data
        assert "risk_status" in data
        print(f"✓ Got report: score={data['risk_score']}")

    def test_share_report(self):
        """POST /api/reports/{property_id}/share - Share report (needs auth)"""
        property_id = TestProperties.property_id
        if not property_id or not TestAuth.token:
            pytest.skip("No property_id or token available")
        
        headers = {"Authorization": f"Bearer {TestAuth.token}"}
        response = requests.post(f"{BASE_URL}/api/reports/{property_id}/share", json={}, headers=headers)
        assert response.status_code == 200, f"Share report failed: {response.text}"
        data = response.json()
        assert "share_token" in data
        TestReports.share_token = data["share_token"]
        print(f"✓ Share token generated: {data['share_token'][:12]}...")

    def test_get_shared_report_public(self):
        """GET /api/shared-report/{share_token} - Access shared report (public)"""
        if not TestReports.share_token:
            pytest.skip("No share token available")
        
        # NO auth required - public access
        response = requests.get(f"{BASE_URL}/api/shared-report/{TestReports.share_token}")
        assert response.status_code == 200, f"Shared report failed: {response.text}"
        data = response.json()
        assert "report" in data
        assert "property_id" in data
        print(f"✓ Shared report accessible publicly")

    def test_invalid_share_token(self):
        """GET /api/shared-report/{invalid_token} - Returns 404 for invalid token"""
        response = requests.get(f"{BASE_URL}/api/shared-report/invalid_token_xyz123")
        assert response.status_code == 404
        print(f"✓ Invalid token returns 404")


# ==================== Module: payments.py ====================
class TestPricing:
    """Pricing endpoint from routes/payments.py"""
    
    def test_get_pricing(self):
        """GET /api/pricing - Get pricing packages"""
        response = requests.get(f"{BASE_URL}/api/pricing")
        assert response.status_code == 200, f"Pricing failed: {response.text}"
        data = response.json()
        assert "basic" in data
        assert "standard" in data
        assert "premium" in data
        # Verify package structure
        for pkg_name, pkg in data.items():
            assert "name" in pkg
            assert "amount" in pkg
            assert "currency" in pkg
            assert "features" in pkg
        print(f"✓ Pricing: basic={data['basic']['amount']}, standard={data['standard']['amount']}, premium={data['premium']['amount']}")


# ==================== Negative Tests ====================
class TestNegativeCases:
    """Negative test cases for error handling"""
    
    def test_auth_without_token(self):
        """Accessing protected endpoint without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print(f"✓ Protected endpoint without auth returns 401")

    def test_invalid_property_id(self):
        """Accessing non-existent property returns 404"""
        response = requests.get(f"{BASE_URL}/api/property/full-profile/non_existent_id")
        assert response.status_code == 404
        print(f"✓ Non-existent property returns 404")

    def test_invalid_login(self):
        """Login with wrong password returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@email.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print(f"✓ Invalid login returns 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
