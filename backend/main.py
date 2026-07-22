from fastapi import FastAPI, HTTPException, Query

import queries
from db import run_query

app = FastAPI(title="ML Hub Backend", version="0.1.0")


@app.get("/health")
def health():
    run_query("SELECT 1;")
    return {"status": "ok", "db": "connected"}


@app.get("/api/high-churn-risk")
def get_high_churn_risk(limit: int = Query(20, ge=1, le=200)):
    return queries.high_churn_risk(limit)


@app.get("/api/high-clv")
def get_high_clv(limit: int = Query(20, ge=1, le=200)):
    return queries.high_clv(limit)


@app.get("/api/rmo-customer-counts")
def get_rmo_customer_counts():
    return queries.rmo_customer_counts()


@app.get("/api/customers/{cif}")
def get_customer_by_cif(cif: str):
    customer = queries.customer_by_cif(cif)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
