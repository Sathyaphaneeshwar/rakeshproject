# backend/rate_limited_llm.py
from groq import Groq
import os
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
import time

load_dotenv()

class RateLimitedGroqClient:
    """Groq client with rate limiting: 6 requests per minute"""
    
    CALLS_PER_MINUTE = 6
    ONE_MINUTE = 60
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.client = Groq(api_key=self.api_key)
        self.request_count = 0
        
        # Create a rate-limited chat interface
        self.chat = RateLimitedChat(self.client, self)
    
    def reset_counter(self):
        """Reset request counter (called every minute)"""
        self.request_count = 0

class RateLimitedChat:
    """Wrapper for chat.completions with rate limiting"""
    
    def __init__(self, groq_client, rate_limiter):
        self.groq_client = groq_client
        self.rate_limiter = rate_limiter
        self.completions = RateLimitedCompletions(groq_client, rate_limiter)

class RateLimitedCompletions:
    """Wrapper for completions.create with rate limiting"""
    
    def __init__(self, groq_client, rate_limiter):
        self.groq_client = groq_client
        self.rate_limiter = rate_limiter
    
    @sleep_and_retry
    @limits(calls=6, period=60)
    def create(self, **kwargs):
        """Rate-limited create call"""
        self.rate_limiter.request_count += 1
        print(f"    [Rate Limiter] Request #{self.rate_limiter.request_count} this minute")
        
        return self.groq_client.chat.completions.create(**kwargs)

# Create singleton instance
groq_client = RateLimitedGroqClient()

if __name__ == "__main__":
    print("Testing rate limiter with proper interface")
    
    for i in range(8):
        print(f"\nRequest {i+1}/8:")
        try:
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": f"Say 'Request {i+1}'"}],
                model="openai/gpt-oss-20b",
                max_tokens=50
            )
            print(f"  ✓ Response: {response.choices[0].message.content}")
        except Exception as e:
            print(f"  ✗ Error: {e}")