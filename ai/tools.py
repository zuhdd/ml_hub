import os

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

TOOLS = [
    {
        "name": "get_high_churn_risk_customers",
        "description": "Get the customers with the highest predicted churn risk, ordered by churn score descending.",
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
        "description": "Get the customers with the highest customer lifetime value (CLV), ordered by CLV score descending.",
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
        "name": "get_rmo_customer_counts",
        "description": "Get the number of customers managed by each relationship manager (RMO), ordered by count descending.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_customer_profile",
        "description": "Get a single customer's full profile (type, segment, status) plus their churn, CLV, fraud, and lending scores, looked up by CIF.",
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
]


def get_high_churn_risk_customers(limit: int = 20):
    resp = requests.get(f"{BACKEND_URL}/api/high-churn-risk", params={"limit": limit})
    resp.raise_for_status()
    return resp.json()


def get_high_clv_customers(limit: int = 20):
    resp = requests.get(f"{BACKEND_URL}/api/high-clv", params={"limit": limit})
    resp.raise_for_status()
    return resp.json()


def get_rmo_customer_counts():
    resp = requests.get(f"{BACKEND_URL}/api/rmo-customer-counts")
    resp.raise_for_status()
    return resp.json()


def get_customer_profile(cif: str):
    resp = requests.get(f"{BACKEND_URL}/api/customers/{cif}")
    if resp.status_code == 404:
        return {"error": f"No customer found with CIF '{cif}'."}
    resp.raise_for_status()
    return resp.json()


TOOL_FUNCTIONS = {
    "get_high_churn_risk_customers": get_high_churn_risk_customers,
    "get_high_clv_customers": get_high_clv_customers,
    "get_rmo_customer_counts": get_rmo_customer_counts,
    "get_customer_profile": get_customer_profile,
}
