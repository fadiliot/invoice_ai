import requests
from sqlalchemy import text
from app.database import SessionLocal
import json
import os

TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
CLIENT_ID = os.getenv("QB_CLIENT_ID")
CLIENT_SECRET = os.getenv("QB_CLIENT_SECRET")


def _refresh_access_token(refresh_token):
    auth = (CLIENT_ID, CLIENT_SECRET)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    r = requests.post(TOKEN_URL, auth=auth, headers=headers, data=data)
    tokens = r.json()

    if "access_token" not in tokens:
        raise Exception(f"Token refresh failed: {tokens}")

    db = SessionLocal()
    db.execute(
        text("""
        INSERT INTO qb_tokens (access_token, refresh_token, realm_id)
        VALUES (:access, :refresh, :realm)
        """),
        {
            "access": tokens["access_token"],
            "refresh": tokens["refresh_token"],
            "realm": None
        }
    )
    db.commit()
    db.close()

    return tokens["access_token"]



BASE_URL = "https://sandbox-quickbooks.api.intuit.com"


def _get_tokens():
    db = SessionLocal()
    row = db.execute(
        text("SELECT * FROM qb_tokens ORDER BY id DESC LIMIT 1")
    ).fetchone()
    db.close()

    if not row:
        raise Exception("QuickBooks not connected")

    try:
        # QuickBooks access tokens are short-lived
        return row
    except:
        new_access = _refresh_access_token(row.refresh_token)
        return {
            "access_token": new_access,
            "refresh_token": row.refresh_token,
            "realm_id": row.realm_id
        }


def _get_or_create_vendor(access_token, realm_id, vendor_name):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Try to find vendor
    query_url = f"{BASE_URL}/v3/company/{realm_id}/query"
    q = f"SELECT Id FROM Vendor WHERE DisplayName='{vendor_name}'"
    r = requests.get(query_url, headers=headers, params={"query": q})
    res = r.json()

    if "Vendor" in res.get("QueryResponse", {}):
        return res["QueryResponse"]["Vendor"][0]["Id"]

    # Create vendor if not found
    create_url = f"{BASE_URL}/v3/company/{realm_id}/vendor"
    payload = {"DisplayName": vendor_name}
    r = requests.post(create_url, headers=headers, json=payload)

    return r.json()["Vendor"]["Id"]



def push_to_quickbooks(invoice: dict) -> dict:
    tokens = _get_tokens()
    access_token = tokens.access_token
    realm_id = tokens.realm_id

    expense_account_id = _get_expense_account_id(access_token, realm_id)
    vendor_id = _get_or_create_vendor(access_token, realm_id, invoice["vendor"])

    payload = {
        "VendorRef": {
            "value": vendor_id
        },
        "Line": [
            {
                "DetailType": "AccountBasedExpenseLineDetail",
                "Amount": float(item["price"]) * float(item["quantity"]),
                "AccountBasedExpenseLineDetail": {
                    "AccountRef": {
                        "value": expense_account_id
                    }
                }
            }
            for item in invoice["line_items"]
        ]
    }

    print("\n📘 FINAL BILL PAYLOAD (DOC-ALIGNED)")
    print(payload)
    print("=================================\n")

    url = f"{BASE_URL}/v3/company/{realm_id}/bill?minorversion=75"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    r = requests.post(url, headers=headers, json=payload)

    if r.status_code == 401:
        new_access = _refresh_access_token(tokens.refresh_token)
        headers["Authorization"] = f"Bearer {new_access}"
        r = requests.post(url, headers=headers, json=payload)

    if r.status_code not in (200, 201):
        raise Exception(r.text)

    return {
        "status": "SUCCESS",
        "qb_id": r.json()["Bill"]["Id"]
    }


    

def _create_expense_account(access_token, realm_id):
    url = f"{BASE_URL}/v3/company/{realm_id}/account"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "Name": "Office Expense",
        "AccountType": "Expense"
    }

    r = requests.post(url, headers=headers, json=payload)

    print("\n🧾 ACCOUNT CREATE RESPONSE 🧾")
    print(r.json())
    print("🧾 END 🧾\n")

    data = r.json()

    if "Account" not in data:
        raise Exception(f"Account creation failed: {data}")

    return data["Account"]["Id"]



def _get_expense_account_id(access_token, realm_id):
    url = f"{BASE_URL}/v3/company/{realm_id}/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    q = "SELECT Id FROM Account WHERE Active=true MAXRESULTS 1"
    r = requests.get(url, headers=headers, params={"query": q})
    data = r.json()

    accounts = data.get("QueryResponse", {}).get("Account")
    if accounts:
        return accounts[0]["Id"]

    #  fallback: create account
    print("⚠️ No account found. Creating Office Expense account.")
    return _create_expense_account(access_token, realm_id)

def _get_ap_account_id(access_token, realm_id):
    url = f"{BASE_URL}/v3/company/{realm_id}/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    # Accounts Payable account
    q = "SELECT Id FROM Account WHERE AccountType='Accounts Payable' AND Active=true MAXRESULTS 1"
    r = requests.get(url, headers=headers, params={"query": q})
    data = r.json()

    accounts = data.get("QueryResponse", {}).get("Account")
    if accounts:
        return accounts[0]["Id"]

    raise Exception("No Accounts Payable account found")
