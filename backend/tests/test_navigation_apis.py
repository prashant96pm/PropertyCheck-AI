"""
Backend API Tests for PropertyCheck AI - P0 Navigation & Search Features
Tests navigation and search related APIs
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://risk-analysis-hub-5.preview.emergentagent.com')

class TestHealthAndBasicAPIs:
    """Basic API health checks"""
    
    def test_health_endpoint(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed - status: {data['status']}")
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "PropertyCheck AI" in data["message"]
        print(f"✓ API root check passed - version: {data.get('version')}")

class TestPropertySearchAPIs:
    """Tests for Universal Property Search endpoints"""
    
    def test_search_no_params(self):
        """Test search endpoint returns sample properties when no params"""
        response = requests.get(f"{BASE_URL}/api/property/search")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "total" in data
        assert "search_type" in data
        assert data["search_type"] == "sample_registry"
        assert len(data["results"]) >= 1  # Should have sample data
        print(f"✓ Search (no params) returned {len(data['results'])} sample properties")
    
    def test_search_by_state(self):
        """Test search by state filter"""
        response = requests.get(f"{BASE_URL}/api/property/search?state=Karnataka")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        # All results should be from Karnataka
        for prop in data["results"]:
            assert prop.get("state", "").lower() == "karnataka"
        print(f"✓ Search by state returned {len(data['results'])} properties")
    
    def test_search_by_district(self):
        """Test search by district filter"""
        response = requests.get(f"{BASE_URL}/api/property/search?district=Bangalore")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print(f"✓ Search by district returned {len(data['results'])} properties")
    
    def test_search_by_survey_no(self):
        """Test search by survey number"""
        response = requests.get(f"{BASE_URL}/api/property/search?survey_no=123")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print(f"✓ Search by survey_no returned {len(data['results'])} properties")
    
    def test_ai_smart_search(self):
        """Test AI smart search endpoint"""
        payload = {
            "query": "Land in Bangalore Karnataka"
        }
        response = requests.post(
            f"{BASE_URL}/api/property/ai-smart-search",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "query_parsed" in data
        assert "results" in data
        assert "search_type" in data
        assert data["search_type"] == "ai_smart_search"
        print(f"✓ AI Smart Search returned {len(data['results'])} results, parsed: {data.get('query_parsed')}")

class TestPropertyProfileAPI:
    """Tests for Property 360 Profile endpoint"""
    
    @pytest.fixture
    def sample_property_id(self):
        """Get a sample property ID from search"""
        response = requests.get(f"{BASE_URL}/api/property/search")
        data = response.json()
        if data["results"]:
            return data["results"][0]["property_id"]
        pytest.skip("No sample properties available")
    
    def test_full_profile_endpoint(self, sample_property_id):
        """Test full profile endpoint returns 360 data"""
        response = requests.get(f"{BASE_URL}/api/property/full-profile/{sample_property_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check all required sections
        assert "property_id" in data
        assert "basic_details" in data
        assert "ownership_history" in data
        assert "legal_records" in data
        assert "documents" in data
        assert "geo_spatial" in data
        assert "government_records" in data
        
        # Verify basic_details structure
        basic = data["basic_details"]
        assert "survey_no" in basic
        assert "state" in basic
        assert "district" in basic
        
        # Verify ownership_history is a list
        assert isinstance(data["ownership_history"], list)
        
        # Verify legal_records structure
        legal = data["legal_records"]
        assert "cersai_status" in legal
        assert "ecourts_check" in legal
        
        print(f"✓ Full profile for {sample_property_id}:")
        print(f"  - Basic: {basic.get('survey_no')}, {basic.get('state')}")
        print(f"  - Ownership entries: {len(data['ownership_history'])}")
        print(f"  - Documents: {len(data['documents'])}")
    
    def test_full_profile_404(self):
        """Test full profile returns 404 for invalid ID"""
        response = requests.get(f"{BASE_URL}/api/property/full-profile/invalid_id_xyz")
        assert response.status_code == 404
        print("✓ Full profile returns 404 for invalid property ID")

class TestGovernmentRecordsAPI:
    """Tests for Government Records endpoint"""
    
    def test_government_records(self):
        """Test government records endpoint"""
        response = requests.get(f"{BASE_URL}/api/government-records/123?state=Karnataka")
        assert response.status_code == 200
        data = response.json()
        
        assert "survey_no" in data
        assert "owner_name" in data
        assert "land_type" in data
        assert "cersai_check" in data
        assert "source" in data
        assert "Bhoomi" in data["source"]  # Karnataka source
        assert "disclaimer" in data  # Should mention mock data
        print(f"✓ Government records API returned data from {data.get('source')}")
    
    def test_government_records_telangana(self):
        """Test government records returns correct source for Telangana"""
        response = requests.get(f"{BASE_URL}/api/government-records/456?state=Telangana")
        assert response.status_code == 200
        data = response.json()
        assert "Dharani" in data["source"]
        print(f"✓ Telangana records source: {data.get('source')}")

class TestAuthAPIs:
    """Tests for authentication endpoints"""
    
    def test_register_user(self):
        """Test user registration"""
        import time
        import random
        test_email = f"test_api_{int(time.time())}_{random.randint(1000,9999)}@test.com"
        payload = {
            "email": test_email,
            "password": "Test123!@",
            "name": "Test API User"
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_email
        print(f"✓ User registration successful - email: {test_email}")
    
    def test_login_user(self):
        """Test user login with existing test user"""
        # Use an already registered user
        payload = {
            "email": "test_nav_1771779964@test.com",
            "password": "Test123!@"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        print(f"✓ User login successful")
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        payload = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 401
        print("✓ Invalid login returns 401")

class TestProtectedEndpoints:
    """Tests for protected endpoints requiring authentication"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session using existing test user"""
        session = requests.Session()
        
        # Login with existing user
        payload = {
            "email": "test_nav_1771779964@test.com",
            "password": "Test123!@"
        }
        response = session.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        return session
    
    def test_dashboard_stats_authenticated(self, auth_session):
        """Test dashboard stats with authentication"""
        response = auth_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_properties" in data
        assert "total_documents" in data
        assert "total_reports" in data
        print(f"✓ Dashboard stats - properties: {data['total_properties']}, docs: {data['total_documents']}")
    
    def test_create_property_authenticated(self, auth_session):
        """Test property creation with authentication"""
        import time
        import random
        payload = {
            "survey_no": f"API/TEST/{int(time.time())}_{random.randint(100,999)}",
            "state": "Karnataka",
            "district": "Bangalore Urban"
        }
        response = auth_session.post(f"{BASE_URL}/api/properties", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "property_id" in data
        print(f"✓ Property created - ID: {data['property_id']}")
    
    def test_get_properties_authenticated(self, auth_session):
        """Test get user properties"""
        response = auth_session.get(f"{BASE_URL}/api/properties")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get properties returned {len(data)} properties")
    
    def test_analyze_property(self, auth_session):
        """Test AI analysis endpoint"""
        # Get user's properties first
        props_response = auth_session.get(f"{BASE_URL}/api/properties")
        assert props_response.status_code == 200
        
        properties = props_response.json()
        if not properties:
            pytest.skip("No properties to analyze")
        
        property_id = properties[0]["property_id"]
        
        # Run analysis
        response = auth_session.post(f"{BASE_URL}/api/analyze/{property_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "risk_score" in data
        assert "risk_status" in data
        assert "red_flags" in data
        assert "yellow_flags" in data
        assert "green_flags" in data
        assert "executive_summary" in data
        assert data["risk_status"] in ["GREEN", "YELLOW", "RED"]
        print(f"✓ AI Analysis - Score: {data['risk_score']}, Status: {data['risk_status']}")
    
    def test_unauthenticated_protected_endpoint(self):
        """Test protected endpoints return 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 401
        print("✓ Protected endpoint returns 401 without authentication")

class TestPricingAPI:
    """Tests for pricing endpoint"""
    
    def test_pricing_endpoint(self):
        """Test pricing returns all packages"""
        response = requests.get(f"{BASE_URL}/api/pricing")
        assert response.status_code == 200
        data = response.json()
        
        assert "basic" in data
        assert "standard" in data
        assert "premium" in data
        
        # Verify pricing amounts
        assert data["basic"]["amount"] == 499.00
        assert data["standard"]["amount"] == 999.00
        assert data["premium"]["amount"] == 1999.00
        
        print(f"✓ Pricing packages: Basic ₹{data['basic']['amount']}, Standard ₹{data['standard']['amount']}, Premium ₹{data['premium']['amount']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
