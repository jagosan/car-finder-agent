import subprocess
import time
import requests
import os
import signal

def test_app():
    try:
        # Start the app in the background
        app_process = subprocess.Popen(
            ["/home/jmacleod/repos/car-finder-agent/venv/bin/python3", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        print(f"Started app with PID: {app_process.pid}")

        # Wait for the app to start
        time.sleep(10)

        # Check if the process is still running
        if app_process.poll() is not None:
            print("App process terminated unexpectedly.")
            stdout, stderr = app_process.communicate()
            print(f"Stdout: {stdout.decode()}")
            print(f"Stderr: {stderr.decode()}")
            return

        # Make a request to the app
        print("Making request to the app...")
        response = requests.get("http://localhost:5000/")
        response.raise_for_status()

        # Check the response
        if response.json().get("message") == "Hello from Flask Backend!":
            print("Backend is running correctly!")
        else:
            print(f"Unexpected response: {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Kill the app process
        if 'app_process' in locals() and app_process.poll() is None:
            print(f"Killing app process {app_process.pid}")
            os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)

if __name__ == '__main__':
    test_app()
