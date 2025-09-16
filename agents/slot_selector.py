# import google.generativeai as genai
# from config.settings import GEMINI_API_KEY

# genai.configure(api_key=GEMINI_API_KEY)

# def choose_best_slot(slots):
#     prompt = f"""
#     You are an assistant helping to select the best appointment slot.

#     Available slots:
#     {slots}

#     Task:
#     - Choose the earliest available slot.
#     - Return JSON only in this format:
#       {{
#         "slot_id": "id",
#         "date": "yyyy-mm-dd"
#       }}
#     """

#     model = genai.GenerativeModel("gemini-2.5-flash")
#     response = model.generate_content(prompt)

#     return response.text.strip()


import google.generativeai as genai
from config.settings import GEMINI_API_KEY
import json
import re
from datetime import datetime

genai.configure(api_key=GEMINI_API_KEY)

def choose_best_slot(slots):
    """
    Decide the best slot using Gemini. 
    If Gemini output is invalid JSON, fallback to earliest slot by date.
    """

    prompt = f"""
    You are an assistant helping to select the best appointment slot.

    Available slots:
    {slots}

    Task:
    - Choose the earliest available slot.
    - Return JSON only in this format:
      {{
        "slot_id": "id",
        "date": "yyyy-mm-dd"
      }}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Try to extract JSON using regex (in case Gemini adds extra text)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found in Gemini response")

        parsed = json.loads(match.group(0))

        if "slot_id" in parsed and "date" in parsed:
            return parsed

    except Exception as e:
        print("[WARN] Gemini parsing failed:", e)

    # --- Fallback logic: pick earliest slot manually ---
    print("[INFO] Falling back to earliest slot selection")

    # Expect slots as list of dicts: {id, text}, where text contains date
    def extract_date(slot_text):
        try:
            # Attempt to parse date (you may need to adjust format based on actual website)
            return datetime.strptime(slot_text.split()[0], "%Y-%m-%d")
        except Exception:
            return datetime.max

    earliest = min(slots, key=lambda s: extract_date(s["text"]))
    return {"slot_id": earliest["id"], "date": earliest["text"].split()[0]}
