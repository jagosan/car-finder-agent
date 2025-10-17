import os
import requests
import json

def analyze_car_data_ollama(car_data: dict, model: str) -> str:
    """
    Analyzes car data using a self-hosted Ollama model.

    Args:
        car_data: A dictionary containing car data.
        model: The name of the Ollama model to use.

    Returns:
        A string containing the analysis of the car data.
    """
    ollama_api_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
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
        response = requests.post(
            ollama_api_url,
            data=json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False
            }),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        # The actual response is a JSON object, and the content is in the 'response' key.
        return response.json().get("response", "No response from model.")
    except requests.exceptions.RequestException as e:
        return f"An error occurred during analysis: {e}"

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