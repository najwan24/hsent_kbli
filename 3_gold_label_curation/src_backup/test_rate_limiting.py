#!/usr/bin/env python3
"""
Test rate limiting for different Gemini models.
"""
import os
import time
import google.generativeai as genai
from datetime import datetime

# Load environment
try:
    from dotenv import load_dotenv
    from pathlib import Path
    dotenv_path = Path(__file__).parent.parent / '.env'
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
except ImportError:
    pass

# Rate limiting configuration
RPM_LIMITS = {
    "models/gemini-1.5-flash-latest": 15,  # 15 RPM for free tier
    "models/gemini-1.5-pro-latest": 2,    # 2 RPM for free tier
    "models/gemini-2.5-flash-lite": 15,   # 15 RPM for free tier
}

def get_rate_limit_delay(model_name: str) -> float:
    """Calculate the minimum delay between requests."""
    rpm = RPM_LIMITS.get(model_name, 15)
    return (60.0 / rpm) * 1.1  # 10% buffer

def test_rate_limiting(model_name: str, num_requests: int = 5):
    """
    Test rate limiting by making multiple requests with proper delays.
    
    Args:
        model_name: The model to test
        num_requests: Number of test requests to make
    """
    print(f"🧪 Testing rate limiting for {model_name}")
    
    # Configure API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    # Calculate timing
    rpm_limit = RPM_LIMITS.get(model_name, 15)
    delay = get_rate_limit_delay(model_name)
    
    print(f"📊 Rate limit: {rpm_limit} RPM")
    print(f"⏱️  Delay between requests: {delay:.1f} seconds")
    print(f"🕒 Total test time: ~{delay * num_requests / 60:.1f} minutes")
    print("=" * 50)
    
    # Simple test prompt
    test_prompt = "What is 2+2? Respond with just the number."
    
    successful_requests = 0
    failed_requests = 0
    
    for i in range(num_requests):
        print(f"\n📤 Request {i+1}/{num_requests} at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            start_time = time.time()
            response = model.generate_content(test_prompt)
            processing_time = time.time() - start_time
            
            if response.text:
                successful_requests += 1
                print(f"✅ Success ({processing_time:.2f}s): {response.text.strip()}")
            else:
                failed_requests += 1
                print("❌ Empty response")
                
        except Exception as e:
            failed_requests += 1
            error_str = str(e)
            if "ResourceExhausted" in error_str or "429" in error_str:
                print(f"⚠️  Rate limit exceeded: {error_str[:100]}...")
            else:
                print(f"❌ Error: {error_str[:100]}...")
        
        # Wait before next request (except for last one)
        if i < num_requests - 1:
            print(f"⏳ Waiting {delay:.1f}s...")
            time.sleep(delay)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 RESULTS:")
    print(f"✅ Successful requests: {successful_requests}")
    print(f"❌ Failed requests: {failed_requests}")
    print(f"📈 Success rate: {successful_requests / num_requests * 100:.1f}%")
    
    if failed_requests == 0:
        print("🎉 All requests successful! Rate limiting is working correctly.")
    else:
        print("⚠️  Some requests failed. You may need to increase the delay.")

def main():
    """Main function."""
    print("🚀 Gemini Rate Limiting Test")
    print("Available models:")
    for i, model in enumerate(RPM_LIMITS.keys(), 1):
        print(f"  {i}. {model} ({RPM_LIMITS[model]} RPM)")
    
    try:
        choice = int(input("\nSelect model to test (number): ")) - 1
        models = list(RPM_LIMITS.keys())
        
        if 0 <= choice < len(models):
            selected_model = models[choice]
            num_requests = int(input("Number of test requests (default 5): ") or "5")
            test_rate_limiting(selected_model, num_requests)
        else:
            print("❌ Invalid choice")
            
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Cancelled")

if __name__ == "__main__":
    main()
