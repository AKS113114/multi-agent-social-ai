import uvicorn
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("================================================================")
    print("🚀 Starting Prodigal AI Multi-Agent Social Media Company")
    print("Local LLM Runtime: Ollama (http://localhost:11434)")
    print("Web Dashboard: http://localhost:8000")
    print("================================================================")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
