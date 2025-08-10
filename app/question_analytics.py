import json
import time
from typing import Optional, Dict, Any, List
import redis
from app.config import settings


class RedisQuestionAnalytics:
    """Redis Streams and Sorted Sets for question history and analytics"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
    
    def log_question_event(self, employee_id: str, question: str, response: str, 
                          category: str = "general", difficulty: str = "beginner") -> str:
        """Log question event to Redis Stream"""
        try:
            current_time = int(time.time())
            stream_key = f"user:{employee_id}:questions"
            
            # Create event data
            event_data = {
                "question": question,
                "response": response,
                "category": category,
                "difficulty": difficulty,
                "timestamp": str(current_time),
                "user_id": employee_id
            }
            
            # Add to stream with auto-generated ID
            stream_id = self.redis_client.xadd(stream_key, event_data)
            
            # Add to analytics sorted set with timestamp as score
            analytics_key = f"user:{employee_id}:analytics"
            self.redis_client.zadd(analytics_key, {stream_id: current_time})
            
            # Add to global analytics
            global_analytics_key = "global:question_analytics"
            self.redis_client.zadd(global_analytics_key, {stream_id: current_time})
            
            # Add to category analytics
            category_key = f"category:{category}:questions"
            self.redis_client.zadd(category_key, {stream_id: current_time})
            
            return stream_id
        except Exception as e:
            print(f"Error logging question event: {e}")
            return None
    
    def get_user_question_history(self, employee_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent question history from Stream"""
        try:
            stream_key = f"user:{employee_id}:questions"
            
            # Get recent events from stream
            events = self.redis_client.xrevrange(stream_key, count=count)
            
            question_history = []
            for event_id, data in events:
                question_history.append({
                    "event_id": event_id,
                    "question": data.get("question"),
                    "response": data.get("response"),
                    "category": data.get("category"),
                    "difficulty": data.get("difficulty"),
                    "timestamp": int(data.get("timestamp", 0))
                })
            
            return question_history
        except Exception as e:
            print(f"Error getting question history: {e}")
            return []
    
    def get_user_analytics(self, employee_id: str, start_time: Optional[int] = None, 
                          end_time: Optional[int] = None) -> Dict[str, Any]:
        """Get user analytics from Sorted Set"""
        try:
            analytics_key = f"user:{employee_id}:analytics"
            
            # Get all analytics entries for user
            if start_time and end_time:
                entries = self.redis_client.zrangebyscore(analytics_key, start_time, end_time)
            else:
                entries = self.redis_client.zrange(analytics_key, 0, -1)
            
            # Get detailed data for each entry
            analytics_data = []
            for stream_id in entries:
                stream_key = f"user:{employee_id}:questions"
                event_data = self.redis_client.xrange(stream_key, stream_id, stream_id)
                
                if event_data:
                    _, data = event_data[0]
                    analytics_data.append({
                        "event_id": stream_id,
                        "question": data.get("question"),
                        "category": data.get("category"),
                        "difficulty": data.get("difficulty"),
                        "timestamp": int(data.get("timestamp", 0))
                    })
            
            # Calculate analytics
            total_questions = len(analytics_data)
            categories = {}
            difficulties = {}
            
            for entry in analytics_data:
                category = entry.get("category", "unknown")
                difficulty = entry.get("difficulty", "unknown")
                
                categories[category] = categories.get(category, 0) + 1
                difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
            
            return {
                "total_questions": total_questions,
                "categories": categories,
                "difficulties": difficulties,
                "recent_questions": analytics_data[:5]  # Last 5 questions
            }
        except Exception as e:
            print(f"Error getting user analytics: {e}")
            return {}
    
    def get_global_analytics(self, start_time: Optional[int] = None, 
                           end_time: Optional[int] = None) -> Dict[str, Any]:
        """Get global analytics from Sorted Set"""
        try:
            global_key = "global:question_analytics"
            
            # Get global entries
            if start_time and end_time:
                entries = self.redis_client.zrangebyscore(global_key, start_time, end_time)
            else:
                entries = self.redis_client.zrange(global_key, 0, -1)
            
            # Get category analytics
            category_stats = {}
            for stream_id in entries:
                # Find which user this belongs to
                user_keys = self.redis_client.keys("user:*:questions")
                
                for user_key in user_keys:
                    event_data = self.redis_client.xrange(user_key, stream_id, stream_id)
                    if event_data:
                        _, data = event_data[0]
                        category = data.get("category", "unknown")
                        category_stats[category] = category_stats.get(category, 0) + 1
                        break
            
            return {
                "total_questions": len(entries),
                "category_distribution": category_stats,
                "time_range": {
                    "start": start_time,
                    "end": end_time
                }
            }
        except Exception as e:
            print(f"Error getting global analytics: {e}")
            return {}
    
    def get_category_analytics(self, category: str, start_time: Optional[int] = None, 
                             end_time: Optional[int] = None) -> Dict[str, Any]:
        """Get analytics for specific category"""
        try:
            category_key = f"category:{category}:questions"
            
            # Get category entries
            if start_time and end_time:
                entries = self.redis_client.zrangebyscore(category_key, start_time, end_time)
            else:
                entries = self.redis_client.zrange(category_key, 0, -1)
            
            # Get question details
            questions = []
            for stream_id in entries:
                # Find which user this belongs to
                user_keys = self.redis_client.keys("user:*:questions")
                
                for user_key in user_keys:
                    event_data = self.redis_client.xrange(user_key, stream_id, stream_id)
                    if event_data:
                        _, data = event_data[0]
                        questions.append({
                            "event_id": stream_id,
                            "question": data.get("question"),
                            "user_id": data.get("user_id"),
                            "difficulty": data.get("difficulty"),
                            "timestamp": int(data.get("timestamp", 0))
                        })
                        break
            
            return {
                "category": category,
                "total_questions": len(questions),
                "questions": questions[:10],  # Last 10 questions
                "time_range": {
                    "start": start_time,
                    "end": end_time
                }
            }
        except Exception as e:
            print(f"Error getting category analytics: {e}")
            return {}
    
    def get_time_based_analytics(self, employee_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get analytics for specific time period"""
        try:
            current_time = int(time.time())
            start_time = current_time - (hours * 3600)
            
            analytics_key = f"user:{employee_id}:analytics"
            
            # Get entries in time range
            entries = self.redis_client.zrangebyscore(analytics_key, start_time, current_time)
            
            # Group by hour
            hourly_stats = {}
            for stream_id in entries:
                stream_key = f"user:{employee_id}:questions"
                event_data = self.redis_client.xrange(stream_key, stream_id, stream_id)
                
                if event_data:
                    _, data = event_data[0]
                    timestamp = int(data.get("timestamp", 0))
                    hour = timestamp - (timestamp % 3600)  # Round to hour
                    
                    if hour not in hourly_stats:
                        hourly_stats[hour] = 0
                    hourly_stats[hour] += 1
            
            return {
                "time_period_hours": hours,
                "total_questions": len(entries),
                "hourly_distribution": hourly_stats,
                "start_time": start_time,
                "end_time": current_time
            }
        except Exception as e:
            print(f"Error getting time-based analytics: {e}")
            return {}
    
    def search_questions(self, employee_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search questions in user's history"""
        try:
            stream_key = f"user:{employee_id}:questions"
            
            # Get all events from stream
            events = self.redis_client.xrange(stream_key)
            
            matching_questions = []
            for event_id, data in events:
                question = data.get("question", "").lower()
                if search_term.lower() in question:
                    matching_questions.append({
                        "event_id": event_id,
                        "question": data.get("question"),
                        "response": data.get("response"),
                        "category": data.get("category"),
                        "timestamp": int(data.get("timestamp", 0))
                    })
            
            return matching_questions
        except Exception as e:
            print(f"Error searching questions: {e}")
            return []
    
    def get_question_by_id(self, employee_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Get specific question by event ID"""
        try:
            stream_key = f"user:{employee_id}:questions"
            event_data = self.redis_client.xrange(stream_key, event_id, event_id)
            
            if event_data:
                _, data = event_data[0]
                return {
                    "event_id": event_id,
                    "question": data.get("question"),
                    "response": data.get("response"),
                    "category": data.get("category"),
                    "difficulty": data.get("difficulty"),
                    "timestamp": int(data.get("timestamp", 0))
                }
            
            return None
        except Exception as e:
            print(f"Error getting question by ID: {e}")
            return None


# Global analytics instance
question_analytics = RedisQuestionAnalytics()
