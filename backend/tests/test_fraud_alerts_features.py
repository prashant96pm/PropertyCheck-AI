"""
Test Suite for PropertyCheck AI - New Features
- AI Fraud Detection Engine (Gemini LLM)
- Record Alert Subscription System
- Gov States API
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://risk-analysis-hub-5.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_USER = {"email": "fraud_test@test.com", "password": "test1234", "name": "FraudTest"}


class TestAuthSetup:
    """Setup: Register/Login test user"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for test user"""
        # Try login first
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        
        if login_resp.status_code == 200:
            data = login_resp.json()
            return data.get("access_token") or data.get("token")
        
        # Register if login fails
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        if reg_resp.status_code in [200, 201]:
            data = reg_resp.json()
            return data.get("access_token") or data.get("token")
        
        # Try login again after registration
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code == 200:
            data = login_resp.json()
            return data.get("access_token") or data.get("token")
        
        pytest.skip(f"Could not authenticate: {login_resp.text}")
    
    def test_auth_works(self, auth_token):
        """Verify auth token is valid"""
        assert auth_token is not None
        print(f"Auth token obtained: {auth_token[:20]}...")


class TestGovStatesAPI:
    """Test GET /api/gov/states - Returns 20 state portals"""
    
    def test_get_states_returns_20_states(self):
        """GET /api/gov/states should return 20 Indian states"""
        resp = requests.get(f"{BASE_URL}/api/gov/states")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "states" in data, "Response should have 'states' key"
        assert "total" in data, "Response should have 'total' key"
        assert data["total"] == 20, f"Expected 20 states, got {data['total']}"
        
        # Verify state structure
        states = data["states"]
        assert len(states) == 20
        
        # Check first state has required fields
        first_state = states[0]
        assert "state" in first_state or "name" in first_state
        assert "documents" in first_state
        print(f"PASS: GET /api/gov/states returns {data['total']} states")


class TestFraudDetectionAPI:
    """Test AI Fraud Detection Engine endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code == 200:
            data = login_resp.json()
            return data.get("access_token") or data.get("token")
        
        # Register if needed
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        if reg_resp.status_code in [200, 201]:
            data = reg_resp.json()
            return data.get("access_token") or data.get("token")
        
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        data = login_resp.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def test_property_id(self, auth_token):
        """Create a test property for fraud analysis"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a property
        prop_data = {
            "survey_no": "FRAUD/TEST/001",
            "owner_name": "Fraud Test Owner",
            "property_type": "residential",
            "state": "karnataka",
            "district": "Bangalore Urban",
            "taluk": "Bangalore South",
            "village": "Koramangala",
            "area": {"value": 2400, "unit": "sqft"}
        }
        
        resp = requests.post(f"{BASE_URL}/api/properties", json=prop_data, headers=headers)
        if resp.status_code in [200, 201]:
            data = resp.json()
            return data.get("property_id")
        
        # If property creation fails, try to get existing property
        list_resp = requests.get(f"{BASE_URL}/api/properties", headers=headers)
        if list_resp.status_code == 200:
            props = list_resp.json().get("properties", [])
            if props:
                return props[0].get("property_id")
        
        pytest.skip("Could not create or find test property")
    
    def test_fraud_analyze_requires_auth(self):
        """POST /api/fraud/analyze/{property_id} requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/fraud/analyze/test123")
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("PASS: Fraud analyze requires authentication")
    
    def test_fraud_analyze_property_not_found(self, auth_token):
        """POST /api/fraud/analyze/{property_id} returns 404 for non-existent property"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = requests.post(f"{BASE_URL}/api/fraud/analyze/nonexistent_prop_xyz", headers=headers)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        print("PASS: Fraud analyze returns 404 for non-existent property")
    
    def test_fraud_analyze_success(self, auth_token, test_property_id):
        """POST /api/fraud/analyze/{property_id} returns fraud analysis with AI/rule-based results"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Run fraud analysis - may take a few seconds for AI
        resp = requests.post(f"{BASE_URL}/api/fraud/analyze/{test_property_id}", headers=headers, timeout=30)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Verify required fields
        assert "fraud_score" in data, "Response should have 'fraud_score'"
        assert "risk_level" in data, "Response should have 'risk_level'"
        assert "findings" in data, "Response should have 'findings'"
        assert "recommended_actions" in data, "Response should have 'recommended_actions'"
        
        # Validate fraud_score is 0-100
        assert 0 <= data["fraud_score"] <= 100, f"fraud_score should be 0-100, got {data['fraud_score']}"
        
        # Validate risk_level
        valid_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert data["risk_level"] in valid_levels, f"risk_level should be one of {valid_levels}, got {data['risk_level']}"
        
        # Validate findings is a list
        assert isinstance(data["findings"], list), "findings should be a list"
        
        # Validate recommended_actions is a list
        assert isinstance(data["recommended_actions"], list), "recommended_actions should be a list"
        
        # Check analysis method
        method = data.get("analysis_method", "unknown")
        print(f"PASS: Fraud analysis completed - Score: {data['fraud_score']}, Risk: {data['risk_level']}, Method: {method}")
    
    def test_fraud_report_get(self, auth_token, test_property_id):
        """GET /api/fraud/report/{property_id} retrieves latest fraud report"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/fraud/report/{test_property_id}", headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Should have fraud_score (either from analysis or null message)
        if "fraud_score" in data and data["fraud_score"] is not None:
            assert "risk_level" in data
            assert "findings" in data
            print(f"PASS: Fraud report retrieved - Score: {data['fraud_score']}")
        else:
            # No analysis run yet
            assert "message" in data
            print(f"PASS: Fraud report endpoint works - {data.get('message', 'No report yet')}")
    
    def test_fraud_report_requires_auth(self):
        """GET /api/fraud/report/{property_id} requires authentication"""
        resp = requests.get(f"{BASE_URL}/api/fraud/report/test123")
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("PASS: Fraud report requires authentication")


class TestRecordAlertSubscription:
    """Test Record Alert Subscription System endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code == 200:
            data = login_resp.json()
            return data.get("access_token") or data.get("token")
        
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        if reg_resp.status_code in [200, 201]:
            data = reg_resp.json()
            return data.get("access_token") or data.get("token")
        
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        data = login_resp.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def created_subscription_id(self, auth_token):
        """Create a subscription and return its ID for other tests"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        sub_data = {
            "state": "Karnataka",
            "documentTypes": ["RTC", "EC"],
            "frequency": "daily",
            "propertyId": "test_prop_123"
        }
        
        resp = requests.post(f"{BASE_URL}/api/alerts/subscribe", json=sub_data, headers=headers)
        if resp.status_code in [200, 201]:
            return resp.json().get("subscription_id")
        return None
    
    def test_subscribe_requires_auth(self):
        """POST /api/alerts/subscribe requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/alerts/subscribe", json={"state": "Karnataka"})
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("PASS: Subscribe requires authentication")
    
    def test_subscribe_requires_state(self, auth_token):
        """POST /api/alerts/subscribe requires state field"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = requests.post(f"{BASE_URL}/api/alerts/subscribe", json={}, headers=headers)
        assert resp.status_code == 400, f"Expected 400 without state, got {resp.status_code}"
        print("PASS: Subscribe requires state field")
    
    def test_subscribe_success(self, auth_token):
        """POST /api/alerts/subscribe creates subscription successfully"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        sub_data = {
            "state": "Maharashtra",
            "documentTypes": ["SATBARA", "7/12"],
            "frequency": "weekly",
            "propertyId": "test_prop_456"
        }
        
        resp = requests.post(f"{BASE_URL}/api/alerts/subscribe", json=sub_data, headers=headers)
        assert resp.status_code in [200, 201], f"Expected 200/201, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "subscription_id" in data, "Response should have 'subscription_id'"
        assert data.get("status") == "active", f"Status should be 'active', got {data.get('status')}"
        print(f"PASS: Subscription created - ID: {data['subscription_id']}")
        
        return data["subscription_id"]
    
    def test_list_subscriptions(self, auth_token):
        """GET /api/alerts/subscriptions lists user's subscriptions"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/alerts/subscriptions", headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "subscriptions" in data, "Response should have 'subscriptions'"
        assert "total" in data, "Response should have 'total'"
        assert isinstance(data["subscriptions"], list), "subscriptions should be a list"
        print(f"PASS: Listed {data['total']} subscriptions")
    
    def test_update_subscription(self, auth_token, created_subscription_id):
        """PUT /api/alerts/subscription/{sub_id} updates subscription"""
        if not created_subscription_id:
            pytest.skip("No subscription created")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        update_data = {
            "frequency": "instant",
            "active": True
        }
        
        resp = requests.put(f"{BASE_URL}/api/alerts/subscription/{created_subscription_id}", 
                          json=update_data, headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert data.get("status") == "updated", f"Status should be 'updated', got {data.get('status')}"
        print(f"PASS: Subscription {created_subscription_id} updated")
    
    def test_update_subscription_not_found(self, auth_token):
        """PUT /api/alerts/subscription/{sub_id} returns 404 for non-existent subscription"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        resp = requests.put(f"{BASE_URL}/api/alerts/subscription/nonexistent_sub_xyz", 
                          json={"active": False}, headers=headers)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("PASS: Update returns 404 for non-existent subscription")
    
    def test_manual_check(self, auth_token, created_subscription_id):
        """POST /api/alerts/check-now/{sub_id} triggers manual check"""
        if not created_subscription_id:
            pytest.skip("No subscription created")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        resp = requests.post(f"{BASE_URL}/api/alerts/check-now/{created_subscription_id}", headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert data.get("status") == "checking", f"Status should be 'checking', got {data.get('status')}"
        print(f"PASS: Manual check triggered for {created_subscription_id}")
    
    def test_manual_check_not_found(self, auth_token):
        """POST /api/alerts/check-now/{sub_id} returns 404 for non-existent subscription"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        resp = requests.post(f"{BASE_URL}/api/alerts/check-now/nonexistent_sub_xyz", headers=headers)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("PASS: Manual check returns 404 for non-existent subscription")
    
    def test_get_notifications(self, auth_token):
        """GET /api/alerts/notifications returns user's notifications"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        resp = requests.get(f"{BASE_URL}/api/alerts/notifications", headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "notifications" in data, "Response should have 'notifications'"
        assert isinstance(data["notifications"], list), "notifications should be a list"
        print(f"PASS: Got {len(data['notifications'])} notifications")
    
    def test_delete_subscription(self, auth_token):
        """DELETE /api/alerts/subscription/{sub_id} deletes subscription"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create a subscription to delete
        sub_data = {"state": "Telangana", "frequency": "daily"}
        create_resp = requests.post(f"{BASE_URL}/api/alerts/subscribe", json=sub_data, headers=headers)
        
        if create_resp.status_code not in [200, 201]:
            pytest.skip("Could not create subscription to delete")
        
        sub_id = create_resp.json().get("subscription_id")
        
        # Delete it
        resp = requests.delete(f"{BASE_URL}/api/alerts/subscription/{sub_id}", headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert data.get("status") == "deleted", f"Status should be 'deleted', got {data.get('status')}"
        print(f"PASS: Subscription {sub_id} deleted")
    
    def test_delete_subscription_not_found(self, auth_token):
        """DELETE /api/alerts/subscription/{sub_id} returns 404 for non-existent subscription"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        resp = requests.delete(f"{BASE_URL}/api/alerts/subscription/nonexistent_sub_xyz", headers=headers)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("PASS: Delete returns 404 for non-existent subscription")


class TestGovFetchMockMode:
    """Test POST /api/gov/fetch in mock mode"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code == 200:
            data = login_resp.json()
            return data.get("access_token") or data.get("token")
        
        reg_resp = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        if reg_resp.status_code in [200, 201]:
            data = reg_resp.json()
            return data.get("access_token") or data.get("token")
        
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        data = login_resp.json()
        return data.get("access_token") or data.get("token")
    
    def test_gov_fetch_requires_auth(self):
        """POST /api/gov/fetch requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/gov/fetch", json={"state": "karnataka", "documentType": "RTC"})
        assert resp.status_code == 401, f"Expected 401 without auth, got {resp.status_code}"
        print("PASS: Gov fetch requires authentication")
    
    def test_gov_fetch_mock_mode(self, auth_token):
        """POST /api/gov/fetch returns job in mock mode"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        fetch_data = {
            "state": "karnataka",
            "documentType": "RTC",
            "inputs": {
                "survey_no": "123/4",
                "district": "Bangalore Urban",
                "taluk": "Bangalore South",
                "village": "Koramangala"
            }
        }
        
        resp = requests.post(f"{BASE_URL}/api/gov/fetch", json=fetch_data, headers=headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        
        # Should return job_id or CACHED
        if data.get("status") == "CACHED":
            print("PASS: Gov fetch returned cached result")
        else:
            assert "job_id" in data, "Response should have 'job_id'"
            assert data.get("status") == "PENDING", f"Status should be 'PENDING', got {data.get('status')}"
            print(f"PASS: Gov fetch job created - ID: {data['job_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
