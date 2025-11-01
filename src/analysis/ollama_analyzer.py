import os
import requests
import json
import logging
import subprocess

import time

def analyze_car_data_ollama(car_data: dict, model: str) -> str:
    time.sleep(5)
    """
    Analyzes car data using a self-hosted Ollama model.

    Args:
        car_data: A dictionary containing car data.
        model: The name of the Ollama model to use.

    Returns:
        A string containing the analysis of the car data.
    """
    ollama_api_url = os.environ.get("OLLAMA_API_URL", "http://ollama.ollama.svc.cluster.local:11434/api/generate")
    prompt = f"""
    Analyze the following car listing and provide a summary of its pros and cons.
    Be concise and to the point.

    **Car Data:**
    - Title: {car_data.get('title')}
    - Price: {car_data.get('price')}
    - Mileage: {car_data.get('mileage')}
    - Location: {car_data.get('location')}
    - Link: {car_data.get('link')}

    **Analysis:**
    """

    try:
        logging.info(f"Ollama API URL: {ollama_api_url}")
        request_data = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        logging.info(f"Request Data: {json.dumps(request_data)}")
        headers = {"Content-Type": "application/json"}
        logging.info(f"Request Headers: {headers}")

        time.sleep(10)
        with requests.Session() as session:
            response = session.post(
                ollama_api_url,
                data=json.dumps(request_data),
                headers=headers
            )
            if response.status_code != 200:
                logging.error(f"Ollama API returned status code {response.status_code}")
                logging.error(f"Response headers: {response.headers}")
                logging.error(f"Response content: {response.content}")
            response.raise_for_status()

            full_response = []
            for line in response.iter_lines():
                if line:
                    try:
                        json_line = json.loads(line)
                        full_response.append(json_line.get("response", ""))
                    except json.JSONDecodeError:
                        # Ignore lines that are not valid JSON
                        pass
            return "".join(full_response)

    except Exception as e:
        return f"An unexpected error occurred during analysis: {e}"

if __name__ == '__main__':
    # Example usage
    sample_car_data = {
        'title': '2018 Honda Civic Type R',
        'price': '$35,000',
        'mileage': '30,000 miles',
        'location': 'Los Angeles, CA',
        'link': 'https://example.com/car123'
    }
    
    # To run this example, you need to have Ollama running.
    # You can customize the model and API URL if needed.
    analysis = analyze_car_data_ollama(sample_car_data, model="mistral")
    print(analysis)