# Employee API with Redis Sessions & Semantic Caching

A comprehensive FastAPI application that demonstrates advanced Redis data structures, session management, analytics, and semantic caching capabilities. This application serves as a question-answering service for employees with intelligent caching and analytics features.

## 🚀 Features

### Core Features
- **FastAPI REST API** 
- **Redis Session Management**
- **User Authentication** 
- **Question-Answering Service** 

### Redis Data Structures
- **Redis Hashes** - User profiles with multiple fields
- **Redis Streams** - Question history with event logging
- **Redis Sorted Sets** - Time-based analytics and rankings
- **Redis Strings** - Session storage and caching

### Analytics & Tracking
- **User Statistics** - Track login count, questions asked, and activity
- **Question Analytics** - Category-based and time-based analytics
- **Global Analytics** - System-wide question statistics
- **Search Functionality** - Search through question history

### Semantic Caching
- **Vector Similarity Search** - Using OpenAI embeddings and Redis vector search
- **Semantic Routing** - Intelligent question routing based on semantic similarity
- **Hybrid Search** - Combining semantic and traditional search methods

## 🏗️ Architecture

```
app/
├── api/                    # API routes and endpoints
│   ├── auth/              # Authentication endpoints
│   ├── users/             # User management
│   └── analytics/         # Analytics endpoints
├── core/                  # Core configuration and session management
├── models/                # Pydantic models
├── services/              # Business logic and Redis clients
│   └── caching/          # Redis client implementations
└── utils/                # Utility functions and helpers

semantic_cahing/          # Semantic caching implementations
├── semantic_caching_ai_course.py  # OpenAI + Redis vector search
└── semantic_cahing.py    # Semantic routing with RedisVL
```

## 🛠️ Technology Stack

- **Backend**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database**: Redis 5.0.1
- **Validation**: Pydantic 2.5.0
- **Configuration**: Pydantic-settings 2.1.0
- **Semantic Search**: OpenAI Embeddings + Redis Vector Search
- **Semantic Routing**: RedisVL

## 📋 Prerequisites

- Python 3.8+
- Redis Server
- OpenAI API Key (for semantic features)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd redis_caching_session
   ```

2. **Install dependencies**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Using uv (recommended)
   uv sync
   ```

3. **Set up Redis**
   ```bash
   # Start Redis server
   redis-server
   
   # Or using Docker
   docker run -d -p 6379:6379 redis:latest
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your settings
   OPENAI_API_KEY=your_openai_api_key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Run with auto-reload
python main.py

# Or using uvicorn directly
uvicorn app.__main__:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
```bash
uvicorn app.__main__:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/signup` - Register new employee
- `POST /api/v1/auth/login` - Employee login
- `POST /api/v1/auth/ask` - Ask a question (requires authentication)

### User Management
- `GET /api/v1/users/profile/{employee_id}` - Get user profile
- `GET /api/v1/users/all` - Get all users (admin)
- `PUT /api/v1/users/profile/{employee_id}` - Update user profile
- `DELETE /api/v1/users/profile/{employee_id}` - Delete user profile

### Analytics
- `GET /api/v1/analytics/user/{employee_id}` - Get user analytics
- `GET /api/v1/analytics/global` - Get global analytics
- `GET /api/v1/analytics/category/{category}` - Get category analytics
- `GET /api/v1/analytics/time-based/{employee_id}` - Get time-based analytics

## 🔧 Redis Data Structures

### User Profiles (Redis Hashes)
```redis
user:employee_123
├── employee_id: "employee_123"
├── username: "john_doe"
├── password: "hashed_password"
├── department: "Engineering"
├── role: "Developer"
├── questions_asked: "15"
├── login_count: "25"
├── last_login: "1703123456"
├── created_at: "1703000000"
└── status: "active"
```

### Question History (Redis Streams)
```redis
user:employee_123:questions
├── 1703123456-0: {"question": "What is Redis?", "response": "...", "category": "technology"}
├── 1703123500-0: {"question": "How to use FastAPI?", "response": "...", "category": "programming"}
└── 1703123600-0: {"question": "Best practices for caching?", "response": "...", "category": "technology"}
```

### Analytics (Redis Sorted Sets)
```redis
user:employee_123:analytics
├── 1703123456-0: 1703123456
├── 1703123500-0: 1703123500
└── 1703123600-0: 1703123600

global:question_analytics
├── 1703123456-0: 1703123456
├── 1703123500-0: 1703123500
└── 1703123600-0: 1703123600

category:technology:questions
├── 1703123456-0: 1703123456
└── 1703123600-0: 1703123600
```

## 🧠 Semantic Caching

### OpenAI + Redis Vector Search
The application includes semantic caching using OpenAI embeddings and Redis vector search:

```python
# Features:
# - Vector similarity search using COSINE distance
# - HNSW (Hierarchical Navigable Small World) indexing
# - Hybrid search combining semantic and traditional methods
# - Support for multiple document types and genres
```

### Semantic Routing
Intelligent question routing based on semantic similarity:

```python
# Routes questions to appropriate handlers based on:
# - Technology questions → Tech handler
# - Sports questions → Sports handler  
# - Entertainment questions → Entertainment handler
# - Configurable distance thresholds
```

## 📊 Analytics Features

### User Analytics
- **Question Count**: Total questions asked by user
- **Category Distribution**: Questions grouped by category
- **Difficulty Analysis**: Questions grouped by difficulty level
- **Time-based Analytics**: Activity patterns over time

### Global Analytics
- **System-wide Statistics**: Total questions across all users
- **Category Distribution**: Popular question categories
- **Trend Analysis**: Question patterns over time

### Search & Filtering
- **Question Search**: Search through user's question history
- **Time Range Filtering**: Filter analytics by time period
- **Category Filtering**: Filter by question category

## 🔒 Security Features

- **Session Management**: Secure session handling with Redis
- **Password Hashing**: Secure password storage
- **Authentication Middleware**: Protected endpoints
- **CORS Configuration**: Configurable cross-origin requests

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_utils.py
```

## 📦 Development



### Project Structure
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── conftest.py        # Test configuration
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.__main__:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Required
REDIS_HOST=localhost
REDIS_PORT=6379
OPENAI_API_KEY=your_key

# Optional
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
SESSION_SECRET=your_session_secret
LOG_LEVEL=INFO
```

## 📈 Performance

### Redis Optimizations
- **Connection Pooling**: Efficient Redis connection management
- **Pipeline Operations**: Batch Redis operations for better performance
- **Key Expiration**: Automatic cleanup of old data
- **Indexed Queries**: Optimized search and retrieval

### Caching Strategy
- **User Profiles**: Long-term caching (1 year)
- **Sessions**: Short-term caching (1 hour)
- **Analytics**: Persistent storage with time-based indexing
- **Semantic Cache**: Vector-based similarity caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🔮 Future Enhancements

- [ ] Real-time notifications using Redis Pub/Sub
- [ ] Advanced analytics dashboard
- [ ] Machine learning-based question categorization
- [ ] Multi-language support
- [ ] GraphQL API
- [ ] Microservices architecture
- [ ] Kubernetes deployment
- [ ] Monitoring and alerting
