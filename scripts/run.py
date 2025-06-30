#!/usr/bin/env python3
"""
Startup script for Natural Language SQL Tool
Handles environment validation and starts the server
"""

import os
import sys

def check_environment():
    """Check if required environment variables are set"""
    from app.core.config import config
    
    missing_vars = []
    
    if not config.OPENAI_API_KEY:
        missing_vars.append("OPENAI_API_KEY")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in a .env file or as environment variables.")
        print("Example .env file:")
        print("OPENAI_API_KEY=your_key_here")
        print("DATABASE_URL=postgresql://user:pass@localhost:5432/db")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🗃️  Natural Language SQL Tool")
    print("=" * 40)
    
    # Add parent directory to path so we can import app modules
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    from app.core.config import config
    
    print("✅ Environment variables configured")
    print(f"✅ Max query timeout: {config.MAX_QUERY_TIMEOUT}s")
    print(f"✅ Max result rows: {config.MAX_RESULT_ROWS}")
    
    # Start the server
    print("\n🚀 Starting server...")
    print("   Web interface: http://localhost:8000")
    print("   API docs: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        import uvicorn
        from app.main import app
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except ImportError:
        print("❌ uvicorn not installed. Installing dependencies...")
        os.system("pip install -r requirements.txt")
        print("Please run the script again.")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 