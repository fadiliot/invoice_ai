import os
import json
import re
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = "models/gemini-2.5-flash"


def _safe_json_extract(text: str) -> dict:
    """
    Extract JSON object from Gemini response safely
    """
    if not text:
        raise ValueError("Empty response from Gemini")

    # Remove markdown fences if present
    text = text.replace("```json", "").replace("```", "").strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fallback: extract first JSON object using regex
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group())

    raise ValueError(f"Could not parse JSON from Gemini response:\n{text}")


def parse_invoice_with_gemini(ocr_text: str) -> dict:
    prompt = f"""
You are an invoice extraction engine.

Extract invoice data from OCR text below.
Return ONLY valid JSON. Do not include explanations.

Schema:
{{
  "vendor": "",
  "invoice_number": "",
  "invoice_date": "",
  "line_items": [
    {{
      "name": "",
      "quantity": 0,
      "price": 0
    }}
  ],
  "tax": 0,
  "total": 0
}}

OCR TEXT:
{ocr_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    raw_text = (response.text or "").strip()

    
    print("\n====== GEMINI RAW RESPONSE ======\n")
    print(raw_text)
    print("\n================================\n")

    return _safe_json_extract(raw_text)
