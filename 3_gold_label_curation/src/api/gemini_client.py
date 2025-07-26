"""
Consolidated Gemini API Client
Handles all Gemini API interactions, rate limiting, and error handling.
"""

import os
import time
import re
import google.generativeai as genai
from typing import Dict, Any, Optional
from datetime import datetime

# Available models and their configurations
AVAILABLE_MODELS = {
    "models/gemini-1.5-flash-latest": {"rpm": 15, "description": "Gemini 1.5 Flash (Latest)"},
    "models/gemini-1.5-pro-latest": {"rpm": 2, "description": "Gemini 1.5 Pro (Latest)"},
    "models/gemini-2.5-flash-lite": {"rpm": 15, "description": "Gemini 2.5 Flash Lite"},
}

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 2


class GeminiClient:
    """Centralized Gemini API client with rate limiting and error handling."""
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = DEFAULT_MAX_RETRIES):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Gemini API key (if None, reads from GEMINI_API_KEY env var)
            max_retries: Maximum number of API call retries
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.max_retries = max_retries
        self._configure_api()
        
    def _configure_api(self) -> None:
        """Configure the Gemini API client."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found. Please set it before running.")
        
        genai.configure(api_key=self.api_key)
        print("✅ Gemini API configured successfully")
    
    @staticmethod
    def get_available_models() -> Dict[str, Dict[str, Any]]:
        """Get available models and their configurations."""
        return AVAILABLE_MODELS.copy()
    
    @staticmethod
    def list_available_models() -> None:
        """Display available models and their configurations."""
        print("🤖 Available Models:")
        print("=" * 60)
        for model, config in AVAILABLE_MODELS.items():
            print(f"📋 {model}")
            print(f"   Description: {config['description']}")
            print(f"   Rate Limit: {config['rpm']} requests per minute")
            delay = (60.0 / config['rpm']) * 1.1
            print(f"   Delay between requests: {delay:.1f} seconds")
            print()
    
    @staticmethod
    def get_rate_limit_delay(model_name: str) -> float:
        """
        Calculate the minimum delay between requests to respect rate limits.
        
        Args:
            model_name: The model being used
            
        Returns:
            Minimum delay in seconds between requests
        """
        rpm = AVAILABLE_MODELS.get(model_name, {}).get("rpm", 15)
        return (60.0 / rpm) * 1.1
    
    def generate_content(self, prompt: str, model_name: str, temperature: float = 0.7,
                        top_p: float = 0.8, top_k: int = 40, 
                        max_output_tokens: int = 2048) -> str:
        """
        Call the Gemini API with retry logic and rate limiting.
        
        Args:
            prompt: The formatted prompt
            model_name: Name of the model to use
            temperature: Temperature parameter for generation
            top_p: Top-p parameter for generation
            top_k: Top-k parameter for generation
            max_output_tokens: Maximum output tokens
            
        Returns:
            Raw response text from the API
            
        Raises:
            ValueError: If the model is not available or response is empty
            Exception: If all retry attempts fail
        """
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} not available. Use get_available_models() to see options.")
        
        model = genai.GenerativeModel(model_name)
        
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
        )
        
        for attempt in range(self.max_retries):
            try:
                response = model.generate_content(prompt, generation_config=generation_config)
                
                if response.text:
                    return response.text
                else:
                    raise ValueError("Empty response from API")
                    
            except Exception as e:
                error_str = str(e)
                print(f"API call attempt {attempt + 1} failed: {error_str[:100]}...")
                
                # Handle rate limiting errors
                if "ResourceExhausted" in error_str or "429" in error_str:
                    # Check for suggested retry delay in error message
                    retry_delay_match = re.search(r'retry_delay.*?seconds: (\d+)', error_str)
                    if retry_delay_match:
                        suggested_delay = int(retry_delay_match.group(1))
                        print(f"  Rate limit hit, waiting {suggested_delay}s as suggested...")
                        time.sleep(suggested_delay)
                    else:
                        # Use calculated rate limit delay
                        rate_delay = self.get_rate_limit_delay(model_name)
                        print(f"  Rate limit hit, waiting {rate_delay:.1f}s...")
                        time.sleep(rate_delay)
                elif attempt < self.max_retries - 1:
                    # Exponential backoff for other errors
                    time.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                else:
                    # Last attempt failed, re-raise the exception
                    raise
    
    def test_connection(self, model_name: str = "models/gemini-2.5-flash-lite") -> bool:
        """
        Test the API connection with a simple prompt.
        
        Args:
            model_name: Model to test with
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_prompt = "Say 'Hello' in JSON format: {\"message\": \"Hello\"}"
            response = self.generate_content(test_prompt, model_name, temperature=0.1)
            return len(response.strip()) > 0
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False


# Convenience functions for backward compatibility
def configure_gemini_api() -> GeminiClient:
    """Create and configure a Gemini API client."""
    return GeminiClient()

def get_rate_limit_delay(model_name: str) -> float:
    """Get rate limit delay for a model."""
    return GeminiClient.get_rate_limit_delay(model_name)

def list_available_models() -> None:
    """List available models."""
    GeminiClient.list_available_models()
