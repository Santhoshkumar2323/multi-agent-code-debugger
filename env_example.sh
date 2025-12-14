# Environment Variables for Code Debugger Agent

# Gemini API Key (Required)
# Get your free API key from: https://ai.google.dev/
GEMINI_API_KEY=AIzaSyC-DFCeVAXw1DWvBuT6e3ozcOP0xF1Befg

# Optional: Model configuration
# Default: gemini-1.5-flash (free tier)
# Alternative: gemini-1.5-pro (more capable, paid)
GEMINI_MODEL=gemini-2.5-flash-lite

# Optional: Debugging settings
MAX_RETRIES=3
CODE_TIMEOUT=5

# SETUP INSTRUCTIONS:
# 1. Copy this file to .env: cp .env.example .env
# 2. Get your Gemini API key from https://ai.google.dev/
# 3. Replace 'your_gemini_api_key_here' with your actual key
# 4. Never commit .env to git (it's in .gitignore)
#
# Why .env file?
# - Keeps secrets out of code
# - Easy to change without code changes
# - Standard practice in production
# - Different keys for dev/staging/prod
