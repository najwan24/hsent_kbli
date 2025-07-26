#!/usr/bin/env python3
"""
ACSES Pilot Study - Phase 2B: Test Rate Limiting (Refactored)
This script tests API rate limiting for different Gemini models using consolidated src/ modules.

This is now a thin CLI wrapper that imports functionality from src/ modules.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

from src.api.gemini_client import GeminiClient
from src.utils.common import load_env_file, print_section_header


def main():
    """Main execution function using consolidated modules."""
    print_section_header("ACSES Pilot Study - Rate Limiting Test")
    
    # Load environment variables
    load_env_file()
    
    try:
        # Initialize Gemini client
        client = GeminiClient()
        
        # List available models
        print("🤖 Available models:")
        available_models = client.list_available_models()
        
        for i, (model_id, model_info) in enumerate(available_models.items(), 1):
            print(f"  {i}. {model_id}")
            print(f"     Description: {model_info['description']}")
            print(f"     Rate Limit: {model_info['rpm']} RPM")
            print(f"     Delay: {client.get_rate_limit_delay(model_id):.1f}s between requests")
            print()
        
        # Get user choice
        try:
            choice = int(input("Select model to test (number): ")) - 1
            model_ids = list(available_models.keys())
            
            if 0 <= choice < len(model_ids):
                selected_model = model_ids[choice]
                num_requests = int(input("Number of test requests (default 5): ") or "5")
                
                # Run the test
                print(f"\n🧪 Testing rate limiting for {selected_model}")
                print(f"📊 Rate limit: {available_models[selected_model]['rpm']} RPM")
                print(f"⏱️  Delay between requests: {client.get_rate_limit_delay(selected_model):.1f} seconds")
                print(f"🕒 Total test time: ~{client.get_rate_limit_delay(selected_model) * num_requests / 60:.1f} minutes")
                print("=" * 60)
                
                success_count = client.test_rate_limiting(selected_model, num_requests)
                
                print(f"\n📊 TEST RESULTS")
                print("=" * 30)
                print(f"✅ Successful requests: {success_count}/{num_requests}")
                print(f"📈 Success rate: {success_count/num_requests*100:.1f}%")
                
                if success_count == num_requests:
                    print("\n🎉 Rate limiting test PASSED!")
                    print("✅ All requests succeeded with proper delays")
                else:
                    print(f"\n⚠️  Rate limiting test PARTIAL SUCCESS")
                    print(f"   {num_requests - success_count} requests failed")
                
                return success_count == num_requests
                
            else:
                print("❌ Invalid choice")
                return False
                
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Test cancelled")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during rate limiting test: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
