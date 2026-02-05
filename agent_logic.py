"""
Core logic for the Real Estate Triage Agent.
Used by both CLI (agent.py) and web app (app.py).
Extracts only relevant data from user's free-form responses.
"""

import csv
import os

# Load .env so env vars are available (app.py and agent.py also load, but this ensures it for direct imports)
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from pathlib import Path

FIELDNAMES = [
    "timestamp", "type", "budget", "location", "property_type",
    "address", "expected_price", "urgency", "monthly_budget", "move_in_date"
]

# Prompts to extract and NORMALIZE - output clean, short values for the table
EXTRACT_PROMPTS = {
    "type": "Extract ONLY: Buyer, Seller, or Renter. Reply with exactly one word. Message: ",
    "budget": "Extract the budget amount. NORMALIZE: convert 'lacks' to 'lakh', remove words like 'around', 'approximately'. Output format: '60 lakh' or '50 lakh'. Just number + lakh/cr/$ etc. Message: ",
    "location": "Extract the location/city/area. NORMALIZE: clean format like 'Palasia, Indore' or 'Indore, MP'. No extra words. Message: ",
    "property_type": "Extract the property type. NORMALIZE: remove 'a', 'an', 'the'. Output: 'Villa', 'Apartment', '3BHK', etc. Just the type. Message: ",
    "address": "Extract the property address. Clean format, no extra words. Max 80 chars. Message: ",
    "expected_price": "Extract the price. NORMALIZE: 'lacks' to 'lakh', remove 'around'. Format: '60 lakh'. Message: ",
    "urgency": "Extract the timeline. Format: 'ASAP', '1 month', '3 months'. Message: ",
    "monthly_budget": "Extract the monthly rent. NORMALIZE: number + currency. Format: '25k', '30 lakh'. Message: ",
    "move_in_date": "Extract the move-in date. Format: 'Jan 2025', '15 March', 'ASAP'. Message: ",
}


def _normalize_value(value: str, field: str) -> str:
    """Clean up extracted value for consistent storage."""
    v = value.strip()
    if not v:
        return v
    # Normalize Indian English: lacks/lac -> lakh (case-insensitive)
    v = v.replace("lacks", "lakh").replace("lac", "lakh")
    v = v.replace("Lacks", "lakh").replace("Lac", "lakh")
    # Remove leading filler: "around ", "approximately ", "a ", "an ", "the "
    for prefix in ("around ", "approximately ", "approx ", "about ", "a ", "an ", "the "):
        if v.lower().startswith(prefix):
            v = v[len(prefix):].strip()
    # Trim extra spaces and limit length
    v = " ".join(v.split())
    return v[:100].strip()


def _extract_field(user_message: str, field: str) -> str:
    """Use AI to extract only the relevant value from user's free-form response."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return _normalize_value(_fallback_extract(user_message, field), field)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = EXTRACT_PROMPTS.get(field, f"Extract the {field}. Reply with just the value. Max 50 chars. Message: ") + user_message
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt.strip(),
        )
        value = (response.text or "").strip()
        value = value[:200] if value else _fallback_extract(user_message, field)
        return _normalize_value(value, field)
    except Exception:
        return _normalize_value(_fallback_extract(user_message, field), field)


def _fallback_extract(user_message: str, field: str) -> str:
    """Simple fallback when AI is unavailable: trim and limit length."""
    msg = user_message.strip()
    if not msg:
        return ""
    # For type, do simple keyword match
    if field == "type":
        msg_lower = msg.lower()
        if "buyer" in msg_lower or "buy" in msg_lower or "purchas" in msg_lower:
            return "Buyer"
        if "seller" in msg_lower or "sell" in msg_lower:
            return "Seller"
        if "renter" in msg_lower or "rent" in msg_lower or "tenant" in msg_lower:
            return "Renter"
    return msg[:100].strip()


def _lead_to_row(lead: dict) -> list:
    """Convert lead dict to a row list for Sheets/CSV."""
    lead["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [str(lead.get(f, "")) for f in FIELDNAMES]


def _save_to_google_sheets(lead: dict) -> bool:
    """Save lead to Google Sheets. Returns True if successful."""
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not sheet_id:
        print("[Sheets] Skipped: GOOGLE_SHEET_ID not set")
        return False
    if not creds_path:
        print("[Sheets] Skipped: GOOGLE_APPLICATION_CREDENTIALS not set")
        return False

    # If path is relative, try from project folder
    if not os.path.isabs(creds_path):
        project_dir = Path(__file__).parent
        creds_path = str(project_dir / creds_path)
    if not os.path.exists(creds_path):
        print(f"[Sheets] Error: Credentials file not found: {creds_path}")
        return False

    try:
        import gspread
        gc = gspread.service_account(filename=creds_path)
        sh = gc.open_by_key(sheet_id)
        wks = sh.sheet1

        # Add header row if sheet is empty
        first_cell = wks.acell("A1").value
        if not first_cell or first_cell != "timestamp":
            wks.append_row(FIELDNAMES, value_input_option="USER_ENTERED")

        wks.append_row(_lead_to_row(lead), value_input_option="USER_ENTERED")
        print("[Sheets] Lead saved to Google Sheets")
        return True
    except Exception as e:
        print(f"[Sheets] Error: {e}")
        return False


def _save_to_csv(lead: dict, filepath: str = "leads.csv") -> None:
    """Save lead to CSV file."""
    row = {f: lead.get(f, "") for f in FIELDNAMES}
    row["timestamp"] = lead.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    file_path = Path(filepath)
    file_exists = file_path.exists()

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def save_lead(lead: dict, filepath: str = "leads.csv") -> None:
    """Save a completed lead to Google Sheets (if configured) or CSV."""
    lead["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not _save_to_google_sheets(lead):
        _save_to_csv(lead, filepath)


def process_message(message: str, state: dict) -> tuple[str, dict, bool]:
    """
    Process user message and return (reply, new_state, done).
    done=True means lead is saved and conversation is complete.
    """
    msg = message.strip().lower()
    reply = ""
    new_state = state.copy()
    done = False

    # Step 1: Determine user type (Buyer, Seller, Renter) - extract only that
    if "step" not in state or state["step"] == "type":
        extracted = _extract_field(message, "type")
        extracted_lower = extracted.lower()
        if "buyer" in extracted_lower or extracted_lower == "buy":
            new_state = {"step": "buyer_budget", "type": "Buyer"}
            reply = "Great! I'd love to help you find your dream property. What is your budget?"
        elif "seller" in extracted_lower or "sell" in extracted_lower:
            new_state = {"step": "seller_address", "type": "Seller"}
            reply = "Great! I'd love to help you sell your property. What is the property address?"
        elif "renter" in extracted_lower or "rent" in extracted_lower:
            new_state = {"step": "renter_budget", "type": "Renter"}
            reply = "Great! I'd love to help you find a rental. What is your monthly budget?"
        else:
            reply = "I didn't quite catch that. Are you a Buyer, Seller, or Renter?"
        return reply, new_state, done

    # Buyer flow - extract only the asked field
    if new_state["type"] == "Buyer":
        if new_state["step"] == "buyer_budget":
            new_state["budget"] = _extract_field(message, "budget")
            new_state["step"] = "buyer_location"
            reply = "What is your preferred location?"
        elif new_state["step"] == "buyer_location":
            new_state["location"] = _extract_field(message, "location")
            new_state["step"] = "buyer_property_type"
            reply = "What type of property? (e.g., Apartment, Villa, House)"
        elif new_state["step"] == "buyer_property_type":
            new_state["property_type"] = _extract_field(message, "property_type")
            save_lead(new_state)
            reply = "Thanks for sharing! We're working on it and will get back to you soon."
            done = True

    # Seller flow
    elif new_state["type"] == "Seller":
        if new_state["step"] == "seller_address":
            new_state["address"] = _extract_field(message, "address")
            new_state["step"] = "seller_price"
            reply = "What is your expected price?"
        elif new_state["step"] == "seller_price":
            new_state["expected_price"] = _extract_field(message, "expected_price")
            new_state["step"] = "seller_urgency"
            reply = "How urgent is the sale? (e.g., ASAP, 1 month, 3 months)"
        elif new_state["step"] == "seller_urgency":
            new_state["urgency"] = _extract_field(message, "urgency")
            save_lead(new_state)
            reply = "Thanks for sharing! We're working on it and will get back to you soon."
            done = True

    # Renter flow
    elif new_state["type"] == "Renter":
        if new_state["step"] == "renter_budget":
            new_state["monthly_budget"] = _extract_field(message, "monthly_budget")
            new_state["step"] = "renter_move_in"
            reply = "When do you need to move in?"
        elif new_state["step"] == "renter_move_in":
            new_state["move_in_date"] = _extract_field(message, "move_in_date")
            save_lead(new_state)
            reply = "Thanks for sharing! We're working on it and will get back to you soon."
            done = True

    return reply, new_state, done
