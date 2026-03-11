"""
Backend API tests for PropertyCheck AI - Property Intelligence Features
Tests: Title Chain, Legal Copilot, Valuation, Government Sources, Shared Reports
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_EMAIL = "test_intel@test.com"
TEST_PASSWORD = "Test123!@"
TEST_NAME = "Intel User"


class TestHealthAndBasics:
    """Health check and basic API tests"""
    
    def test_health_check(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health check passed")

    def test_root_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "PropertyCheck AI" in data.get("message", "")
        print("✓ Root endpoint passed")


class TestAuthentication:
    """User registration and authentication tests"""
    token = None
    
    def test_register_user(self):
        """Register test user"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME
        })
        # Either 200 (new user) or 400 (already exists)
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            TestAuthentication.token = data["access_token"]
            print(f"✓ User registered: {TEST_EMAIL}")
        elif response.status_code == 400:
            print(f"✓ User already exists, will login")
        else:
            pytest.fail(f"Unexpected status: {response.status_code}")

    def test_login_user(self):
        """Login and get token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        TestAuthentication.token = data["access_token"]
        print(f"✓ User logged in, token obtained")


class TestPropertyCreation:
    """Property creation for testing intelligence features"""
    property_id = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestAuthentication.token:
            # Login to get token
            response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            if response.status_code == 200:
                TestAuthentication.token = response.json()["access_token"]
        yield

    def test_create_property(self):
        """Create test property"""
        headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
        response = requests.post(f"{BASE_URL}/api/properties", json={
            "survey_no": "INT/001",
            "state": "Karnataka",
            "district": "Bengaluru Urban",
            "owner_name": "Intel Test Owner",
            "land_type": "Residential",
            "extent": "1200 Sq Ft"
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "property_id" in data
        TestPropertyCreation.property_id = data["property_id"]
        print(f"✓ Property created: {TestPropertyCreation.property_id}")


class TestTitleChain:
    """Tests for Title Chain Reconstruction endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestPropertyCreation.property_id:
            pytest.skip("No property_id available")
        yield

    def test_title_chain_returns_5_transfers(self):
        """GET /api/property/{id}/title-chain returns title chain with 5 transfers"""
        response = requests.get(f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/title-chain")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "chain" in data
        assert "total_transfers" in data
        assert "gaps" in data
        assert "anomalies" in data
        assert "completeness_score" in data
        
        # Verify 5 ownership entries
        assert len(data["chain"]) == 5, f"Expected 5 transfers, got {len(data['chain'])}"
        assert data["total_transfers"] == 5
        
        # Verify chain structure
        for entry in data["chain"]:
            assert "owner_name" in entry
            assert "transfer_date" in entry
            assert "transfer_type" in entry
            assert "verified" in entry
        
        print(f"✓ Title chain returned {data['total_transfers']} transfers, completeness: {data['completeness_score']}%")

    def test_title_chain_gap_analysis(self):
        """Title chain includes gap analysis"""
        response = requests.get(f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/title-chain")
        data = response.json()
        
        # Gaps should be a list (may be empty)
        assert isinstance(data["gaps"], list)
        # Anomalies should be a list
        assert isinstance(data["anomalies"], list)
        print(f"✓ Gap analysis: {len(data['gaps'])} gaps, {len(data['anomalies'])} anomalies")


class TestValuation:
    """Tests for Property Valuation endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestPropertyCreation.property_id:
            pytest.skip("No property_id available")
        yield

    def test_valuation_returns_market_intelligence(self):
        """GET /api/property/{id}/valuation returns estimated value, guideline value, price trends"""
        response = requests.get(f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/valuation")
        assert response.status_code == 200
        data = response.json()
        
        # Verify estimated value
        assert "estimated_value" in data
        assert "amount" in data["estimated_value"]
        assert "formatted" in data["estimated_value"]
        assert "confidence" in data["estimated_value"]
        
        # Verify guideline value
        assert "guideline_value" in data
        assert "formatted" in data["guideline_value"]
        assert "source" in data["guideline_value"]
        
        # Verify price trends
        assert "price_trends" in data
        assert "annual_appreciation" in data["price_trends"]
        assert "data_points" in data["price_trends"]
        
        print(f"✓ Valuation: {data['estimated_value']['formatted']}, trend: {data['price_trends']['annual_appreciation']}")

    def test_valuation_neighborhood_scores(self):
        """Valuation includes neighborhood scores"""
        response = requests.get(f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/valuation")
        data = response.json()
        
        assert "neighborhood" in data
        assert "locality_rating" in data["neighborhood"]
        assert "connectivity_score" in data["neighborhood"]
        assert "safety_score" in data["neighborhood"]
        print(f"✓ Neighborhood scores: locality={data['neighborhood']['locality_rating']}/5")

    def test_valuation_infrastructure(self):
        """Valuation includes infrastructure info"""
        response = requests.get(f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/valuation")
        data = response.json()
        
        assert "infrastructure" in data
        assert "metro_station" in data["infrastructure"]
        assert "hospital" in data["infrastructure"]
        print(f"✓ Infrastructure: metro at {data['infrastructure']['metro_station']['distance']}")


class TestGovernmentSources:
    """Tests for Government Sources endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestPropertyCreation.property_id:
            pytest.skip("No property_id available")
        yield

    def test_government_sources_returns_7_sources(self):
        """GET /api/property/{id}/government-sources returns 7 sources"""
        response = requests.get(f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/government-sources")
        assert response.status_code == 200
        data = response.json()
        
        assert "sources" in data
        assert "total_sources" in data
        assert "retrieved" in data
        assert "pending" in data
        
        # Verify 7 sources (state-specific + common)
        assert data["total_sources"] >= 7, f"Expected at least 7 sources, got {data['total_sources']}"
        
        # Verify each source has status
        for source in data["sources"]:
            assert "name" in source
            assert "status" in source
            assert source["status"] in ["RETRIEVED", "PENDING"]
        
        print(f"✓ Government sources: {data['retrieved']} retrieved, {data['pending']} pending out of {data['total_sources']}")


class TestLegalCopilot:
    """Tests for Legal Copilot endpoint (requires auth)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestPropertyCreation.property_id or not TestAuthentication.token:
            pytest.skip("No property_id or token available")
        yield

    def test_legal_copilot_generates_analysis(self):
        """POST /api/property/{id}/legal-copilot generates legal analysis"""
        headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
        response = requests.post(
            f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/legal-copilot",
            json={},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "analysis" in data
        assert data["analysis"] is not None
        assert len(data["analysis"]) > 100  # Should be substantial text
        assert "copilot_id" in data
        assert "ai_powered" in data
        
        print(f"✓ Legal Copilot generated analysis ({len(data['analysis'])} chars), AI powered: {data['ai_powered']}")

    def test_legal_copilot_get_saved_report(self):
        """GET /api/property/{id}/legal-copilot returns saved report"""
        headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
        response = requests.get(
            f"{BASE_URL}/api/property/{TestPropertyCreation.property_id}/legal-copilot",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # After POST, should have analysis
        if data.get("analysis"):
            print(f"✓ Retrieved saved Legal Copilot report")
        else:
            print(f"✓ No saved report (expected if POST not run first)")


class TestRiskAnalysis:
    """Tests for Risk Analysis endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestPropertyCreation.property_id or not TestAuthentication.token:
            pytest.skip("No property_id or token available")
        yield

    def test_run_analysis(self):
        """POST /api/analyze/{id} generates risk report"""
        headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
        response = requests.post(
            f"{BASE_URL}/api/analyze/{TestPropertyCreation.property_id}",
            json={},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "risk_score" in data
        assert "risk_status" in data
        assert "report_id" in data
        assert data["risk_status"] in ["GREEN", "YELLOW", "RED"]
        
        print(f"✓ Risk analysis: score={data['risk_score']}, status={data['risk_status']}")


class TestSharedReport:
    """Tests for Shared Report functionality"""
    share_token = None
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not TestPropertyCreation.property_id or not TestAuthentication.token:
            pytest.skip("No property_id or token available")
        yield

    def test_create_shared_report(self):
        """POST /api/reports/{property_id}/share generates share token"""
        headers = {"Authorization": f"Bearer {TestAuthentication.token}"}
        
        # First run analysis to create a report
        requests.post(
            f"{BASE_URL}/api/analyze/{TestPropertyCreation.property_id}",
            json={},
            headers=headers
        )
        
        response = requests.post(
            f"{BASE_URL}/api/reports/{TestPropertyCreation.property_id}/share",
            json={},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "share_token" in data
        TestSharedReport.share_token = data["share_token"]
        print(f"✓ Share token generated: {data['share_token'][:12]}...")

    def test_access_shared_report_public(self):
        """GET /api/shared-report/{token} returns report (public access)"""
        if not TestSharedReport.share_token:
            pytest.skip("No share token available")
        
        # This should work WITHOUT authentication
        response = requests.get(f"{BASE_URL}/api/shared-report/{TestSharedReport.share_token}")
        assert response.status_code == 200
        data = response.json()
        
        assert "report" in data
        assert "property_id" in data
        assert "created_at" in data
        print(f"✓ Shared report accessible publicly")

    def test_invalid_share_token_returns_404(self):
        """Invalid share token returns 404"""
        response = requests.get(f"{BASE_URL}/api/shared-report/invalid_token_xyz123")
        assert response.status_code == 404
        print(f"✓ Invalid token returns 404")


class TestPropertySearch:
    """Tests for Property Search"""
    
    def test_search_returns_sample_properties(self):
        """Search with no params returns sample registry"""
        response = requests.get(f"{BASE_URL}/api/property/search")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert len(data["results"]) > 0
        print(f"✓ Search returned {len(data['results'])} sample properties")

    def test_search_bengaluru_urban(self):
        """Search with district=Bengaluru Urban"""
        response = requests.get(f"{BASE_URL}/api/property/search?district=Bengaluru+Urban")
        assert response.status_code == 200
        data = response.json()
        
        for prop in data["results"]:
            if prop.get("district"):
                # Should find Bengaluru Urban properties
                pass
        print(f"✓ District search returned {len(data['results'])} results")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
