"""
Test Gemini API connection - Real integration test with clear success/failure output
"""
import os
import sys
import unittest
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ GEMINI NOT INSTALLED: google-generativeai package is not installed")
    sys.exit(1)


def test_gemini_connection():
    """Test actual Gemini API connection and response"""
    print("\n" + "="*70)
    print("GEMINI 2.5-FLASH API CONNECTION TEST")
    print("="*70)
    
    # Step 1: Load API key
    print("\n[1/4] Loading API key from .env...")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ FAILURE: GOOGLE_API_KEY not found in .env file")
        return False
    
    if len(api_key) < 10:
        print("❌ FAILURE: API key appears invalid (too short)")
        return False
    
    print(f"✅ SUCCESS: API key loaded ({api_key[:15]}...)")
    
    # Step 2: Configure Gemini
    print("\n[2/4] Configuring Gemini API...")
    try:
        genai.configure(api_key=api_key)
        print("✅ SUCCESS: Gemini configured")
    except Exception as e:
        print(f"❌ FAILURE: Failed to configure Gemini: {e}")
        return False
    
    # Step 3: Initialize model
    print("\n[3/4] Initializing gemini-2.5-flash model...")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ SUCCESS: Model initialized")
    except Exception as e:
        print(f"❌ FAILURE: Failed to initialize model: {e}")
        return False
    
    # Step 4: Generate content
    print("\n[4/4] Testing content generation with prompt 'Say hello'...")
    try:
        response = model.generate_content("Say hello")
        response_text = response.text.strip()
        
        if response_text:
            print(f"✅ SUCCESS: Generated response")
            print(f"\n   Response: {response_text[:100]}..." if len(response_text) > 100 else f"\n   Response: {response_text}")
            return True
        else:
            print("❌ FAILURE: Empty response from model")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ FAILURE: Content generation failed")
        
        # Parse error type for clarity
        if "ResourceExhausted" in error_msg or "429" in error_msg:
            print(f"   Reason: QUOTA EXCEEDED")
            print(f"   Details: Free tier daily limit reached")
            print(f"   Solution: Wait 24 hours for quota reset or upgrade to paid plan")
        elif "NotFound" in error_msg or "404" in error_msg:
            print(f"   Reason: MODEL NOT FOUND")
            print(f"   Details: Model not available or not supported")
        elif "PermissionDenied" in error_msg or "403" in error_msg:
            print(f"   Reason: INVALID API KEY")
            print(f"   Details: API key unauthorized or revoked")
        else:
            print(f"   Details: {error_msg[:200]}")
        
        return False


if __name__ == "__main__":
    success = test_gemini_connection()
    
    print("\n" + "="*70)
    if success:
        print("✅ ALL TESTS PASSED - Gemini API is working correctly")
        print("="*70)
        sys.exit(0)
    else:
        print("❌ TEST FAILED - Gemini API connection unsuccessful")
        print("="*70)
        sys.exit(1)

        # Configure API
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        model = genai.GenerativeModel(self.model_name)
        
        # Generate content
        response = model.generate_content("Hello")

        mock_configure.assert_called_once()
        self.assertEqual(response.text, "Hello from Gemini!")


if __name__ == '__main__':
    unittest.main()