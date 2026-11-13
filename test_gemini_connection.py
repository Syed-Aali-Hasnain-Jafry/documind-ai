
import os

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError


def main():
    # Load API key from .env
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("ERROR: API key is missing!")
        return

    # Connect to Gemini
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents="What is an invoice? Answer in one sentence."
        )

        print("SUCCESS! Gemini responded:")
        print(response.text)

    except APIError as error:
        if error.code == 503:
            print("Gemini is busy. Try again later.")
        else:
            print(f"Gemini API error: {error.code}")
            print(error.message)

    finally:
        client.close()


if __name__ == "__main__":
    main()
