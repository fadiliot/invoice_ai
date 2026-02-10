def validate_invoice(parsed):
    score = 0
    total_checks = 5

    if parsed.get("vendor"):
        score += 1
    if parsed.get("invoice_number"):
        score += 1
    if parsed.get("invoice_date"):
        score += 1
    if parsed.get("total"):
        score += 1
    if parsed.get("line_items") and len(parsed.get("line_items")) > 0:
        score += 1

    return score / total_checks
