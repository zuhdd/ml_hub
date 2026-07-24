import os
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import queries
from db import run_query

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 12
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

app = FastAPI(title="ML Hub Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CustomerType = Literal["Retail", "Corporate", "SME"]


class LoginRequest(BaseModel):
    rmo_code: str


class AdminLoginRequest(BaseModel):
    password: str


def get_current_principal(authorization: Optional[str] = Header(None)) -> dict:
    """Decodes the session token. Returns either
    {"role": "rmo", "rmo_id": ..., "rmo_code": ..., ...} or {"role": "admin"}."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ")
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session, please log in again")


def _resolve_scope(principal: dict, rmo_code: Optional[str]) -> Optional[int]:
    """Returns the RmoId to scope a query to, or None for bank-wide access.
    RMO principals are always locked to their own id, regardless of rmo_code -
    that parameter only has any effect for admins."""
    if principal.get("role") == "admin":
        if rmo_code:
            rmo = queries.rmo_by_code(rmo_code.strip().upper())
            if rmo is None:
                raise HTTPException(status_code=404, detail="Unknown RMO code")
            return rmo["RmoId"]
        return None
    return principal["rmo_id"]


@app.get("/health")
def health():
    run_query("SELECT 1;")
    return {"status": "ok", "db": "connected"}


@app.post("/api/auth/login")
def login(body: LoginRequest):
    rmo = queries.rmo_by_code(body.rmo_code.strip().upper())
    if rmo is None:
        raise HTTPException(status_code=401, detail="Unknown RMO code")

    payload = {
        "role": "rmo",
        "rmo_id": rmo["RmoId"],
        "rmo_code": rmo["RmoCode"],
        "rmo_name": rmo["RmoName"],
        "team": rmo["Team"],
        "region": rmo["Region"],
    }
    token = jwt.encode(
        {**payload, "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return {"token": token, "rmo": payload}


@app.post("/api/auth/admin-login")
def admin_login(body: AdminLoginRequest):
    if body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Incorrect admin password")

    payload = {"role": "admin"}
    token = jwt.encode(
        {**payload, "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return {"token": token}


@app.get("/api/admin/rmos")
def list_rmos(principal: dict = Depends(get_current_principal)):
    if principal.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return queries.all_rmos()


@app.get("/api/high-churn-risk")
def get_high_churn_risk(
    limit: int = Query(20, ge=1, le=200),
    rmo_code: Optional[str] = None,
    principal: dict = Depends(get_current_principal),
):
    return queries.high_churn_risk(limit, _resolve_scope(principal, rmo_code))


@app.get("/api/high-clv")
def get_high_clv(
    limit: int = Query(20, ge=1, le=200),
    rmo_code: Optional[str] = None,
    principal: dict = Depends(get_current_principal),
):
    return queries.high_clv(limit, _resolve_scope(principal, rmo_code))


@app.get("/api/rmo-customer-counts")
def get_my_customer_count(
    rmo_code: Optional[str] = None,
    principal: dict = Depends(get_current_principal),
):
    return queries.my_customer_count(_resolve_scope(principal, rmo_code))


@app.get("/api/recommendations")
def get_recommendations(
    limit: int = Query(20, ge=1, le=200),
    customer_type: Optional[CustomerType] = None,
    rmo_code: Optional[str] = None,
    principal: dict = Depends(get_current_principal),
):
    return queries.top_recommendations(limit, _resolve_scope(principal, rmo_code), customer_type)


@app.get("/api/lending-eligible")
def get_lending_eligible(
    limit: int = Query(20, ge=1, le=200),
    customer_type: Optional[CustomerType] = None,
    rmo_code: Optional[str] = None,
    principal: dict = Depends(get_current_principal),
):
    return queries.lending_eligible(limit, _resolve_scope(principal, rmo_code), customer_type)


@app.get("/api/customers/{cif}")
def get_customer_by_cif(
    cif: str,
    rmo_code: Optional[str] = None,
    principal: dict = Depends(get_current_principal),
):
    customer = queries.customer_by_cif(cif, _resolve_scope(principal, rmo_code))
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
