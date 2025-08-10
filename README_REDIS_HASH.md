# Redis Hash Implementation for User Profiles

This implementation demonstrates how to use Redis **Hash data structure** to create enhanced user profiles with persistent storage, analytics, and real-time updates.

## 🎯 What's Implemented

### **Redis Hash Data Structure**
- **Data Type**: Hash (HSET/HGETALL)
- **Use Case**: User profiles with multiple fields
- **Key Pattern**: `user:{employee_id}`

### **Enhanced User Profile Fields**
```bash
user:EMP001 = {
  "employee_id": "EMP001",
  "username": "john_doe", 
  "password": "secret123",
  "department": "Engineering",
  "role": "Developer",
  "questions_asked": "5",
  "login_count": "12",
  "last_login": "1703123456",
  "created_at": "1703000000",
  "status": "active"
}
```

## 🚀 New API Endpoints

### **1. Enhanced Signup** 
```http
POST /api/v1/auth/signup
```
**Features:**
- Creates Redis Hash profile with extended fields
- Stores department and role information
- Initializes counters (questions_asked: 0, login_count: 0)
- Returns complete profile data

**Request Body:**
```json
{
  "employee_id": "EMP001",
  "username": "john_doe",
  "password": "secret123",
  "department": "Engineering",
  "role": "Developer"
}
```

### **2. Enhanced Login**
```http
POST /api/v1/auth/login
```
**Features:**
- Updates login_count counter (HINCRBY)
- Updates last_login timestamp (HSET)
- Returns updated profile with statistics

### **3. Enhanced Ask Question**
```http
POST /api/v1/auth/ask
```
**Features:**
- Increments questions_asked counter (HINCRBY)
- Returns user statistics in response
- Tracks user engagement

### **4. Get User Profile**
```http
GET /api/v1/auth/profile
```
**Features:**
- Retrieves complete profile (HGETALL)
- Returns all user fields and statistics
- Requires authentication

### **5. Update User Profile**
```http
PUT /api/v1/auth/profile
```
**Features:**
- Updates specific fields (HSET)
- Supports department and role updates
- Returns updated profile

**Request Body:**
```json
{
  "department": "Product Management",
  "role": "Senior Developer"
}
```

### **6. Get User Statistics**
```http
GET /api/v1/auth/stats
```
**Features:**
- Retrieves user statistics (HMGET)
- Shows engagement metrics
- Requires authentication

## 🔧 Redis Hash Commands Used

### **Core Commands**
```bash
# Create/Update Profile
HSET user:EMP001 mapping "field1" "value1" "field2" "value2"

# Get Complete Profile  
HGETALL user:EMP001

# Get Specific Fields
HMGET user:EMP001 department role questions_asked

# Increment Counter
HINCRBY user:EMP001 questions_asked 1

# Update Single Field
HSET user:EMP001 last_login 1703123456

# Check Field Exists
HEXISTS user:EMP001 department

# Get Field Names
HKEYS user:EMP001

# Get Field Values
HVALS user:EMP001

# Get Hash Length
HLEN user:EMP001

# Delete Field
HDEL user:EMP001 status
```

## 📊 Data Structure Benefits

### **1. Atomic Operations**
- **HINCRBY**: Atomic counter increments
- **HSET**: Atomic field updates
- **Pipeline**: Batch operations for consistency

### **2. Memory Efficiency**
- Only store needed fields
- No duplicate data
- Compact storage format

### **3. Flexible Schema**
- Add new fields without migration
- Optional fields supported
- Dynamic field management

### **4. Fast Access**
- O(1) field access
- Efficient for partial reads
- Optimized for frequent updates

## 🧪 Testing the Implementation

### **Run the Test Script**
```bash
python test_redis_hash.py
```

### **Test with API**
```bash
# Start the server
python main.py

# Test signup
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "username": "john_doe",
    "password": "secret123",
    "department": "Engineering",
    "role": "Developer"
  }'

# Test login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secret123"
  }'

# Test ask question
curl -X POST "http://localhost:8000/api/v1/auth/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Redis?"}'

# Get profile
curl -X GET "http://localhost:8000/api/v1/auth/profile"
```

## 🔍 Redis CLI Exploration

### **Connect to Redis**
```bash
redis-cli
```

### **Explore User Data**
```bash
# List all user keys
KEYS user:*

# Get specific user profile
HGETALL user:EMP001

# Get user statistics
HMGET user:EMP001 questions_asked login_count last_login

# Check user activity
HGET user:EMP001 questions_asked
HGET user:EMP001 login_count
```

## 📈 Analytics Capabilities

### **User Engagement Tracking**
- Questions asked per user
- Login frequency
- Last activity timestamp
- Account creation date

### **Department Analytics**
- Users per department
- Activity by department
- Role distribution

### **Time-based Analysis**
- Login patterns
- Question frequency over time
- User retention metrics

## 🔒 Security Features

### **Data Persistence**
- Survives server restarts
- Redis persistence enabled
- Automatic expiration (1 year)

### **Access Control**
- Authentication required for profile access
- Session-based security
- Field-level access control

## 🚀 Production Considerations

### **Performance**
- Use Redis pipelines for batch operations
- Implement connection pooling
- Monitor memory usage

### **Scalability**
- Redis clustering for high availability
- Database sharding for large datasets
- Cache warming strategies

### **Monitoring**
- Track Redis memory usage
- Monitor hash field counts
- Alert on performance degradation

## 📚 Key Learnings

1. **Hash vs String**: Hashes are better for object-like data with multiple fields
2. **Atomic Operations**: Use HINCRBY for counters, HSET for updates
3. **Memory Efficiency**: Hashes use less memory than separate keys
4. **Flexibility**: Easy to add/remove fields without schema changes
5. **Performance**: O(1) access to individual fields

This implementation transforms a simple in-memory user system into a production-ready, scalable user profile management system using Redis Hash data structures.
