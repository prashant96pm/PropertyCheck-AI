"""
GovDataBridge Module Tests - Tests for 20 Indian state government portal scrapers
Tests: GET /api/gov/states, GET /api/gov/portals/status, POST /api/gov/fetch,
       GET /api/gov/job/{job_id}, POST /api/gov/fetch-bulk, GET /api/gov/jobs/history,
       GET /api/gov/records/{property_id}, caching behavior
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test user credentials
TEST_USER = {
    "name": "GovTest",
    "email": "govtest@test.com",
    "password": "testpass123"
}


class TestGovDataBridgePublicEndpoints:
    """Tests for public endpoints (no auth required)"""

    def test_get_states_returns_20_states(self):
        """GET /api/gov/states - returns 20 supported states with portal info"""
        response = requests.get(f"{BASE_URL}/api/gov/states")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "states" in data
        assert "total" in data
        assert data["total"] == 20, f"Expected 20 states, got {data['total']}"
        
        # Verify state structure
        states = data["states"]
        assert len(states) == 20
        
        # Check required fields in each state
        required_fields = ["state_key", "name", "url", "documents", "inputs", "captcha_type"]
        for state in states:
            for field in required_fields:
                assert field in state, f"Missing field '{field}' in state {state.get('state_key', 'unknown')}"
        
        # Verify specific states exist
        state_keys = [s["state_key"] for s in states]
        expected_states = ["karnataka", "telangana", "maharashtra", "uttarpradesh", "tamilnadu"]
        for expected in expected_states:
            assert expected in state_keys, f"Expected state '{expected}' not found"
        
        print(f"✓ GET /api/gov/states returns {data['total']} states with correct structure")

    def test_get_portals_status_mock_mode(self):
        """GET /api/gov/portals/status - returns status for all 20 portals (MOCK mode)"""
        response = requests.get(f"{BASE_URL}/api/gov/portals/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "portals" in data
        assert "total" in data
        assert "mock_mode" in data
        
        assert data["total"] == 20, f"Expected 20 portals, got {data['total']}"
        assert data["mock_mode"] == True, "Expected mock_mode to be True"
        
        # Verify all portals have MOCK status
        portals = data["portals"]
        for state_key, portal in portals.items():
            assert portal["status"] == "MOCK", f"Portal {state_key} status is {portal['status']}, expected MOCK"
            assert "name" in portal
            assert "url" in portal
            assert "documents" in portal
            assert "captcha_type" in portal
        
        print(f"✓ GET /api/gov/portals/status returns {data['total']} portals in MOCK mode")


class TestGovDataBridgeAuthenticatedEndpoints:
    """Tests for authenticated endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Register/login test user and get session"""
        self.session = requests.Session()
        
        # Try to register (may already exist)
        register_resp = self.session.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        
        if login_resp.status_code != 200:
            pytest.skip(f"Login failed: {login_resp.text}")
        
        self.user_data = login_resp.json()
        print(f"✓ Logged in as {TEST_USER['email']}")
        yield
        
    def test_fetch_requires_auth(self):
        """POST /api/gov/fetch - requires authentication"""
        # Use a fresh session without auth
        response = requests.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "karnataka",
            "documentType": "RTC",
            "inputs": {"district": "Bengaluru Urban", "surveyNumber": "123/45"},
            "propertyId": "test"
        })
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ POST /api/gov/fetch requires authentication")

    def test_fetch_invalid_state_returns_400(self):
        """POST /api/gov/fetch - invalid state returns 400 error"""
        response = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "invalidstate",
            "documentType": "RTC",
            "inputs": {},
            "propertyId": "test"
        })
        assert response.status_code == 400, f"Expected 400 for invalid state, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "Unsupported state" in data["detail"]
        print("✓ POST /api/gov/fetch returns 400 for invalid state")

    def test_fetch_invalid_document_type_returns_400(self):
        """POST /api/gov/fetch - invalid document type returns 400 error"""
        response = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "karnataka",
            "documentType": "INVALID_DOC",
            "inputs": {"district": "Bengaluru Urban"},
            "propertyId": "test"
        })
        assert response.status_code == 400, f"Expected 400 for invalid doc type, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "Unsupported document type" in data["detail"]
        print("✓ POST /api/gov/fetch returns 400 for invalid document type")

    def test_fetch_karnataka_rtc_record(self):
        """POST /api/gov/fetch - fetch Karnataka RTC record"""
        response = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "karnataka",
            "documentType": "RTC",
            "inputs": {"district": "Bengaluru Urban", "surveyNumber": "123/45"},
            "propertyId": "test_prop_ka"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Either CACHED or PENDING with job_id
        assert data["status"] in ["CACHED", "PENDING"], f"Unexpected status: {data['status']}"
        
        if data["status"] == "PENDING":
            assert "job_id" in data
            assert "estimated_wait_time" in data
            self.karnataka_job_id = data["job_id"]
            print(f"✓ Karnataka RTC fetch submitted, job_id: {data['job_id']}")
        else:
            assert "result" in data
            print("✓ Karnataka RTC fetch returned CACHED result")

    def test_fetch_telangana_ec_record(self):
        """POST /api/gov/fetch - fetch Telangana EC record"""
        response = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "telangana",
            "documentType": "EC",
            "inputs": {"district": "Hyderabad", "mandal": "Secunderabad", "surveyNumber": "456/78"},
            "propertyId": "test_prop_ts"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] in ["CACHED", "PENDING"]
        print(f"✓ Telangana EC fetch submitted, status: {data['status']}")

    def test_fetch_maharashtra_satbara_record(self):
        """POST /api/gov/fetch - fetch Maharashtra SATBARA record"""
        response = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "maharashtra",
            "documentType": "SATBARA",
            "inputs": {"district": "Pune", "taluka": "Haveli", "gutNumber": "789"},
            "propertyId": "test_prop_mh"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] in ["CACHED", "PENDING"]
        print(f"✓ Maharashtra SATBARA fetch submitted, status: {data['status']}")

    def test_fetch_up_khatauni_record(self):
        """POST /api/gov/fetch - fetch UP KHATAUNI record"""
        response = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "uttarpradesh",
            "documentType": "KHATAUNI",
            "inputs": {"district": "Lucknow", "tehsil": "Lucknow", "khasraNumber": "101"},
            "propertyId": "test_prop_up"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] in ["CACHED", "PENDING"]
        print(f"✓ UP KHATAUNI fetch submitted, status: {data['status']}")

    def test_poll_job_progress_and_completion(self):
        """GET /api/gov/job/{job_id} - poll job progress and check COMPLETED status"""
        # First submit a job
        submit_resp = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "karnataka",
            "documentType": "MR",  # Use different doc type to avoid cache
            "inputs": {"district": "Mysuru", "surveyNumber": f"poll_test_{int(time.time())}"},
            "propertyId": "test_poll"
        })
        assert submit_resp.status_code == 200
        
        data = submit_resp.json()
        if data["status"] == "CACHED":
            print("✓ Job returned CACHED (already completed)")
            return
        
        job_id = data["job_id"]
        print(f"  Polling job {job_id}...")
        
        # Poll for completion (max 30 seconds)
        max_polls = 10
        poll_interval = 3
        completed = False
        
        for i in range(max_polls):
            time.sleep(poll_interval)
            poll_resp = self.session.get(f"{BASE_URL}/api/gov/job/{job_id}")
            assert poll_resp.status_code == 200, f"Poll failed: {poll_resp.text}"
            
            job_data = poll_resp.json()
            status = job_data.get("status")
            progress = job_data.get("progress", 0)
            current_step = job_data.get("current_step", "")
            
            print(f"  Poll {i+1}: status={status}, progress={progress}%, step={current_step}")
            
            if status == "COMPLETED":
                completed = True
                assert "result" in job_data
                assert job_data["progress"] == 100
                print(f"✓ Job {job_id} COMPLETED with result")
                break
            elif status == "FAILED":
                pytest.fail(f"Job failed: {job_data.get('error')}")
        
        assert completed, f"Job did not complete within {max_polls * poll_interval} seconds"

    def test_fetch_bulk_multiple_states(self):
        """POST /api/gov/fetch-bulk - submit bulk fetch for 3 states"""
        bulk_requests = [
            {"state": "karnataka", "documentType": "PT", "inputs": {"district": "Bengaluru"}, "propertyId": "bulk_test"},
            {"state": "telangana", "documentType": "MARKET_VALUE", "inputs": {"district": "Hyderabad"}, "propertyId": "bulk_test"},
            {"state": "rajasthan", "documentType": "JAMABANDI", "inputs": {"district": "Jaipur"}, "propertyId": "bulk_test"},
        ]
        
        response = self.session.post(f"{BASE_URL}/api/gov/fetch-bulk", json={"requests": bulk_requests})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert data["total"] == 3, f"Expected 3 jobs, got {data['total']}"
        
        # Verify each job has required fields
        for job in data["jobs"]:
            if "error" not in job:
                assert "job_id" in job
                assert "state" in job
                assert "document_type" in job
                assert job["status"] == "PENDING"
        
        print(f"✓ Bulk fetch submitted {data['total']} jobs")

    def test_get_job_history(self):
        """GET /api/gov/jobs/history - list user's gov job history"""
        response = self.session.get(f"{BASE_URL}/api/gov/jobs/history")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        assert isinstance(data["jobs"], list)
        
        # Should have jobs from previous tests
        if data["total"] > 0:
            job = data["jobs"][0]
            assert "job_id" in job
            assert "state" in job
            assert "document_type" in job
            assert "status" in job
        
        print(f"✓ GET /api/gov/jobs/history returns {data['total']} jobs")

    def test_get_property_records(self):
        """GET /api/gov/records/{property_id} - list fetched records for property"""
        # Use a property_id from previous tests
        property_id = "test_prop_ka"
        
        response = self.session.get(f"{BASE_URL}/api/gov/records/{property_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "records" in data
        assert "total" in data
        assert isinstance(data["records"], list)
        
        print(f"✓ GET /api/gov/records/{property_id} returns {data['total']} records")

    def test_caching_returns_cached_on_second_fetch(self):
        """Caching - second fetch of same state+doc+inputs should return CACHED"""
        # Use unique inputs for this test
        unique_survey = f"cache_test_{int(time.time())}"
        fetch_payload = {
            "state": "haryana",  # Use state with no captcha for faster processing
            "documentType": "JAMABANDI",
            "inputs": {"district": "Gurugram", "khasraNumber": unique_survey},
            "propertyId": "cache_test_prop"
        }
        
        # First fetch - should be PENDING
        first_resp = self.session.post(f"{BASE_URL}/api/gov/fetch", json=fetch_payload)
        assert first_resp.status_code == 200
        first_data = first_resp.json()
        
        if first_data["status"] == "CACHED":
            print("✓ First fetch already CACHED (from previous run)")
            return
        
        assert first_data["status"] == "PENDING"
        job_id = first_data["job_id"]
        print(f"  First fetch: PENDING, job_id={job_id}")
        
        # Wait for job to complete
        max_wait = 15
        for i in range(max_wait):
            time.sleep(1)
            poll_resp = self.session.get(f"{BASE_URL}/api/gov/job/{job_id}")
            if poll_resp.json().get("status") == "COMPLETED":
                print(f"  Job completed after {i+1} seconds")
                break
        
        # Second fetch - should be CACHED
        time.sleep(1)  # Small delay
        second_resp = self.session.post(f"{BASE_URL}/api/gov/fetch", json=fetch_payload)
        assert second_resp.status_code == 200
        second_data = second_resp.json()
        
        assert second_data["status"] == "CACHED", f"Expected CACHED, got {second_data['status']}"
        assert second_data["job_id"] is None
        assert "result" in second_data
        assert second_data["estimated_wait_time"] == 0
        
        print("✓ Second fetch returns CACHED instantly")


class TestGovDataBridgeEdgeCases:
    """Edge case tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        # Login
        self.session.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })
        if login_resp.status_code != 200:
            pytest.skip("Login failed")
        yield

    def test_fetch_missing_required_fields(self):
        """POST /api/gov/fetch - missing state or documentType returns 400"""
        # Missing state
        resp1 = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "documentType": "RTC",
            "inputs": {},
            "propertyId": "test"
        })
        assert resp1.status_code == 400
        
        # Missing documentType
        resp2 = self.session.post(f"{BASE_URL}/api/gov/fetch", json={
            "state": "karnataka",
            "inputs": {},
            "propertyId": "test"
        })
        assert resp2.status_code == 400
        
        print("✓ Missing required fields returns 400")

    def test_bulk_fetch_max_limit(self):
        """POST /api/gov/fetch-bulk - max 10 requests per bulk"""
        # Create 11 requests
        requests_list = [
            {"state": "karnataka", "documentType": "RTC", "inputs": {}, "propertyId": f"bulk_{i}"}
            for i in range(11)
        ]
        
        response = self.session.post(f"{BASE_URL}/api/gov/fetch-bulk", json={"requests": requests_list})
        assert response.status_code == 400
        assert "Maximum 10" in response.json().get("detail", "")
        
        print("✓ Bulk fetch rejects >10 requests")

    def test_job_not_found_returns_404(self):
        """GET /api/gov/job/{job_id} - non-existent job returns 404"""
        response = self.session.get(f"{BASE_URL}/api/gov/job/nonexistent_job_id_12345")
        assert response.status_code == 404
        print("✓ Non-existent job returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
