import os

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

TOOLS = [
    {
        "name": "get_high_churn_risk_customers",
        "description": "Get the customers with the highest predicted churn risk, ordered by churn score descending. Scoped to your own book (or the RMO/bank-wide view currently selected, for admins).",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "How many customers to return (1-200). Defaults to 20.",
                }
            },
        },
    },
    {
        "name": "get_high_clv_customers",
        "description": "Get the customers with the highest customer lifetime value (CLV), ordered by CLV score descending. Scoped to your own book (or the RMO/bank-wide view currently selected, for admins).",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "How many customers to return (1-200). Defaults to 20.",
                }
            },
        },
    },
    {
        "name": "get_my_customer_count",
        "description": "Get how many customers are managed in the current view (your own book, or the RMO/bank-wide view currently selected, for admins).",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_product_recommendations",
        "description": "Get customers with a recommended product/offer, ordered by priority score descending. Scoped to your own book (or the RMO/bank-wide view currently selected, for admins). Use this for questions about which customers should be offered a product, e.g. 'which retail customers should get a specific offer' or 'which products should be recommended to a segment'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "How many customers to return (1-200). Defaults to 20.",
                },
                "customer_type": {
                    "type": "string",
                    "enum": ["Retail", "Corporate", "SME"],
                    "description": "Restrict to one customer type. Omit to include all types.",
                },
            },
        },
    },
    {
        "name": "get_lending_eligible_customers",
        "description": "Get customers who are eligible for lending, ordered by approved limit descending. Scoped to your own book (or the RMO/bank-wide view currently selected, for admins). Use this for questions about loan/lending eligibility, e.g. 'which SME customers are eligible for lending'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "How many customers to return (1-200). Defaults to 20.",
                },
                "customer_type": {
                    "type": "string",
                    "enum": ["Retail", "Corporate", "SME"],
                    "description": "Restrict to one customer type. Omit to include all types.",
                },
            },
        },
    },
    {
        "name": "get_customer_profile",
        "description": "Get a single customer's full profile (type, segment, status) plus their churn, CLV, fraud, and lending scores, looked up by CIF. Only works if the customer is in your current view (your own book, or the RMO/bank-wide view currently selected, for admins).",
        "input_schema": {
            "type": "object",
            "properties": {
                "cif": {
                    "type": "string",
                    "description": "The customer's CIF identifier, e.g. R000000001.",
                }
            },
            "required": ["cif"],
        },
    },
    {
        "name": "get_rmo_directory",
        "description": "List every relationship manager (RMO) in the bank with how many customers each manages. Admin access only - will return an error if the current user isn't an admin.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

NOT_AUTHENTICATED = {"error": "Not logged in, or the session has expired. Please log in again."}
ADMIN_ONLY = {"error": "That's an admin-only capability - the current user doesn't have admin access."}


def _get(auth_header: str, path: str, params: dict | None = None):
    resp = requests.get(
        f"{BACKEND_URL}{path}",
        params=params,
        headers={"Authorization": auth_header},
    )
    if resp.status_code == 401:
        return None
    if resp.status_code == 403:
        return "forbidden"
    resp.raise_for_status()
    return resp.json()


def _with_scope(params: dict, rmo_code: str | None) -> dict:
    if rmo_code:
        params["rmo_code"] = rmo_code
    return params


def get_high_churn_risk_customers(auth_header: str, rmo_code: str | None, limit: int = 20):
    result = _get(auth_header, "/api/high-churn-risk", _with_scope({"limit": limit}, rmo_code))
    return NOT_AUTHENTICATED if result is None else result


def get_high_clv_customers(auth_header: str, rmo_code: str | None, limit: int = 20):
    result = _get(auth_header, "/api/high-clv", _with_scope({"limit": limit}, rmo_code))
    return NOT_AUTHENTICATED if result is None else result


def get_my_customer_count(auth_header: str, rmo_code: str | None):
    result = _get(auth_header, "/api/rmo-customer-counts", _with_scope({}, rmo_code))
    return NOT_AUTHENTICATED if result is None else result


def get_product_recommendations(auth_header: str, rmo_code: str | None, limit: int = 20, customer_type: str | None = None):
    params = _with_scope({"limit": limit}, rmo_code)
    if customer_type:
        params["customer_type"] = customer_type
    result = _get(auth_header, "/api/recommendations", params)
    return NOT_AUTHENTICATED if result is None else result


def get_lending_eligible_customers(auth_header: str, rmo_code: str | None, limit: int = 20, customer_type: str | None = None):
    params = _with_scope({"limit": limit}, rmo_code)
    if customer_type:
        params["customer_type"] = customer_type
    result = _get(auth_header, "/api/lending-eligible", params)
    return NOT_AUTHENTICATED if result is None else result


def get_customer_profile(auth_header: str, rmo_code: str | None, cif: str):
    resp = requests.get(
        f"{BACKEND_URL}/api/customers/{cif}",
        params=_with_scope({}, rmo_code),
        headers={"Authorization": auth_header},
    )
    if resp.status_code == 401:
        return NOT_AUTHENTICATED
    if resp.status_code == 404:
        return {"error": f"No customer found with CIF '{cif}' in the current view."}
    resp.raise_for_status()
    return resp.json()


def get_rmo_directory(auth_header: str, rmo_code: str | None):
    result = _get(auth_header, "/api/admin/rmos")
    if result is None:
        return NOT_AUTHENTICATED
    if result == "forbidden":
        return ADMIN_ONLY
    return result


TOOL_FUNCTIONS = {
    "get_high_churn_risk_customers": get_high_churn_risk_customers,
    "get_high_clv_customers": get_high_clv_customers,
    "get_my_customer_count": get_my_customer_count,
    "get_product_recommendations": get_product_recommendations,
    "get_lending_eligible_customers": get_lending_eligible_customers,
    "get_customer_profile": get_customer_profile,
    "get_rmo_directory": get_rmo_directory,
}
