import os
import google.generativeai as genai

def analyze_car_data(car_data: dict) -> str:
    """
    Analyzes car data using the Gemini API.

    Args:
        car_data: A dictionary containing car data.

    Returns:
        A string containing the analysis of the car data.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

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
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
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
    
    # To run this example, you need to set the GEMINI_API_KEY environment variable.
    # For example, in your terminal:
    # export GEMINI_API_KEY='your_api_key'
    
    if os.getenv("GEMINI_API_KEY"):
        analysis = analyze_car_data(sample_car_data)
        print(analysis)
    else:
        print("Please set the GEMINI_API_KEY environment variable to run the example.")
