import uvicorn
import os
import sys

# Ensure the current directory (backend) is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting StudioFlow AI Backend...")
    print("Docs available at http://localhost:8000/docs")
    # Run the application using the module path 'app.main:app'
    # This requires 'backend' to be the current working directory or in path
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
