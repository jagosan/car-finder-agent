import requests
import json

def test_requests():
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            data=json.dumps({
                "model": "mistral",
                "prompt": "Why is the sky blue?",
                "stream": False,
                "options": {"num_predict": 20}
            }),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    test_requests()
