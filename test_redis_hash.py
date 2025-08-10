#!/usr/bin/env python3
"""
Test script to demonstrate Redis Hash functionality for user profiles
"""

import redis
import json
import time
from app.config import settings

def test_redis_hash_profiles():
    """Test Redis Hash operations for user profiles"""
    
    # Connect to Redis
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True
    )
    
    print("🔍 Testing Redis Hash Data Structure for User Profiles")
    print("=" * 60)
    
    # Test 1: Create user profile with HSET
    print("\n1️⃣ Creating user profile with HSET...")
    user_key = "user:EMP001"
    current_time = int(time.time())
    
    profile_data = {
        "employee_id": "EMP001",
        "username": "john_doe",
        "password": "secret123",
        "department": "Engineering",
        "role": "Developer",
        "questions_asked": "0",
        "login_count": "0",
        "last_login": str(current_time),
        "created_at": str(current_time),
        "status": "active"
    }
    
    # Use HSET with mapping for multiple fields
    redis_client.hset(user_key, mapping=profile_data)
    print(f"✅ Created profile for user: {user_key}")
    
    # Test 2: Get all profile data with HGETALL
    print("\n2️⃣ Retrieving complete profile with HGETALL...")
    profile = redis_client.hgetall(user_key)
    print(f"📋 Complete profile data:")
    for field, value in profile.items():
        print(f"   {field}: {value}")
    
    # Test 3: Get specific fields with HMGET
    print("\n3️⃣ Getting specific fields with HMGET...")
    specific_fields = redis_client.hmget(user_key, "department", "role", "questions_asked")
    print(f"🏢 Department: {specific_fields[0]}")
    print(f"👤 Role: {specific_fields[1]}")
    print(f"❓ Questions Asked: {specific_fields[2]}")
    
    # Test 4: Increment counter with HINCRBY
    print("\n4️⃣ Incrementing questions asked counter with HINCRBY...")
    redis_client.hincrby(user_key, "questions_asked", 1)
    redis_client.hincrby(user_key, "questions_asked", 1)
    redis_client.hincrby(user_key, "questions_asked", 1)
    
    updated_questions = redis_client.hget(user_key, "questions_asked")
    print(f"❓ Updated questions asked: {updated_questions}")
    
    # Test 5: Update login activity
    print("\n5️⃣ Updating login activity...")
    new_login_time = int(time.time())
    redis_client.hincrby(user_key, "login_count", 1)
    redis_client.hset(user_key, "last_login", new_login_time)
    
    login_count = redis_client.hget(user_key, "login_count")
    last_login = redis_client.hget(user_key, "last_login")
    print(f"🔢 Login count: {login_count}")
    print(f"🕒 Last login: {last_login}")
    
    # Test 6: Check if field exists with HEXISTS
    print("\n6️⃣ Checking field existence with HEXISTS...")
    has_department = redis_client.hexists(user_key, "department")
    has_salary = redis_client.hexists(user_key, "salary")
    print(f"🏢 Has department field: {has_department}")
    print(f"💰 Has salary field: {has_salary}")
    
    # Test 7: Get all field names with HKEYS
    print("\n7️⃣ Getting all field names with HKEYS...")
    field_names = redis_client.hkeys(user_key)
    print(f"📝 All fields: {field_names}")
    
    # Test 8: Get all values with HVALS
    print("\n8️⃣ Getting all values with HVALS...")
    field_values = redis_client.hvals(user_key)
    print(f"📊 All values: {field_values}")
    
    # Test 9: Get hash length with HLEN
    print("\n9️⃣ Getting hash length with HLEN...")
    hash_length = redis_client.hlen(user_key)
    print(f"📏 Number of fields: {hash_length}")
    
    # Test 10: Delete specific field with HDEL
    print("\n🔟 Deleting specific field with HDEL...")
    redis_client.hdel(user_key, "status")
    remaining_fields = redis_client.hkeys(user_key)
    print(f"📝 Remaining fields after deleting 'status': {remaining_fields}")
    
    # Test 11: Show final profile
    print("\n1️⃣1️⃣ Final profile state:")
    final_profile = redis_client.hgetall(user_key)
    print(json.dumps(final_profile, indent=2))
    
    # Test 12: Clean up
    print("\n🧹 Cleaning up test data...")
    redis_client.delete(user_key)
    print("✅ Test data cleaned up")
    
    print("\n🎉 Redis Hash testing completed!")
    print("\n📚 Key Redis Hash Commands Used:")
    print("   HSET key field value          # Set field value")
    print("   HSET key mapping              # Set multiple fields")
    print("   HGETALL key                   # Get all fields")
    print("   HMGET key field1 field2       # Get specific fields")
    print("   HINCRBY key field increment   # Increment numeric field")
    print("   HEXISTS key field             # Check if field exists")
    print("   HKEYS key                     # Get all field names")
    print("   HVALS key                     # Get all values")
    print("   HLEN key                      # Get number of fields")
    print("   HDEL key field                # Delete field")

if __name__ == "__main__":
    test_redis_hash_profiles()
