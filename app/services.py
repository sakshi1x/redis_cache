from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QuestionService:
    """Service class to handle question processing and response generation"""
    
    @staticmethod
    def process_question(question: str, user_name: str, employee_id: str) -> str:
        """
        Process the user's question and generate a response
        
        Args:
            question: The user's question
            user_name: Name of the user
            employee_id: Employee ID of the user
            
        Returns:
            str: Generated response to the question
        """
        logger.info(f"Processing question from {user_name} (ID: {employee_id}): {question}")
        
        # Simple response logic - you can extend this with more sophisticated processing
        if "hello" in question.lower() or "hi" in question.lower():
            return f"Hello {user_name}! How can I help you today?"
        
        elif "help" in question.lower():
            return f"Hi {user_name}, I'm here to help! Please ask me any question and I'll do my best to assist you."
        
        elif "name" in question.lower():
            return f"My name is AI Assistant. Nice to meet you, {user_name}!"
        
        elif "employee" in question.lower() or "id" in question.lower():
            return f"Your employee ID is {employee_id}. Is there anything specific you'd like to know about your account?"
        
        else:
            return f"Thank you for your question, {user_name}. I understand you're asking: '{question}'. This is a generic response - you can enhance this service with more specific logic based on your requirements."
    
    @staticmethod
    def validate_headers(user_name: Optional[str], employee_id: Optional[str]) -> tuple[bool, str]:
        """
        Validate the required headers
        
        Args:
            user_name: User name from header
            employee_id: Employee ID from header
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not user_name:
            return False, "Missing required header: user-name"
        
        if not employee_id:
            return False, "Missing required header: employee-id"
        
        if len(user_name.strip()) == 0:
            return False, "User name cannot be empty"
        
        if len(employee_id.strip()) == 0:
            return False, "Employee ID cannot be empty"
        
        return True, ""
