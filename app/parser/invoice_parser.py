import re
from typing import List

def extract_vendor(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for line in lines:
        if (
            "INVOICE" not in line.upper()
            and "BILL" not in line.upper()
            and len(line) > 5
        ):
            return line.replace("G ", "").strip()

    return "UNKNOWN"


def extract_invoice_number(text: str) -> str:
    patterns = [
        r"Invoice\s*#\s*[:\-]?\s*([A-Z0-9\-]+)",
        r"INV[-\s]*([0-9]+)"
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "UNKNOWN"


def extract_date(text: str) -> str:
    match = re.search(
        r"(\d{2}[/-]\d{2}[/-]\d{4})", text
    )
    return match.group(1) if match else "UNKNOWN"

def extract_total(text: str) -> float:
    clean_text = " ".join(text.split())

    patterns = [
        r"BALANCE\s+DUE\s*[:$₹]*\s*([\d,]+\.\d{2})",
        r"TOTAL\s*[:$₹]*\s*([\d,]+\.\d{2})"
    ]

    for p in patterns:
        match = re.search(p, clean_text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))
    return 0.0

def extract_tax(text: str) -> float:
    match = re.search(
        r"Tax.*?[:$₹]*\s*([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )
    return float(match.group(1).replace(",", "")) if match else 0.0


def extract_line_items(text: str):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    items = []
    description_lines = []
    numeric_lines = []

    # Step 1: Separate description and numeric rows
    for line in lines:
        # Match numeric row like: 1 $500.00 $1,500.00
        if re.match(r"\d+\s+[$₹]?\d", line):
            numeric_lines.append(line)
        elif "description" not in line.lower() \
             and "invoice" not in line.lower() \
             and "subtotal" not in line.lower() \
             and "total" not in line.lower() \
             and "tax" not in line.lower():
            description_lines.append(line)

    # Step 2: Extract numeric details
    parsed_numbers = []
    for line in numeric_lines:
        match = re.search(
            r"(\d+)\s+[$₹]?([\d,]+\.\d{2})\s+[$₹]?([\d,]+\.\d{2})",
            line
        )
        if match:
            quantity = float(match.group(1))
            unit_price = float(match.group(2).replace(",", ""))
            parsed_numbers.append((quantity, unit_price))

    # Step 3: Pair descriptions with numeric rows
    for i in range(min(len(description_lines), len(parsed_numbers))):
        items.append({
            "name": description_lines[i],
            "quantity": parsed_numbers[i][0],
            "price": parsed_numbers[i][1]
        })

    return items


def parse_invoice(text: str) -> dict:
    return {
        "vendor": extract_vendor(text),
        "invoice_number": extract_invoice_number(text),
        "invoice_date": extract_date(text),
        "line_items": extract_line_items(text),
        "tax": extract_tax(text),
        "total": extract_total(text)
    }