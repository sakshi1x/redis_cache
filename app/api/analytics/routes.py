import json
import time
from typing import Optional, Dict, Any, List
import redis
from app.core.config import settings
from app.services.caching.redis_client import (
    RedisStreamClient,
    RedisSortedSetClient,
    RedisHashClient,
)
from app.utils.helpers import (
    convert_numeric_fields, count_by_field, 
    filter_by_time_range, sort_by_timestamp, limit_results,
    validate_time_range, sanitize_search_term
)


class RedisQuestionAnalytics:
    """Redis Hashes and Sorted Sets for question history and analytics using base clients"""
    
    def __init__(self):
        self.stream_client = RedisStreamClient()
        self.sorted_set_client = RedisSortedSetClient()
        self.hash_client = RedisHashClient()
        self.numeric_fields = ["timestamp"]
    
    def log_question_event(self, employee_id: str, question: str, response: str, 
                          category: str = None, difficulty: str = None) -> Optional[str]:
        """Log question event to Redis as one hash per event.

        Key format: app:user:{employee_id}:questions:{event_id}:hash
        Fields: question, response, category, difficulty, timestamp, user_id
        """
        current_time = self.hash_client._get_current_timestamp()
        
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

        # Generate an event id (millisecond timestamp to improve uniqueness)
        try:
            event_id = str(int(time.time() * 1000))
        except Exception:
            event_id = str(current_time)

        # Store event as its own hash where fields are the keys of event_data
        # Key: app:user:{employee_id}:questions:{event_id}:hash
        event_hash_key = self.hash_client.build_key_parts("user", employee_id, "questions", event_id, "hash")
        ok = self.hash_client.hset_mapping(event_hash_key, event_data)
        if not ok:
            return None
        
        # Add to analytics sorted set with timestamp as score
        analytics_key = self.sorted_set_client.build_key_parts("user", employee_id, "question_timestamps", "zset")
        self.sorted_set_client.zadd_members(analytics_key, {event_id: current_time})
        
        # Add to global analytics
        global_key = self.sorted_set_client.build_key("analytics", "global_analytics", "questions")
        self.sorted_set_client.zadd_members(global_key, {event_id: current_time})
        
        # Add to category analytics
        category_key = self.sorted_set_client.build_key("analytics", "category_analytics", category)
        self.sorted_set_client.zadd_members(category_key, {event_id: current_time})

        # Add to difficulty analytics scoped by category (sibling namespace)
        # Key: app:analytics:difficulty_analytics:{difficulty}:category:{category}
        difficulty_by_category_key = self.sorted_set_client.build_key_parts(
            "analytics", "difficulty_analytics", difficulty, "category", category
        )
        self.sorted_set_client.zadd_members(difficulty_by_category_key, {event_id: current_time})

        # Update per-user hash analytics (aggregates)
        user_hash_analytics_key = self.hash_client.build_key_parts("user", employee_id, "hash_analytics")
        self.hash_client.hincr_by(user_hash_analytics_key, "total_questions", 1)
        self.hash_client.hset_field(user_hash_analytics_key, "last_question_timestamp", str(current_time))
        
        return event_id
    
    def get_user_question_history(self, employee_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent question history. Reads per-event hashes."""
        # Keys like: app:user:{employee_id}:questions:{event_id}:hash
        pattern = self.hash_client.build_pattern_parts("user", employee_id, "questions", "*", "hash")
        event_hash_keys = self.hash_client.get_keys_by_pattern(pattern) or []

        question_history: List[Dict[str, Any]] = []
        for key in event_hash_keys:
            # Extract event_id from key (it's the element right before "hash")
            parts = key.split(":")
            try:
                event_id = parts[parts.index("questions") + 1]
            except Exception:
                # Fallback: skip malformed keys
                continue
            data = self.hash_client.hget_all(key) or {}
            if not data:
                continue
            question_history.append({
                "event_id": event_id,
                "question": data.get("question"),
                "response": data.get("response"),
                "category": data.get("category"),
                "difficulty": data.get("difficulty"),
                "timestamp": int(data.get("timestamp", 0))
            })

        # Sort by timestamp desc and return top N
        question_history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return question_history[:count]
    
    def _get_question_details(self, employee_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed question data by event ID from per-event hash"""
        event_hash_key = self.hash_client.build_key_parts("user", employee_id, "questions", event_id, "hash")
        data = self.hash_client.hget_all(event_hash_key) or {}
        if not data:
            return None
        return {
            "event_id": event_id,
            "question": data.get("question"),
            "category": data.get("category"),
            "difficulty": data.get("difficulty"),
            "timestamp": int(data.get("timestamp", 0))
        }
    
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
        
        analytics_key = self.sorted_set_client.build_key_parts("user", employee_id, "question_timestamps", "zset")
        
        # Get analytics entries
        entries = self._get_analytics_entries(analytics_key, start_time, end_time)
        
        # Get detailed data for each entry
        analytics_data = []
        for event_id in entries:
            question_detail = self._get_question_details(employee_id, event_id)
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
    
    def _find_question_by_stream_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Find question details across all users by event ID in Hashes"""
        # Find across all users by looking up the specific event-id-based key
        pattern = self.hash_client.build_pattern_parts("user", "*", "questions", event_id, "hash")
        keys = self.hash_client.get_keys_by_pattern(pattern) or []
        for key in keys:
            data = self.hash_client.hget_all(key) or {}
            if not data:
                continue
            # Extract user_id from data or from key
            user_id = data.get("user_id")
            if not user_id:
                parts = key.split(":")
                try:
                    user_id = parts[parts.index("user") + 1]
                except Exception:
                    user_id = None
            return {
                "event_id": event_id,
                "question": data.get("question"),
                "category": data.get("category"),
                "difficulty": data.get("difficulty"),
                "timestamp": int(data.get("timestamp", 0)),
                "user_id": user_id,
            }
        return None
    
    def get_global_analytics(self, start_time: Optional[int] = None, 
                           end_time: Optional[int] = None) -> Dict[str, Any]:
        """Get global analytics from Sorted Set"""
        # Validate time range
        if not validate_time_range(start_time, end_time):
            return {}
        
        # Get global entries
        global_key = self.sorted_set_client.build_key("analytics", "global_analytics", "questions")
        entries = self._get_analytics_entries(global_key, start_time, end_time)
        
        # Get category and difficulty analytics
        category_stats = {}
        difficulty_stats = {}
        for event_id in entries:
            question_detail = self._find_question_by_stream_id(event_id)
            if question_detail:
                category = question_detail.get("category", "unknown")
                category_stats[category] = category_stats.get(category, 0) + 1
                difficulty = question_detail.get("difficulty", "unknown")
                difficulty_stats[difficulty] = difficulty_stats.get(difficulty, 0) + 1
        
        return {
            "total_questions": len(entries),
            "category_distribution": category_stats,
            "difficulty_distribution": difficulty_stats,
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
        
        category_key = self.sorted_set_client.build_key("analytics", "category_analytics", category)
        # Difficulty sub-keys in sibling namespace, scoped by this category
        difficulty_folder_pattern = self.sorted_set_client.build_pattern_parts(
            "analytics", "difficulty_analytics", "*", "category", category
        )
        
        # Get category entries
        entries = self._get_analytics_entries(category_key, start_time, end_time)
        
        # Get question details
        questions = []
        for stream_id in entries:
            question_detail = self._find_question_by_stream_id(stream_id)
            if question_detail:
                questions.append(question_detail)
        
        # Compute difficulty distribution within this category
        difficulty_stats = count_by_field(questions, "difficulty")

        # Also fetch difficulty totals from the difficulty-by-category sub-keys
        difficulty_totals = {}
        difficulty_keys = self.sorted_set_client.get_keys_by_pattern(difficulty_folder_pattern)
        for dkey in difficulty_keys:
            total = self.sorted_set_client.zcard(dkey)
            # key format: app:analytics:difficulty_analytics:{difficulty}:category:{category}
            parts = dkey.split(":")
            # difficulty is immediately after 'difficulty_analytics'
            diff_index = parts.index("difficulty_analytics") + 1 if "difficulty_analytics" in parts else -1
            diff_value = parts[diff_index] if diff_index != -1 and diff_index < len(parts) else "unknown"
            difficulty_totals[diff_value] = total

        return {
            "category": category,
            "total_questions": len(questions),
            "difficulty_distribution": difficulty_stats,
            "questions": limit_results(questions, 10),  # Last 10 questions
            "difficulty_totals": difficulty_totals,
            "time_range": {
                "start": start_time,
                "end": end_time
            }
        }
    
    def get_time_based_analytics(self, employee_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get analytics for specific time period"""
        current_time = self.stream_client._get_current_timestamp()
        start_time = current_time - (hours * 3600)
        
        analytics_key = self.sorted_set_client.build_key_parts("user", employee_id, "question_timestamps", "zset")
        
        # Get entries in time range
        entries = self.sorted_set_client.zrange_by_score(analytics_key, start_time, current_time)
        
        # Group by hour
        hourly_stats = {}
        for event_id in entries:
            question_detail = self._get_question_details(employee_id, event_id)
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
        
        # Get all per-event hashes
        pattern = self.hash_client.build_pattern_parts("user", employee_id, "questions", "*", "hash")
        event_hash_keys = self.hash_client.get_keys_by_pattern(pattern) or []

        matching_questions: List[Dict[str, Any]] = []
        for key in event_hash_keys:
            parts = key.split(":")
            try:
                event_id = parts[parts.index("questions") + 1]
            except Exception:
                continue
            data = self.hash_client.hget_all(key) or {}
            question = (data.get("question", "") or "").lower()
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
        analytics_key = self.sorted_set_client.build_key_parts("user", employee_id, "question_timestamps", "zset")
        return self.sorted_set_client.zcard(analytics_key)
    
    def get_category_question_count(self, category: str) -> int:
        """Get total number of questions in a category"""
        category_key = self.sorted_set_client.build_key("analytics", "category_analytics", category)
        return self.sorted_set_client.zcard(category_key)
    
    def get_global_question_count(self) -> int:
        """Get total number of questions globally"""
        global_key = self.sorted_set_client.build_key("analytics", "global_analytics", "questions")
        return self.sorted_set_client.zcard(global_key)


# Global analytics instance
question_analytics = RedisQuestionAnalytics()
