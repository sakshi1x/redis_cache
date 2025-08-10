#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
with the new folder structure.
"""

def test_imports():
    """Test all critical imports"""
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Core config import successful")
        
        from app.core.session import set_session_data, get_session_data
        print("✅ Core session import successful")
        
        # Test models imports
        from app.models.auth import Employee, EmployeeSignup, EmployeeLogin
        print("✅ Models auth import successful")
        
        # Test services imports
        from app.services.caching.redis_client import RedisHashClient, RedisStreamClient, RedisSortedSetClient
        print("✅ Services caching import successful")
        
        # Test utils imports
        from app.utils.helpers import require_authentication, get_authenticated_employee
        print("✅ Utils helpers import successful")
        
        # Test API imports
        from app.api.auth.routes import router as auth_router
        print("✅ API auth routes import successful")
        
        from app.api.users.routes import RedisUserProfiles
        print("✅ API users routes import successful")
        
        from app.api.analytics.routes import RedisQuestionAnalytics
        print("✅ API analytics routes import successful")
        
        # Test main app import
        from app.__main__ import app
        print("✅ Main app import successful")
        
        print("\n🎉 All imports successful! The new folder structure is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
