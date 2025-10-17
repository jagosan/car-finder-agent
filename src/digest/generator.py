import jinja2
import os

def generate_digest(cars: list[dict]) -> str:
    """
    Generates an HTML digest from a list of car data.

    Args:
        cars: A list of dictionaries, where each dictionary represents a car.

    Returns:
        A string containing the HTML digest.
    """
    template_path = os.path.join(os.path.dirname(__file__), 'template.html')
    with open(template_path) as f:
        template_content = f.read()

    template = jinja2.Template(template_content)
    return template.render(cars=cars)

def send_email(html_content: str, recipient: str, subject: str = "Daily Car Digest"):
    """
    Sends an email with the given HTML content.

    (For now, this function just prints the email content to the console.)

    Args:
        html_content: The HTML content of the email.
        recipient: The email address of the recipient.
        subject: The subject of the email.
    """
    print("--- Sending Email ---")
    print(f"To: {recipient}")
    print(f"Subject: {subject}")
    print("\n" + html_content)
    print("--- Email Sent ---")

if __name__ == '__main__':
    # Example usage
    sample_cars = [
        {
            'title': '2018 Honda Civic Type R',
            'price': '$35,000',
            'mileage': '30,000 miles',
            'location': 'Los Angeles, CA',
            'link': 'https://example.com/car123',
            'analysis': 'This is a great car for enthusiasts. The price is a bit high, but the mileage is low.'
        },
        {
            'title': '2020 Toyota Camry TRD',
            'price': '$32,000',
            'mileage': '25,000 miles',
            'location': 'San Francisco, CA',
            'link': 'https://example.com/car456',
            'analysis': 'A reliable and sporty sedan. Good value for the price.'
        }
    ]

    html_digest = generate_digest(sample_cars)
    send_email(html_digest, "test@example.com")
