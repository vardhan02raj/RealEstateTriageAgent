"""
Real Estate Triage Agent - CLI
A helpful assistant that collects lead information from Buyers, Sellers, and Renters.
"""

import os

from dotenv import load_dotenv
load_dotenv()

from google import genai

from agent_logic import save_lead

# API key is read from the environment - never store it in code
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Error: Set your Google API key first: export GOOGLE_API_KEY='your-key'")
    print("Run this in your terminal before starting the agent.")
    exit(1)
client = genai.Client(api_key=api_key)


def get_welcome_message() -> str:
    """Use AI to generate a friendly welcome message."""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Write one short, friendly sentence welcoming someone to a real estate assistant. Be warm and professional. No quotes."
        )
        return response.text.strip()
    except Exception:
        return "Welcome to the Real Estate Triage Agent!"


def run_buyer_flow() -> dict:
    """Collect information from a buyer."""
    lead = {"type": "Buyer"}
    print("\nGreat! I'd love to help you find your dream property.\n")

    lead["budget"] = input("What is your budget? ").strip()
    lead["location"] = input("What is your preferred location? ").strip()
    lead["property_type"] = input("What type of property? (e.g., Apartment, Villa, House): ").strip()

    return lead


def run_seller_flow() -> dict:
    """Collect information from a seller."""
    lead = {"type": "Seller"}
    print("\nGreat! I'd love to help you sell your property.\n")

    lead["address"] = input("What is the property address? ").strip()
    lead["expected_price"] = input("What is your expected price? ").strip()
    lead["urgency"] = input("How urgent is the sale? (e.g., ASAP, 1 month, 3 months): ").strip()

    return lead


def run_renter_flow() -> dict:
    """Collect information from a renter."""
    lead = {"type": "Renter"}
    print("\nGreat! I'd love to help you find a rental.\n")

    lead["monthly_budget"] = input("What is your monthly budget? ").strip()
    lead["move_in_date"] = input("When do you need to move in? ").strip()

    return lead


def main():
    """Main conversation loop."""
    print("=" * 50)
    print(f"  {get_welcome_message()}")
    print("  I'm here to help Buyers, Sellers, and Renters.")
    print("  Type 'exit' at any time to quit.")
    print("=" * 50)

    while True:
        print("\nAre you a Buyer, Seller, or Renter?")
        user_input = input("You: ").strip().lower()

        if user_input == "exit":
            print("\nThank you for using the Real Estate Triage Agent. Goodbye!")
            break

        if "buyer" in user_input:
            lead = run_buyer_flow()
        elif "seller" in user_input:
            lead = run_seller_flow()
        elif "renter" in user_input:
            lead = run_renter_flow()
        else:
            print("\nI didn't quite catch that. Please say Buyer, Seller, or Renter.")
            continue

        save_lead(lead)
        print("\n✓ Thanks for sharing! We're working on it and will get back to you soon.\n")
        print("Thank you for using the Real Estate Triage Agent. Goodbye!")
        break


if __name__ == "__main__":
    main()
