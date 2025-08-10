import json
import time
from typing import Optional, Dict, Any, List, Union
import redis
from app.config import settings


class RedisBaseClient:
    """Base Redis client with common operations and error handling"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
    
    def _safe_execute(self, operation: str, func, *args, **kwargs) -> Any:
        """Safely execute Redis operations with error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {operation}: {e}")
            return None
    
    def _format_key(self, pattern: str, **kwargs) -> str:
        """Format Redis key using pattern and parameters"""
        return pattern.format(**kwargs)
    
    def _convert_numeric_fields(self, data: Dict[str, Any], 
                               numeric_fields: List[str]) -> Dict[str, Any]:
        """Convert string fields to integers where appropriate"""
        result = data.copy()
        for field in numeric_fields:
            if field in result and result[field]:
                try:
                    result[field] = int(result[field])
                except (ValueError, TypeError):
                    result[field] = 0
        return result
    
    def _get_current_timestamp(self) -> int:
        """Get current Unix timestamp"""
        return int(time.time())
    
    def _json_dumps(self, data: Dict[str, Any]) -> str:
        """Safely serialize data to JSON"""
        try:
            return json.dumps(data)
        except (TypeError, ValueError) as e:
            print(f"Error serializing data to JSON: {e}")
            return "{}"
    
    def _json_loads(self, data: str) -> Optional[Dict[str, Any]]:
        """Safely deserialize JSON data"""
        try:
            return json.loads(data) if data else None
        except (TypeError, ValueError) as e:
            print(f"Error deserializing JSON data: {e}")
            return None
    
    def key_exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        return self._safe_execute("key_exists", self.redis_client.exists, key) or False
    
    def delete_key(self, key: str) -> bool:
        """Delete a key from Redis"""
        return self._safe_execute("delete_key", self.redis_client.delete, key) or False
    
    def get_keys_by_pattern(self, pattern: str) -> List[str]:
        """Get keys matching a pattern"""
        return self._safe_execute("get_keys_by_pattern", self.redis_client.keys, pattern) or []
    
    def get_key_type(self, key: str) -> Optional[str]:
        """Get the type of a Redis key"""
        return self._safe_execute("get_key_type", self.redis_client.type, key)
    
    def set_expiry(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key"""
        return self._safe_execute("set_expiry", self.redis_client.expire, key, seconds) or False


class RedisHashClient(RedisBaseClient):
    """Redis Hash operations client"""
    
    def hset_mapping(self, key: str, mapping: Dict[str, Any], 
                    expire_seconds: Optional[int] = None) -> bool:
        """Set multiple hash fields with optional expiration"""
        try:
            pipeline = self.redis_client.pipeline()
            pipeline.hset(key, mapping=mapping)
            if expire_seconds:
                pipeline.expire(key, expire_seconds)
            pipeline.execute()
            return True
        except Exception as e:
            print(f"Error in hset_mapping: {e}")
            return False
    
    def hget_all(self, key: str) -> Optional[Dict[str, Any]]:
        """Get all hash fields"""
        return self._safe_execute("hget_all", self.redis_client.hgetall, key)
    
    def hget_fields(self, key: str, fields: List[str]) -> List[Optional[str]]:
        """Get specific hash fields"""
        return self._safe_execute("hget_fields", self.redis_client.hmget, key, fields) or []
    
    def hset_field(self, key: str, field: str, value: Any) -> bool:
        """Set a single hash field"""
        return self._safe_execute("hset_field", self.redis_client.hset, key, field, value) or False
    
    def hincr_by(self, key: str, field: str, amount: int = 1) -> Optional[int]:
        """Increment a hash field by amount"""
        return self._safe_execute("hincr_by", self.redis_client.hincrby, key, field, amount)


class RedisStreamClient(RedisBaseClient):
    """Redis Stream operations client"""
    
    def xadd_event(self, stream_key: str, event_data: Dict[str, Any]) -> Optional[str]:
        """Add event to stream"""
        return self._safe_execute("xadd_event", self.redis_client.xadd, stream_key, event_data)
    
    def xrange_events(self, stream_key: str, start: str = "-", 
                     end: str = "+", count: Optional[int] = None) -> List[tuple]:
        """Get events from stream range"""
        args = [stream_key, start, end]
        if count:
            args.extend(["COUNT", count])
        return self._safe_execute("xrange_events", self.redis_client.xrange, *args) or []
    
    def xrevrange_events(self, stream_key: str, count: Optional[int] = None) -> List[tuple]:
        """Get recent events from stream in reverse order"""
        args = [stream_key]
        if count:
            args.extend(["COUNT", count])
        return self._safe_execute("xrevrange_events", self.redis_client.xrevrange, *args) or []


class RedisSortedSetClient(RedisBaseClient):
    """Redis Sorted Set operations client"""
    
    def zadd_members(self, key: str, mapping: Dict[str, float]) -> int:
        """Add members to sorted set with scores"""
        return self._safe_execute("zadd_members", self.redis_client.zadd, key, mapping) or 0
    
    def zrange_members(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get members from sorted set by rank"""
        return self._safe_execute("zrange_members", self.redis_client.zrange, key, start, end) or []
    
    def zrange_by_score(self, key: str, min_score: Union[int, float], 
                       max_score: Union[int, float]) -> List[str]:
        """Get members from sorted set by score range"""
        return self._safe_execute("zrange_by_score", self.redis_client.zrangebyscore, 
                                 key, min_score, max_score) or []
    
    def zcard(self, key: str) -> int:
        """Get cardinality (number of members) of sorted set"""
        return self._safe_execute("zcard", self.redis_client.zcard, key) or 0


class RedisStringClient(RedisBaseClient):
    """Redis String operations client"""
    
    def set_value(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """Set string value with optional expiration"""
        try:
            if expire_seconds:
                return self._safe_execute("set_value", self.redis_client.setex, 
                                        key, expire_seconds, value) or False
            else:
                return self._safe_execute("set_value", self.redis_client.set, key, value) or False
        except Exception as e:
            print(f"Error in set_value: {e}")
            return False
    
    def get_value(self, key: str) -> Optional[str]:
        """Get string value"""
        return self._safe_execute("get_value", self.redis_client.get, key)
    
    def set_json(self, key: str, data: Dict[str, Any], 
                expire_seconds: Optional[int] = None) -> bool:
        """Set JSON data as string"""
        json_data = self._json_dumps(data)
        return self.set_value(key, json_data, expire_seconds)
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get and parse JSON data"""
        data = self.get_value(key)
        return self._json_loads(data) if data else None
