
try:
    from google import genai
    print("Has google.genai: Yes")
    print(dir(genai))
    if hasattr(genai, 'Client'):
        print("Has Client: Yes")
        # Try to init client with just api_key
        try:
             import os
             k = os.getenv("GEMINI_API_KEY") or "TEST"
             c = genai.Client(api_key=k)
             print("Client init success")
        except Exception as e:
             print(f"Client init failed: {e}")
except ImportError:
    print("Has google.genai: No")

try:
    import google.generativeai as old_genai
    print("Has google.generativeai: Yes")
except ImportError:
    print("Has google.generativeai: No")
