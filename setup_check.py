"""
Setup script for the Agentic Call Simulator

This script helps you configure the environment to run the agent simulator.
"""

import os
import sys
from dotenv import load_dotenv
def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ .env file not found!")
        print("📝 Creating .env template...")
        with open(env_path, 'w') as f:
            f.write("# REQUIRED: Set your OpenAI API key here\n")
            f.write("# Get your API key from: https://platform.openai.com/api-keys\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✅ .env file created. Please edit it with your OpenAI API key.")
        return False
    
    # Check if API key is set
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set in .env file!")
        print("🔑 Please edit .env file and add your OpenAI API key.")
        return False
    
    print("✅ Environment configured correctly!")
    return True

def check_packages():
    """Check if required packages are installed."""
    required_packages = [
        'langchain_openai',
        'gtts',
        'soundfile',
        'numpy',
        'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("📦 Run: pip install " + " ".join(missing))
        return False
    
    print("✅ All required packages installed!")
    return True

def main():
    print("🤖 Agentic Call Simulator Setup")
    print("=" * 40)
    
    env_ok = check_env_file()
    packages_ok = check_packages()
    
    if env_ok and packages_ok:
        print("\n🎉 Setup complete! You can now run:")
        print("   python examples/run_scripted.py")
    else:
        print("\n⚠️  Setup incomplete. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
