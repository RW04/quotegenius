# run.py
import os
import subprocess
import time
import argparse
import webbrowser
from threading import Thread

def run_command(command, name=None):
    """Run a command in a subprocess."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        shell=True
    )
    
    prefix = f"[{name}] " if name else ""
    
    for line in process.stdout:
        print(f"{prefix}{line}", end="")
    
    process.wait()
    return process.returncode

def setup_environment():
    """Set up the environment."""
    print("Setting up environment...")
    
    # Create .env file with OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:
        key = input("Enter your OpenAI API key: ")
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={key}\n")
    
    # Install requirements
    print("Installing requirements...")
    run_command("pip install -r requirements.txt")
    
    # Generate mock data
    print("Generating mock data...")
    run_command("python generate_mock_data.py")

def run_api_server():
    """Run the FastAPI server."""
    print("Starting API server...")
    run_command("uvicorn app:app --host 0.0.0.0 --port 8000 --reload", name="API")

def run_streamlit_app():
    """Run the Streamlit app."""
    print("Starting Streamlit app...")
    run_command("streamlit run app_ui.py", name="UI")

def main():
    parser = argparse.ArgumentParser(description="Run the QuoteGenius application")
    parser.add_argument("--skip-setup", action="store_true", help="Skip environment setup")
    parser.add_argument("--ui-only", action="store_true", help="Run only the UI in demo mode")
    args = parser.parse_args()
    
    if not args.skip_setup:
        setup_environment()
    
    if args.ui_only:
        print("Running in UI-only demo mode...")
        run_streamlit_app()
    else:
        # Run API and UI in separate threads
        api_thread = Thread(target=run_api_server)
        ui_thread = Thread(target=run_streamlit_app)
        
        api_thread.daemon = True
        ui_thread.daemon = True
        
        api_thread.start()
        time.sleep(5)  # Wait for API to start before launching UI
        ui_thread.start()
        
        # Open browser
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    main()