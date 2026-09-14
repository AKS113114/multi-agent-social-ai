import uvicorn
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("================================================================")
    print("🚀 Starting Prodigal AI Multi-Agent Social Media Company")
    print(f"Web Dashboard Port: {port}")
    print("================================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
