# ML — Second-Cohort Pipeline + Lending Classifiers

Two things live here:

1. **The second-cohort pipeline** — generates 100,000 brand-new customers, trains a model per existing warehouse output (churn, CLV, fraud, lending, recommendations) on the original 100,000 as ground truth, predicts onto the new 100,000, and writes the results **directly into the live warehouse**. Nothing in the running app (backend/ai/frontend) changes — the warehouse just grows from 100k to 200k customers, all real rows, queryable exactly like the original ones.
2. **Two earlier, standalone lending classifiers** (kept as reference — see bottom of this file).

## The second-cohort pipeline — run in this order

| # | Notebook | Writes to | What it does |
|---|---|---|---|
| 1 | `new_customer_base_generator.ipynb` | `DimCustomer`, `FactCustomerAccount`, `FactCustomerEngagement` | Generates 100,000 new customers (IDs 100,001–200,000) with realistic, weighted-random distributions (~70/20/10 Retail/SME/Corporate, randomly assigned to existing branches/RMOs) — deliberately *not* the original script's clean 1/3 splits and perfect round-robin. Also writes the shared feature CSV every other notebook reads from. **Must run first** — everything else foreign-keys against `DimCustomer`. |
| 2 | `churn_segmentation_model.ipynb` | `FactCustomerSegmentScore` | Regressor trained on the seed 100k's `Score`, predicts onto the new 100k. |
| 3 | `clv_model.ipynb` | `FactCustomerCLV` | Regressor trained on the seed 100k's `CLVScore` (0–100 scale). |
| 4 | `fraud_model.ipynb` | `FactFraudSignal` | Regressor trained on the seed 100k's `FraudRiskScore`. |
| 5 | `lending_model.ipynb` | `FactCustomerLending` | Two-stage: predicts `LendingModelScore`/`Eligible` first, then `DefaultRiskScore`/`Defaulted` using those as additional features (mirrors real underwriting order). `ApprovedLimit` is generated (tied to balance), not modeled — same as the original data, it has no real relationship to anything. |
| 6 | `recommendation_model.ipynb` | `FactCustomerRecommendation` | Multi-class classifier predicting which of the 8 real `DimProduct` entries fits each customer, plus regressors for `Score`/`PriorityScore`. |

**The existing 100,000 customers (IDs 1–100,000) are treated as frozen seed data** — every notebook trains on them and never modifies them. Only the new 100,000 ever get predicted on and written.

### Setup

```bash
cd ml
python3 -m venv .venv   # or reuse the existing .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # same SQL Server connection details as backend/.env
```

### Run

```bash
jupyter nbconvert --to notebook --execute --inplace new_customer_base_generator.ipynb
jupyter nbconvert --to notebook --execute --inplace churn_segmentation_model.ipynb
jupyter nbconvert --to notebook --execute --inplace clv_model.ipynb
jupyter nbconvert --to notebook --execute --inplace fraud_model.ipynb
jupyter nbconvert --to notebook --execute --inplace lending_model.ipynb
jupyter nbconvert --to notebook --execute --inplace recommendation_model.ipynb
```

Each writes straight into the live `ML_HUB_DEMO` database via `db_utils.py` — a `pymssql`-based chunked bulk insert (`INSERT ... VALUES (...),(...),...` in batches of 1,000), since `pymssql` has no `fast_executemany` (that's a `pyodbc`/SQLAlchemy-specific feature, and this machine has no Homebrew or Microsoft ODBC driver installed to support it). Re-running the base generator would create a second set of duplicate customers — it's meant to run once.

### Verified end-to-end (see conversation for full detail)

- All 8 warehouse tables sit at exactly 200,000 rows, zero missing joins, zero duplicate CIFs.
- Row-level security, the admin RMO directory, and individual customer lookups all work unmodified against the larger, unevenly-distributed population (RMO customer counts now range ~931–1,065, not a flat 500).

### Honest results, not hidden

Model quality varied a lot by target — worth knowing before presenting any of these numbers:

| Model | R² (regression) / Accuracy (classifier) | Note |
|---|---|---|
| Churn (`Score`) | R² ≈ 0.01 | No learnable signal found — only 15 of 100k new customers crossed the `PredictedChurn` threshold at all (predicted score range compressed to 0.27–0.74 vs. the seed's 0.12–0.92). |
| CLV (`CLVScore`) | R² ≈ 0.20 | Weak signal; predictions skew heavily toward the "Low" band. |
| Fraud (`FraudRiskScore`) | R² ≈ 0.63 | The strongest regression result — meaningfully more learnable than churn or CLV. |
| Lending eligibility (`LendingModelScore`) | R² ≈ 0.0 | Same near-zero pattern as churn; cascades into a much lower default rate on new customers (~0.8%) than the seed's ~12%, since predictions cluster above the eligibility threshold. |
| Lending default (`DefaultRiskScore`) | R² ≈ 0.95 | Very strong — because `LendingModelScore`/`Eligible` are legitimate input features here. |
| Recommendation (`ProductId`) | Accuracy = 1.00 | Trivial, not impressive — the seed data only ever assigns 3 of 8 products, purely by `CustomerType`, so the classifier just relearned that fixed mapping perfectly. |

**Same caveat as always:** every seed target is a formula of `CustomerId`, not real behavior, so these numbers measure how well each model reconstructs arithmetic coincidences between different synthetic formulas — not genuine predictive skill. The real deliverable is the pipeline itself (extract seed → train → predict on new → write to warehouse), which is sound and reusable the moment real historical outcomes replace any of these synthetic columns.

---

## Earlier, standalone lending classifiers (kept as reference)

Two notebooks built before the second-cohort pipeline above, evaluating classification approaches on the *existing* 100k customers only (no writes to the database):

### `lending_default_risk_classifier.ipynb` — the actual ask
**Question:** if we lend to this customer, what's the risk they default (fail to repay)?
**Target:** `Defaulted`. **Features:** demographics, account, churn/CLV/fraud, **and** `LendingModelScore`/`Eligible`/`ApprovedLimit` — legitimate inputs, since a lender's own approval signals are real, independent evidence about default risk.
Handles the realistic ~12% default rate (class imbalance) via stratified splitting, class-weighted models, and precision-recall alongside ROC.

### `lending_eligibility_classifier.ipynb` — built first, kept as a reference
**Question:** can eligibility be predicted from a customer's broader profile instead of the score that already determines it?
**Target:** `Eligible`. **Features:** demographics, account, churn/CLV/fraud — deliberately *excluding* `LendingModelScore`, since that's what mechanically produces the label.

Run the same way as above (`jupyter nbconvert --to notebook --execute --inplace <name>.ipynb`). Trained models from all notebooks are saved to `models/`.
