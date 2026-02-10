import os
import requests
from fastapi import APIRouter, Request
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter()

CLIENT_ID = os.getenv("QB_CLIENT_ID")
CLIENT_SECRET = os.getenv("QB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("QB_REDIRECT_URI")

AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


@router.get("/auth/qb/login")
def qb_login():
    url = (
        f"{AUTH_URL}"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&scope=com.intuit.quickbooks.accounting"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state=securetoken"
    )
    return {"auth_url": url}


@router.get("/auth/qb/callback")
def qb_callback(request: Request):
    code = request.query_params.get("code")
    realm_id = request.query_params.get("realmId")

    auth = (CLIENT_ID, CLIENT_SECRET)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    resp = requests.post(TOKEN_URL, auth=auth, headers=headers, data=data)
    tokens = resp.json()

    db = SessionLocal()
    db.execute(
        text("""
        INSERT INTO qb_tokens (access_token, refresh_token, realm_id)
        VALUES (:access, :refresh, :realm)
        """),
        {
            "access": tokens["access_token"],
            "refresh": tokens["refresh_token"],
            "realm": realm_id
        }
    )
    db.commit()
    db.close()

    return {"status": "QuickBooks connected successfully"}
