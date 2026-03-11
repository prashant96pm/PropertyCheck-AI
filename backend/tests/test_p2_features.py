"""
P2 Features Test Suite - Admin Panel & Enterprise API
Tests for: Admin endpoints, Enterprise API key generation, role management
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEnterpriseAPI:
    """Enterprise API Key Generation and Usage Tests"""
    
    def test_generate_api_key(self):
        """Test API key generation (no auth required)"""
        response = requests.post(
            f"{BASE_URL}/api/enterprise/v1/api-keys",
            params={"org_name": "TEST_P2_Org", "contact_email": "p2test@test.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("pck_")
        assert data["org_name"] == "TEST_P2_Org"
        assert data["plan"] == "trial"
        assert "rate_limit" in data
        # Store for later tests
        TestEnterpriseAPI.api_key = data["api_key"]
    
    def test_enterprise_verify_without_key(self):
        """Test enterprise verify returns 422 without API key"""
        response = requests.get(f"{BASE_URL}/api/enterprise/v1/verify/SOME_PROP_ID")
        assert response.status_code == 422  # Missing required header
    
    def test_enterprise_verify_with_invalid_key(self):
        """Test enterprise verify with invalid API key"""
        response = requests.get(
            f"{BASE_URL}/api/enterprise/v1/verify/SOME_PROP_ID",
            headers={"X-API-Key": "pck_invalid_key_12345"}
        )
        assert response.status_code == 401
        assert "Invalid" in response.json().get("detail", "")


class TestAdminEndpoints:
    """Admin Panel Backend Endpoints Tests"""
    
    @pytest.fixture(autouse=True)
    def setup_admin_user(self):
        """Register and setup admin user"""
        timestamp = int(time.time())
        email = f"test_p2_admin_{timestamp}@test.com"
        
        # Register user
        reg_resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"name": "P2 Admin Test", "email": email, "password": "testpass123"}
        )
        if reg_resp.status_code == 200:
            self.user = reg_resp.json()["user"]
            self.token = reg_resp.json()["access_token"]
            self.email = email
            # Set user as admin via MongoDB
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            async def set_admin():
                client = AsyncIOMotorClient('mongodb://localhost:27017')
                db = client['test_database']
                await db.users.update_one({'email': email}, {'$set': {'role': 'admin'}})
            asyncio.run(set_admin())
            
            # Re-login to get token with admin role
            login_resp = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": email, "password": "testpass123"}
            )
            if login_resp.status_code == 200:
                self.token = login_resp.json()["access_token"]
                self.user = login_resp.json()["user"]
    
    def test_admin_stats_without_auth(self):
        """Test admin stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 401
    
    def test_admin_stats_with_non_admin(self):
        """Test admin stats requires admin role"""
        # Register regular user
        timestamp = int(time.time())
        email = f"test_p2_regular_{timestamp}@test.com"
        reg_resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"name": "Regular User", "email": email, "password": "testpass123"}
        )
        assert reg_resp.status_code == 200
        token = reg_resp.json()["access_token"]
        
        # Try admin endpoint
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert "Admin" in response.json().get("detail", "")
    
    def test_admin_stats_success(self):
        """Test admin stats returns expected data"""
        if not hasattr(self, 'token'):
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected fields
        assert "total_users" in data
        assert "total_properties" in data
        assert "total_reports" in data
        assert "total_documents" in data
        assert "total_searches" in data
        assert "recent_users" in data
        assert isinstance(data["total_users"], int)
        assert isinstance(data["recent_users"], list)
    
    def test_admin_users_list(self):
        """Test admin users list endpoint"""
        if not hasattr(self, 'token'):
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
        
        # Verify user objects have expected fields
        if len(data["users"]) > 0:
            user = data["users"][0]
            assert "user_id" in user
            assert "email" in user
            assert "name" in user
            # Password should NOT be in response
            assert "password" not in user
    
    def test_admin_verifications_list(self):
        """Test admin verifications list endpoint"""
        if not hasattr(self, 'token'):
            pytest.skip("Admin token not available")
        
        response = requests.get(
            f"{BASE_URL}/api/admin/verifications",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "verifications" in data
        assert "total" in data
        assert isinstance(data["verifications"], list)
    
    def test_admin_update_user_role(self):
        """Test admin can update user roles"""
        if not hasattr(self, 'token'):
            pytest.skip("Admin token not available")
        
        # Create a test user to update
        timestamp = int(time.time())
        email = f"test_p2_role_target_{timestamp}@test.com"
        reg_resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={"name": "Role Target", "email": email, "password": "testpass123"}
        )
        assert reg_resp.status_code == 200
        target_user_id = reg_resp.json()["user"]["user_id"]
        
        # Update role to lawyer
        response = requests.put(
            f"{BASE_URL}/api/admin/users/{target_user_id}/role",
            params={"role": "lawyer"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
        assert "lawyer" in response.json().get("message", "")
        
        # Verify role updated
        users_resp = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        users = users_resp.json()["users"]
        target = next((u for u in users if u["user_id"] == target_user_id), None)
        assert target is not None
        assert target["role"] == "lawyer"
    
    def test_admin_update_role_invalid_value(self):
        """Test admin cannot set invalid role"""
        if not hasattr(self, 'token'):
            pytest.skip("Admin token not available")
        
        response = requests.put(
            f"{BASE_URL}/api/admin/users/some_user_id/role",
            params={"role": "superadmin"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 400


class TestAPIDocsPage:
    """Tests for API Documentation endpoint"""
    
    def test_api_key_generation_flow(self):
        """Test full API key generation flow"""
        # 1. Generate API key
        gen_resp = requests.post(
            f"{BASE_URL}/api/enterprise/v1/api-keys",
            params={"org_name": "TEST_FlowOrg", "contact_email": "flow@test.com"}
        )
        assert gen_resp.status_code == 200
        api_key = gen_resp.json()["api_key"]
        
        # 2. Key should be usable (404 expected for non-existent property)
        verify_resp = requests.get(
            f"{BASE_URL}/api/enterprise/v1/verify/nonexistent_prop",
            headers={"X-API-Key": api_key}
        )
        assert verify_resp.status_code == 404  # Not 401 (key works)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
