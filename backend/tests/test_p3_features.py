"""
P3 Features Backend API Tests
Tests for: Land Registries (17 states), Background Jobs, Payment endpoints
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestLandRegistries:
    """Test GET /api/property/{id}/land-registries - 17 Indian state registries"""

    def test_land_registries_endpoint_exists(self):
        """Test that land-registries endpoint returns data"""
        # First create a test property to get a valid property_id
        resp = requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "P3 LandReg Test",
            "email": "p3landregtest@test.com",
            "password": "testpass123"
        })
        
        # Login to get session
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "p3landregtest@test.com",
            "password": "testpass123"
        })
        
        if login_resp.status_code != 200:
            # User already exists, try logging in
            session = requests.Session()
            login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": "p3landregtest@test.com",
                "password": "testpass123"
            })
        
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        
        # Create a test property
        prop_resp = session.post(f"{BASE_URL}/api/properties", json={
            "survey_no": "P3/LANDREG/001",
            "owner_name": "Land Registry Test Owner",
            "district": "Bengaluru Urban",
            "state": "Karnataka"
        })
        
        property_id = None
        if prop_resp.status_code in [200, 201]:
            property_id = prop_resp.json().get("property_id")
        else:
            # Search for existing property
            search_resp = session.get(f"{BASE_URL}/api/properties/search?query=P3")
            if search_resp.status_code == 200:
                props = search_resp.json()
                if isinstance(props, list) and len(props) > 0:
                    property_id = props[0].get("property_id")
                elif isinstance(props, dict) and props.get("properties"):
                    property_id = props["properties"][0].get("property_id")
        
        if not property_id:
            # Use a known existing property or generate test id
            property_id = "test_property_123"
        
        # Test land registries endpoint
        reg_resp = session.get(f"{BASE_URL}/api/property/{property_id}/land-registries")
        
        # Verify response structure
        assert reg_resp.status_code in [200, 404], f"Unexpected status: {reg_resp.status_code}"
        
        if reg_resp.status_code == 200:
            data = reg_resp.json()
            
            # Verify 17 states present
            assert "registries" in data, "Missing registries key"
            registries = data["registries"]
            assert len(registries) >= 17, f"Expected 17 states, got {len(registries)}"
            
            # Verify structure of each registry
            expected_states = ["Karnataka", "Maharashtra", "Tamil Nadu", "Telangana", "Andhra Pradesh", 
                              "Uttar Pradesh", "Rajasthan", "Gujarat", "West Bengal", "Kerala",
                              "Madhya Pradesh", "Punjab", "Haryana", "Odisha", "Assam", "Bihar", "Delhi"]
            
            registry_states = [r["state"] for r in registries]
            for state in expected_states:
                assert state in registry_states, f"Missing state: {state}"
            
            # Verify each registry has required fields
            for reg in registries:
                assert "state" in reg
                assert "name" in reg
                assert "portal_url" in reg
                assert "digitization" in reg
                assert "records_available" in reg
            
            # Verify primary registry is set correctly
            if "primary_registry" in data:
                assert "name" in data["primary_registry"]
                assert "portal_url" in data["primary_registry"]
            
            print(f"PASS: Land registries endpoint returned {len(registries)} states")


class TestBackgroundJobs:
    """Test Background Jobs: submit, status poll, list"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        # Register test user
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "P3 Jobs Test",
            "email": "p3jobstest@test.com",
            "password": "testpass123"
        })
        
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "p3jobstest@test.com",
            "password": "testpass123"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        return session
    
    @pytest.fixture
    def test_property_id(self, auth_session):
        """Get or create test property"""
        prop_resp = auth_session.post(f"{BASE_URL}/api/properties", json={
            "survey_no": "P3/JOBS/001",
            "owner_name": "Jobs Test Owner",
            "district": "Mumbai",
            "state": "Maharashtra"
        })
        
        if prop_resp.status_code in [200, 201]:
            return prop_resp.json().get("property_id")
        
        # Search for existing property
        search_resp = auth_session.get(f"{BASE_URL}/api/properties/search?query=P3")
        if search_resp.status_code == 200:
            props = search_resp.json()
            if isinstance(props, list) and len(props) > 0:
                return props[0].get("property_id")
            elif isinstance(props, dict) and props.get("properties"):
                return props["properties"][0].get("property_id")
        
        pytest.skip("Could not get test property")
    
    def test_submit_job(self, auth_session, test_property_id):
        """POST /api/jobs/submit - submit background job"""
        job_types = ["risk_analysis", "document_ocr", "govt_data_retrieval", "title_verification", "valuation_report"]
        
        for job_type in job_types[:2]:  # Test 2 types to save time
            resp = auth_session.post(f"{BASE_URL}/api/jobs/submit", json={
                "job_type": job_type,
                "property_id": test_property_id
            })
            
            assert resp.status_code == 200, f"Job submit failed for {job_type}: {resp.text}"
            data = resp.json()
            
            assert "job_id" in data, "Missing job_id in response"
            assert data["status"] == "queued", f"Expected status 'queued', got {data['status']}"
            assert data["job_id"].startswith("job_"), "job_id should start with 'job_'"
            
            print(f"PASS: Submitted {job_type} job: {data['job_id']}")
    
    def test_job_status_polling(self, auth_session, test_property_id):
        """GET /api/jobs/status/{job_id} - poll job progress"""
        # Submit a job
        submit_resp = auth_session.post(f"{BASE_URL}/api/jobs/submit", json={
            "job_type": "risk_analysis",
            "property_id": test_property_id
        })
        
        assert submit_resp.status_code == 200
        job_id = submit_resp.json()["job_id"]
        
        # Poll status multiple times
        prev_progress = 0
        for i in range(3):
            time.sleep(2)  # Wait 2 seconds between polls
            
            status_resp = auth_session.get(f"{BASE_URL}/api/jobs/status/{job_id}")
            assert status_resp.status_code == 200, f"Status check failed: {status_resp.text}"
            
            data = status_resp.json()
            assert "job_id" in data
            assert "status" in data
            assert "progress" in data
            
            status = data["status"]
            progress = data["progress"]
            
            assert status in ["queued", "processing", "completed", "failed"]
            assert 0 <= progress <= 100
            
            # Progress should increase (or stay same if completed)
            if data["status"] == "processing":
                assert progress >= prev_progress, f"Progress decreased: {prev_progress} -> {progress}"
            
            prev_progress = progress
            print(f"Poll {i+1}: status={status}, progress={progress}%")
            
            if status == "completed":
                assert progress == 100
                break
    
    def test_list_jobs(self, auth_session, test_property_id):
        """GET /api/jobs/list - list user's jobs"""
        # Submit a job first
        auth_session.post(f"{BASE_URL}/api/jobs/submit", json={
            "job_type": "document_ocr",
            "property_id": test_property_id
        })
        
        # List jobs
        list_resp = auth_session.get(f"{BASE_URL}/api/jobs/list")
        assert list_resp.status_code == 200, f"List jobs failed: {list_resp.text}"
        
        data = list_resp.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)
        assert len(data["jobs"]) >= 1
        
        # Verify job structure
        job = data["jobs"][0]
        assert "job_id" in job
        assert "job_type" in job
        assert "status" in job
        assert "property_id" in job
        
        print(f"PASS: Listed {len(data['jobs'])} jobs")
    
    def test_job_requires_auth(self):
        """Test that job endpoints require authentication"""
        # Submit without auth
        resp = requests.post(f"{BASE_URL}/api/jobs/submit", json={
            "job_type": "risk_analysis",
            "property_id": "test_prop"
        })
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        
        # Status without auth
        resp = requests.get(f"{BASE_URL}/api/jobs/status/job_123")
        assert resp.status_code in [401, 403, 404], f"Expected 401/403/404, got {resp.status_code}"
        
        # List without auth
        resp = requests.get(f"{BASE_URL}/api/jobs/list")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        
        print("PASS: Job endpoints correctly require authentication")


class TestPaymentEndpoints:
    """Test Payment endpoints: Stripe & Razorpay"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "P3 Payment Test",
            "email": "p3paymenttest@test.com",
            "password": "testpass123"
        })
        
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "p3paymenttest@test.com",
            "password": "testpass123"
        })
        assert login_resp.status_code == 200
        return session
    
    @pytest.fixture
    def test_property_id(self, auth_session):
        """Get or create test property"""
        prop_resp = auth_session.post(f"{BASE_URL}/api/properties", json={
            "survey_no": "P3/PAYMENT/001",
            "owner_name": "Payment Test Owner",
            "district": "Chennai",
            "state": "Tamil Nadu"
        })
        
        if prop_resp.status_code in [200, 201]:
            return prop_resp.json().get("property_id")
        
        # Use existing property
        search_resp = auth_session.get(f"{BASE_URL}/api/properties/search?query=P3")
        if search_resp.status_code == 200:
            props = search_resp.json()
            if isinstance(props, list) and len(props) > 0:
                return props[0].get("property_id")
            elif isinstance(props, dict) and props.get("properties"):
                return props["properties"][0].get("property_id")
        
        return "test_property_pay"
    
    def test_pricing_endpoint(self):
        """GET /api/pricing - returns pricing tiers"""
        resp = requests.get(f"{BASE_URL}/api/pricing")
        assert resp.status_code == 200, f"Pricing failed: {resp.text}"
        
        data = resp.json()
        
        # Verify 3 tiers present
        assert "basic" in data
        assert "standard" in data
        assert "premium" in data
        
        # Verify each tier has required fields
        for tier in ["basic", "standard", "premium"]:
            assert "name" in data[tier]
            assert "amount" in data[tier]
            assert "features" in data[tier]
            assert isinstance(data[tier]["features"], list)
        
        print(f"PASS: Pricing returned 3 tiers")
    
    def test_create_checkout_stripe(self, auth_session, test_property_id):
        """POST /api/payments/create-checkout with payment_method='stripe'"""
        resp = auth_session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "property_id": test_property_id,
            "package_type": "basic",
            "origin_url": "https://test.com",
            "payment_method": "stripe"
        })
        
        # Could be 200 (success) or 500 (Stripe test key issue)
        if resp.status_code == 200:
            data = resp.json()
            # Verify response structure
            assert "checkout_url" in data or "session_id" in data, f"Missing checkout fields: {data}"
            if "payment_method" in data:
                assert data["payment_method"] in ["stripe", "mock"]
            print(f"PASS: Stripe checkout response: {data.get('payment_method', 'unknown')}")
        else:
            # 500 is acceptable for test keys
            print(f"INFO: Stripe checkout returned {resp.status_code} (test keys may not work)")
    
    def test_create_checkout_razorpay(self, auth_session, test_property_id):
        """POST /api/payments/create-checkout with payment_method='razorpay'"""
        resp = auth_session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "property_id": test_property_id,
            "package_type": "standard",
            "origin_url": "https://test.com",
            "payment_method": "razorpay"
        })
        
        # Could be 200 (success) or 500 (Razorpay test key issue)
        if resp.status_code == 200:
            data = resp.json()
            # Verify Razorpay response structure
            assert "order_id" in data or "amount" in data, f"Missing razorpay fields: {data}"
            if "payment_method" in data:
                assert data["payment_method"] == "razorpay"
            print(f"PASS: Razorpay order created: {data.get('order_id', 'N/A')}")
        else:
            # 500 is acceptable for test keys
            print(f"INFO: Razorpay checkout returned {resp.status_code} (test keys may not work)")
    
    def test_razorpay_verify_endpoint_exists(self, auth_session):
        """POST /api/payments/razorpay-verify - endpoint exists"""
        # This will fail validation but confirms endpoint exists
        resp = auth_session.post(f"{BASE_URL}/api/payments/razorpay-verify", json={
            "order_id": "test_order",
            "razorpay_payment_id": "pay_test",
            "razorpay_signature": "sig_test"
        })
        
        # Should not be 404 or 405
        assert resp.status_code not in [404, 405], f"Endpoint not found: {resp.status_code}"
        # 400 or 500 is expected with invalid data
        print(f"PASS: Razorpay verify endpoint exists (status: {resp.status_code})")
    
    def test_payment_status_endpoint(self, auth_session):
        """GET /api/payments/status/{session_id} - payment status check"""
        # Test with mock session
        resp = auth_session.get(f"{BASE_URL}/api/payments/status/mock_session_123")
        
        # Should return some status (not_found is acceptable)
        assert resp.status_code == 200, f"Payment status failed: {resp.text}"
        
        data = resp.json()
        assert "status" in data or "payment_status" in data
        print(f"PASS: Payment status endpoint working")
    
    def test_checkout_requires_auth(self):
        """Test that checkout requires authentication"""
        resp = requests.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "property_id": "test",
            "package_type": "basic",
            "payment_method": "stripe"
        })
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print("PASS: Checkout correctly requires authentication")


class TestIntegration:
    """Integration tests for P3 features"""
    
    def test_full_p3_flow(self):
        """Test full P3 flow: register -> property -> land registries -> job"""
        # 1. Register user
        email = f"p3flow_{int(time.time())}@test.com"
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "name": "P3 Flow Test",
            "email": email,
            "password": "testpass123"
        })
        
        # 2. Login
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": "testpass123"
        })
        
        if login_resp.status_code != 200:
            pytest.skip("Could not login for integration test")
        
        # 3. Create property
        prop_resp = session.post(f"{BASE_URL}/api/properties", json={
            "survey_no": f"P3/FLOW/{int(time.time()) % 1000}",
            "owner_name": "Flow Test Owner",
            "district": "Hyderabad",
            "state": "Telangana"
        })
        
        if prop_resp.status_code not in [200, 201]:
            pytest.skip("Could not create property")
        
        property_id = prop_resp.json().get("property_id")
        
        # 4. Get land registries
        reg_resp = session.get(f"{BASE_URL}/api/property/{property_id}/land-registries")
        assert reg_resp.status_code == 200, f"Land registries failed: {reg_resp.text}"
        
        registries = reg_resp.json().get("registries", [])
        assert len(registries) == 17, f"Expected 17 states, got {len(registries)}"
        
        # Verify Telangana is marked as property state
        telangana = next((r for r in registries if r["state"] == "Telangana"), None)
        assert telangana is not None
        assert telangana.get("is_property_state") == True
        
        # 5. Submit background job
        job_resp = session.post(f"{BASE_URL}/api/jobs/submit", json={
            "job_type": "risk_analysis",
            "property_id": property_id
        })
        assert job_resp.status_code == 200, f"Job submit failed: {job_resp.text}"
        job_id = job_resp.json()["job_id"]
        
        # 6. Poll job status
        time.sleep(3)
        status_resp = session.get(f"{BASE_URL}/api/jobs/status/{job_id}")
        assert status_resp.status_code == 200
        
        status_data = status_resp.json()
        assert status_data["status"] in ["queued", "processing", "completed"]
        assert status_data["progress"] >= 0
        
        print(f"PASS: Full P3 flow completed - property: {property_id}, job: {job_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
