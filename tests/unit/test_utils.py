import pytest
from app.utils.helpers import (
    validate_time_range, sanitize_search_term, format_redis_key,
    convert_numeric_fields, count_by_field, group_by_field,
    filter_by_time_range, sort_by_timestamp, limit_results
)


class TestUtils:
    """Test utility functions"""
    
    def test_validate_time_range(self):
        """Test time range validation"""
        # Valid ranges
        assert validate_time_range(100, 200) == True
        assert validate_time_range(100, 100) == True
        assert validate_time_range(None, 200) == True
        assert validate_time_range(100, None) == True
        assert validate_time_range(None, None) == True
        
        # Invalid ranges
        assert validate_time_range(200, 100) == False
    
    def test_sanitize_search_term(self):
        """Test search term sanitization"""
        assert sanitize_search_term("  Hello World  ") == "hello world"
        assert sanitize_search_term("") == ""
        assert sanitize_search_term(None) == ""
        assert sanitize_search_term("UPPERCASE") == "uppercase"
    
    def test_format_redis_key(self):
        """Test Redis key formatting"""
        pattern = "user:{employee_id}:questions"
        result = format_redis_key(pattern, employee_id="EMP001")
        assert result == "user:EMP001:questions"
    
    def test_convert_numeric_fields(self):
        """Test numeric field conversion"""
        data = {
            "questions_asked": "10",
            "login_count": "5",
            "name": "John",
            "age": "30"
        }
        numeric_fields = ["questions_asked", "login_count", "age"]
        
        result = convert_numeric_fields(data, numeric_fields)
        
        assert result["questions_asked"] == 10
        assert result["login_count"] == 5
        assert result["age"] == 30
        assert result["name"] == "John"  # Non-numeric field unchanged
    
    def test_count_by_field(self):
        """Test counting by field"""
        items = [
            {"category": "tech", "name": "John"},
            {"category": "tech", "name": "Jane"},
            {"category": "hr", "name": "Bob"},
            {"category": "tech", "name": "Alice"}
        ]
        
        result = count_by_field(items, "category")
        
        assert result["tech"] == 3
        assert result["hr"] == 1
    
    def test_group_by_field(self):
        """Test grouping by field"""
        items = [
            {"category": "tech", "name": "John"},
            {"category": "tech", "name": "Jane"},
            {"category": "hr", "name": "Bob"}
        ]
        
        result = group_by_field(items, "category")
        
        assert len(result["tech"]) == 2
        assert len(result["hr"]) == 1
        assert result["tech"][0]["name"] == "John"
        assert result["hr"][0]["name"] == "Bob"
    
    def test_filter_by_time_range(self):
        """Test time range filtering"""
        items = [
            {"timestamp": 100, "name": "John"},
            {"timestamp": 200, "name": "Jane"},
            {"timestamp": 300, "name": "Bob"}
        ]
        
        # Filter with start time only
        result = filter_by_time_range(items, "timestamp", start_time=150)
        assert len(result) == 2
        assert result[0]["name"] == "Jane"
        assert result[1]["name"] == "Bob"
        
        # Filter with end time only
        result = filter_by_time_range(items, "timestamp", end_time=250)
        assert len(result) == 2
        assert result[0]["name"] == "John"
        assert result[1]["name"] == "Jane"
        
        # Filter with both start and end time
        result = filter_by_time_range(items, "timestamp", start_time=150, end_time=250)
        assert len(result) == 1
        assert result[0]["name"] == "Jane"
    
    def test_sort_by_timestamp(self):
        """Test timestamp sorting"""
        items = [
            {"timestamp": 300, "name": "Bob"},
            {"timestamp": 100, "name": "John"},
            {"timestamp": 200, "name": "Jane"}
        ]
        
        # Sort in descending order (default)
        result = sort_by_timestamp(items)
        assert result[0]["name"] == "Bob"
        assert result[1]["name"] == "Jane"
        assert result[2]["name"] == "John"
        
        # Sort in ascending order
        result = sort_by_timestamp(items, reverse=False)
        assert result[0]["name"] == "John"
        assert result[1]["name"] == "Jane"
        assert result[2]["name"] == "Bob"
    
    def test_limit_results(self):
        """Test result limiting"""
        items = [
            {"name": "John"},
            {"name": "Jane"},
            {"name": "Bob"},
            {"name": "Alice"}
        ]
        
        # Limit to 2 results
        result = limit_results(items, 2)
        assert len(result) == 2
        assert result[0]["name"] == "John"
        assert result[1]["name"] == "Jane"
        
        # Limit to 0 results
        result = limit_results(items, 0)
        assert len(result) == 0
        
        # Limit more than available
        result = limit_results(items, 10)
        assert len(result) == 4
