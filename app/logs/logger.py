import datetime

def log(invoice_id, stage, message):
    print(f"[{datetime.datetime.utcnow()}] {invoice_id} | {stage} | {message}")
