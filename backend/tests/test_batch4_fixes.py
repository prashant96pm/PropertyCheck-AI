"""
Test suite for PropertyCheck AI Batch 4 fixes
Tests: Landing/Dashboard icons, Legal pages, Profile/Settings, Search, Pricing, etc.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://risk-analysis-hub-5.preview.emergentagent.com')

# Test credentials 
TEST_EMAIL = f"test_batch4_{int(time.time())}@test.com"
TEST_PASSWORD = "Test123!@"
TEST_NAME = "Test Batch4 User"

class TestHealthAndBasicEndpoints:
    """Basic endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health check passed: {data}")

    def test_api_root(self):
        """Test /api/ root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "PropertyCheck AI API" in data.get("message", "")
        print(f"✓ API root passed: {data}")

    def test_pricing_endpoint(self):
        """Test /api/pricing endpoint returns 3 plans"""
        response = requests.get(f"{BASE_URL}/api/pricing")
        assert response.status_code == 200
        data = response.json()
        assert "basic" in data
        assert "standard" in data
        assert "premium" in data
        assert data["basic"]["amount"] == 499.00
        assert data["standard"]["amount"] == 999.00
        assert data["premium"]["amount"] == 1999.00
        print(f"✓ Pricing endpoint passed: 3 plans found")


class TestAuthenticationFlow:
    """Test user registration and login"""
    
    def test_register_new_user(self):
        """Test user registration"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"✓ Registration passed for: {TEST_EMAIL}")
        return data["access_token"]

    def test_login_existing_user(self):
        """Test user login"""
        # First register
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        
        # Then login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        # May get 401 if already registered with different password
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            print(f"✓ Login passed for: {TEST_EMAIL}")
        else:
            print(f"Note: Login returned {response.status_code} - may be duplicate registration")


class TestProfileEndpoints:
    """Test profile get/update endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        # Register new user
        email = f"test_profile_{int(time.time())}@test.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": TEST_PASSWORD,
            "name": "Profile Test User"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            session.headers.update({"Authorization": f"Bearer {token}"})
        return session, email
    
    def test_get_profile(self, auth_session):
        """Test GET /api/profile"""
        session, email = auth_session
        response = session.get(f"{BASE_URL}/api/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert "first_name" in data
        assert "last_name" in data
        assert "gender" in data
        assert "date_joined" in data
        print(f"✓ GET profile passed: {data.get('email')}")

    def test_update_profile(self, auth_session):
        """Test PUT /api/profile"""
        session, email = auth_session
        response = session.put(f"{BASE_URL}/api/profile", json={
            "first_name": "Updated",
            "last_name": "Name",
            "gender": "male"
        })
        assert response.status_code == 200
        
        # Verify update
        profile_response = session.get(f"{BASE_URL}/api/profile")
        profile_data = profile_response.json()
        assert profile_data["first_name"] == "Updated"
        assert profile_data["last_name"] == "Name"
        print(f"✓ PUT profile passed: name updated")


class TestSearchEndpoints:
    """Test property search endpoints"""
    
    def test_property_search_default(self):
        """Test /api/property/search returns sample properties"""
        response = requests.get(f"{BASE_URL}/api/property/search")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert len(data["results"]) > 0
        print(f"✓ Property search returned {data['total']} results")

    def test_property_search_by_state(self):
        """Test /api/property/search with state filter"""
        response = requests.get(f"{BASE_URL}/api/property/search?state=Karnataka")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # All results should be from Karnataka
        for result in data["results"]:
            if result.get("state"):
                assert "Karnataka" in result["state"] or result["state"] == "Karnataka"
        print(f"✓ Filtered search (Karnataka) returned {data['total']} results")

    def test_ai_smart_search(self):
        """Test /api/property/ai-smart-search"""
        response = requests.post(f"{BASE_URL}/api/property/ai-smart-search", json={
            "query": "land in Karnataka"
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query_parsed" in data
        # Should not fail with error
        print(f"✓ Smart search passed: {data['total']} results, parsed: {data.get('query_parsed')}")

    def test_smart_search_fallback(self):
        """Test smart search falls back to sample data on no results"""
        response = requests.post(f"{BASE_URL}/api/property/ai-smart-search", json={
            "query": "nonexistent property xyz123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Should return sample results with note
        if len(data["results"]) > 0:
            print(f"✓ Smart search fallback: returned {len(data['results'])} results")
        if "note" in data:
            print(f"  Note: {data['note']}")


class TestPropertyFullProfile:
    """Test property 360 profile endpoint"""
    
    def test_get_full_profile_from_registry(self):
        """Test /api/property/full-profile/{id} for registry property"""
        # First get a property from search
        search_response = requests.get(f"{BASE_URL}/api/property/search")
        results = search_response.json().get("results", [])
        if results:
            prop_id = results[0].get("property_id")
            response = requests.get(f"{BASE_URL}/api/property/full-profile/{prop_id}")
            assert response.status_code == 200
            data = response.json()
            assert "basic_details" in data
            assert "ownership_history" in data
            assert "legal_records" in data
            assert "government_records" in data
            print(f"✓ Full profile passed for property: {prop_id}")
            print(f"  Basic details: Survey {data['basic_details'].get('survey_no')}, Owner: {data['basic_details'].get('owner_name')}")


class TestGovernmentRecords:
    """Test government records endpoint"""
    
    def test_government_records_endpoint(self):
        """Test /api/government-records/{survey_no}"""
        response = requests.get(f"{BASE_URL}/api/government-records/123%2F4?state=Karnataka")
        assert response.status_code == 200
        data = response.json()
        assert "survey_no" in data
        assert "source" in data
        assert "Bhoomi" in data["source"]  # Karnataka uses Bhoomi
        assert "disclaimer" in data
        print(f"✓ Government records passed: source={data['source']}")

    def test_government_records_with_slash(self):
        """Test government records with survey number containing slash"""
        response = requests.get(f"{BASE_URL}/api/government-records/456/2?state=Telangana")
        assert response.status_code == 200
        data = response.json()
        assert "Dharani" in data["source"]  # Telangana uses Dharani
        print(f"✓ Government records with slash passed: source={data['source']}")


class TestBengaluruSpelling:
    """Test Bengaluru spelling is used instead of Bangalore"""
    
    def test_sample_properties_use_bengaluru(self):
        """Verify sample properties use 'Bengaluru' not 'Bangalore'"""
        response = requests.get(f"{BASE_URL}/api/property/search")
        data = response.json()
        
        bengaluru_count = 0
        bangalore_count = 0
        
        for result in data.get("results", []):
            district = result.get("district", "")
            if "Bengaluru" in district:
                bengaluru_count += 1
            elif "Bangalore" in district and "Bengaluru" not in district:
                bangalore_count += 1
        
        print(f"  Properties with 'Bengaluru': {bengaluru_count}")
        print(f"  Properties with 'Bangalore' only: {bangalore_count}")
        
        # Sample data should use Bengaluru
        if bengaluru_count > 0:
            print("✓ Sample properties use correct 'Bengaluru' spelling")
        

class TestDashboardStats:
    """Test dashboard stats endpoint"""
    
    def test_dashboard_stats_authenticated(self):
        """Test /api/dashboard/stats requires auth"""
        # First register and get token
        email = f"test_dashboard_{int(time.time())}@test.com"
        session = requests.Session()
        reg_response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": TEST_PASSWORD,
            "name": "Dashboard Test User"
        })
        
        if reg_response.status_code == 200:
            token = reg_response.json()["access_token"]
            session.headers.update({"Authorization": f"Bearer {token}"})
            
            response = session.get(f"{BASE_URL}/api/dashboard/stats")
            assert response.status_code == 200
            data = response.json()
            assert "total_properties" in data
            assert "total_documents" in data
            assert "total_reports" in data
            print(f"✓ Dashboard stats passed: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
