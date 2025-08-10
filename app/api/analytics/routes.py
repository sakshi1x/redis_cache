import json
import time
from typing import Optional, Dict, Any, List
import redis
from app.core.config import settings
from app.services.caching.redis_client import RedisStreamClient, RedisSortedSetClient
from app.utils.helpers import (
    format_redis_key, convert_numeric_fields, count_by_field, 
    filter_by_time_range, sort_by_timestamp, limit_results,
    validate_time_range, sanitize_search_term
)


class RedisQuestionAnalytics:
    """Redis Streams and Sorted Sets for question history and analytics using base clients"""
    
    def __init__(self):
        self.stream_client = RedisStreamClient()
        self.sorted_set_client = RedisSortedSetClient()
        self.numeric_fields = ["timestamp"]
    
    def log_question_event(self, employee_id: str, question: str, response: str, 
                          category: str = None, difficulty: str = None) -> Optional[str]:
        """Log question event to Redis Stream"""
        current_time = self.stream_client._get_current_timestamp()
        stream_key = format_redis_key(settings.USER_QUESTIONS_STREAM_PATTERN, employee_id=employee_id)
        
        # Set default values if not provided
        category = category or settings.DEFAULT_CATEGORY
        difficulty = difficulty or settings.DEFAULT_DIFFICULTY
        
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
        stream_id = self.stream_client.xadd_event(stream_key, event_data)
        if not stream_id:
            return None
        
        # Add to analytics sorted set with timestamp as score
        analytics_key = format_redis_key(settings.USER_ANALYTICS_KEY_PATTERN, employee_id=employee_id)
        self.sorted_set_client.zadd_members(analytics_key, {stream_id: current_time})
        
        # Add to global analytics
        self.sorted_set_client.zadd_members(settings.GLOBAL_ANALYTICS_KEY, {stream_id: current_time})
        
        # Add to category analytics
        category_key = format_redis_key(settings.CATEGORY_ANALYTICS_PATTERN, category=category)
        self.sorted_set_client.zadd_members(category_key, {stream_id: current_time})
        
        return stream_id
    
    def get_user_question_history(self, employee_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent question history from Stream"""
        stream_key = format_redis_key(settings.USER_QUESTIONS_STREAM_PATTERN, employee_id=employee_id)
        
        # Get recent events from stream
        events = self.stream_client.xrevrange_events(stream_key, count=count)
        
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
    
    def _get_question_details(self, employee_id: str, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed question data by stream ID"""
        stream_key = format_redis_key(settings.USER_QUESTIONS_STREAM_PATTERN, employee_id=employee_id)
        event_data = self.stream_client.xrange_events(stream_key, stream_id, stream_id)
        
        if event_data:
            _, data = event_data[0]
            return {
                "event_id": stream_id,
                "question": data.get("question"),
                "category": data.get("category"),
                "difficulty": data.get("difficulty"),
                "timestamp": int(data.get("timestamp", 0))
            }
        return None
    
    def _get_analytics_entries(self, analytics_key: str, start_time: Optional[int] = None, 
                             end_time: Optional[int] = None) -> List[str]:
        """Get analytics entries with optional time filtering"""
        if start_time is not None and end_time is not None:
            return self.sorted_set_client.zrange_by_score(analytics_key, start_time, end_time)
        else:
            return self.sorted_set_client.zrange_members(analytics_key)
    
    def get_user_analytics(self, employee_id: str, start_time: Optional[int] = None, 
                          end_time: Optional[int] = None) -> Dict[str, Any]:
        """Get user analytics from Sorted Set"""
        # Validate time range
        if not validate_time_range(start_time, end_time):
            return {}
        
        analytics_key = format_redis_key(settings.USER_ANALYTICS_KEY_PATTERN, employee_id=employee_id)
        
        # Get analytics entries
        entries = self._get_analytics_entries(analytics_key, start_time, end_time)
        
        # Get detailed data for each entry
        analytics_data = []
        for stream_id in entries:
            question_detail = self._get_question_details(employee_id, stream_id)
            if question_detail:
                analytics_data.append(question_detail)
        
        # Calculate analytics
        total_questions = len(analytics_data)
        categories = count_by_field(analytics_data, "category")
        difficulties = count_by_field(analytics_data, "difficulty")
        
        return {
            "total_questions": total_questions,
            "categories": categories,
            "difficulties": difficulties,
            "recent_questions": limit_results(analytics_data, 5)  # Last 5 questions
        }
    
    def _find_question_by_stream_id(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Find question details across all users by stream ID"""
        user_keys = self.stream_client.get_keys_by_pattern("user:*:questions")
        
        for user_key in user_keys:
            event_data = self.stream_client.xrange_events(user_key, stream_id, stream_id)
            if event_data:
                _, data = event_data[0]
                return {
                    "event_id": stream_id,
                    "question": data.get("question"),
                    "category": data.get("category"),
                    "difficulty": data.get("difficulty"),
                    "timestamp": int(data.get("timestamp", 0)),
                    "user_id": data.get("user_id")
                }
        return None
    
    def get_global_analytics(self, start_time: Optional[int] = None, 
                           end_time: Optional[int] = None) -> Dict[str, Any]:
        """Get global analytics from Sorted Set"""
        # Validate time range
        if not validate_time_range(start_time, end_time):
            return {}
        
        # Get global entries
        entries = self._get_analytics_entries(settings.GLOBAL_ANALYTICS_KEY, start_time, end_time)
        
        # Get category analytics
        category_stats = {}
        for stream_id in entries:
            question_detail = self._find_question_by_stream_id(stream_id)
            if question_detail:
                category = question_detail.get("category", "unknown")
                category_stats[category] = category_stats.get(category, 0) + 1
        
        return {
            "total_questions": len(entries),
            "category_distribution": category_stats,
            "time_range": {
                "start": start_time,
                "end": end_time
            }
        }
    
    def get_category_analytics(self, category: str, start_time: Optional[int] = None, 
                             end_time: Optional[int] = None) -> Dict[str, Any]:
        """Get analytics for specific category"""
        # Validate time range
        if not validate_time_range(start_time, end_time):
            return {}
        
        category_key = format_redis_key(settings.CATEGORY_ANALYTICS_PATTERN, category=category)
        
        # Get category entries
        entries = self._get_analytics_entries(category_key, start_time, end_time)
        
        # Get question details
        questions = []
        for stream_id in entries:
            question_detail = self._find_question_by_stream_id(stream_id)
            if question_detail:
                questions.append(question_detail)
        
        return {
            "category": category,
            "total_questions": len(questions),
            "questions": limit_results(questions, 10),  # Last 10 questions
            "time_range": {
                "start": start_time,
                "end": end_time
            }
        }
    
    def get_time_based_analytics(self, employee_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get analytics for specific time period"""
        current_time = self.stream_client._get_current_timestamp()
        start_time = current_time - (hours * 3600)
        
        analytics_key = format_redis_key(settings.USER_ANALYTICS_KEY_PATTERN, employee_id=employee_id)
        
        # Get entries in time range
        entries = self.sorted_set_client.zrange_by_score(analytics_key, start_time, current_time)
        
        # Group by hour
        hourly_stats = {}
        for stream_id in entries:
            question_detail = self._get_question_details(employee_id, stream_id)
            if question_detail:
                timestamp = question_detail.get("timestamp", 0)
                hour = timestamp - (timestamp % 3600)  # Round to hour
                hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
        
        return {
            "time_period_hours": hours,
            "total_questions": len(entries),
            "hourly_distribution": hourly_stats,
            "start_time": start_time,
            "end_time": current_time
        }
    
    def search_questions(self, employee_id: str, search_term: str) -> List[Dict[str, Any]]:
        """Search questions in user's history"""
        sanitized_term = sanitize_search_term(search_term)
        if not sanitized_term:
            return []
        
        stream_key = format_redis_key(settings.USER_QUESTIONS_STREAM_PATTERN, employee_id=employee_id)
        
        # Get all events from stream
        events = self.stream_client.xrange_events(stream_key)
        
        matching_questions = []
        for event_id, data in events:
            question = data.get("question", "").lower()
            if sanitized_term in question:
                matching_questions.append({
                    "event_id": event_id,
                    "question": data.get("question"),
                    "response": data.get("response"),
                    "category": data.get("category"),
                    "timestamp": int(data.get("timestamp", 0))
                })
        
        return sort_by_timestamp(matching_questions)
    
    def get_question_by_id(self, employee_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Get specific question by event ID"""
        return self._get_question_details(employee_id, event_id)
    
    def get_user_question_count(self, employee_id: str) -> int:
        """Get total number of questions asked by user"""
        analytics_key = format_redis_key(settings.USER_ANALYTICS_KEY_PATTERN, employee_id=employee_id)
        return self.sorted_set_client.zcard(analytics_key)
    
    def get_category_question_count(self, category: str) -> int:
        """Get total number of questions in a category"""
        category_key = format_redis_key(settings.CATEGORY_ANALYTICS_PATTERN, category=category)
        return self.sorted_set_client.zcard(category_key)
    
    def get_global_question_count(self) -> int:
        """Get total number of questions globally"""
        return self.sorted_set_client.zcard(settings.GLOBAL_ANALYTICS_KEY)


# Global analytics instance
question_analytics = RedisQuestionAnalytics()
