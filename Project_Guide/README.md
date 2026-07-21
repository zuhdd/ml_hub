# ML Hub Project Guide

## Project Vision

Wema ML Hub is a banking-focused AI assistant platform designed to help customer relationship teams, relationship managers, and business users query customer intelligence in natural language.

Instead of asking different teams to manually pull insights from multiple model outputs, ML Hub brings together customer data, model predictions, and engagement history into one experience.

The aim is to support questions such as:
- Which customers are likely to churn?
- Which retail customers should receive a specific offer?
- Which corporate customers are high-value and should be prioritized?
- Which SME customers are eligible for lending or should be contacted now?
- Which products should be recommended to a given customer or segment?

This project is meant to be an MVP demo, not a full production banking platform. The goal is to show how a realistic AI-powered experience can sit on top of a well-structured warehouse and help users explore customer intelligence with guardrails and auditability.

---

## What the Project Includes

The project has four major layers:

1. Data Layer
   - A realistic Microsoft SQL Server warehouse
   - Synthetic but realistic banking data for around 100,000 customers
   - Customer, account, product, RMO, and model output tables

2. AI Layer
   - A natural language interface that can understand business questions
   - A reasoning layer that translates questions into SQL queries
   - An orchestration layer that manages prompts, execution, and result handling

3. Application Layer
   - A frontend interface where the user can ask questions in plain English
   - A simple experience for viewing results, customer lists, recommendations, and risk insights

4. Governance Layer
   - Audit trail of generated queries and responses
   - Guardrails to prevent unsafe or inappropriate actions
   - Structured logging for traceability and review

---

## Recommended End-to-End Workflow for the Intern

The intern should follow the work in this order:

### Step 1: Understand the Business Problem

Before touching code, the intern should understand the purpose of the platform:
- This is not just a chatbot.
- It is a business intelligence assistant for banking operations.
- The assistant should help business users ask questions about customers and receive safe, explainable, and traceable outputs.

The intern should be comfortable with concepts such as:
- Retail, Corporate, and SME customer segments
- CIF-based customer identification
- Relationship managers and customer ownership
- Product recommendations and churn risk
- CLV, fraud, and lending outputs

---

### Step 2: Set Up the Data Warehouse

The first technical milestone is the data layer.

Go to the SQL folder:
- [sql](sql)

Inside that folder, the intern should review:
- the SQL warehouse script
- the setup guide
- the data dictionary

The intern should:
1. Install or access a SQL Server instance
2. Connect to it using the SQL Server extension in VS Code
3. Run the SQL script to create the warehouse
4. Confirm that the database and tables are created successfully

The warehouse should contain:
- customer master data
- branch and RMO information
- products
- account information
- churn and segmentation signals
- CLV score outputs
- recommendation outputs
- fraud and lending signals
- engagement data

The data should be used as the main source of truth for the AI experience.

---

### Step 3: Review the Data Model

The intern should read the data dictionary thoroughly and understand:
- which tables are dimensions and which are facts
- how customers relate to RMOs and branches
- how model outputs connect to customer records
- which fields are useful for natural language questions

The intern should learn how to answer questions such as:
- Who are the customers at risk of churn?
- Which customers have high CLV?
- Which products were recommended to a customer?
- Which RMOs manage a specific customer segment?

---

### Step 4: Build the Backend Data Access Layer

Once the warehouse is ready, the next step is to create a backend service that can query the warehouse safely.

This backend should:
- connect to SQL Server
- receive a request from the AI layer
- run approved SQL queries
- return structured results to the application layer

At this stage, the intern should focus on reliability and security rather than fancy UI.

Recommended approach:
- use a lightweight backend service
- expose a simple endpoint for natural language questions
- return JSON results that the frontend can display

---

### Step 5: Connect an LLM with a Proper Orchestrator

This is the heart of the experience.

The intern should connect an LLM to the warehouse through an orchestrator so that the model can:
- understand a natural language question
- decide what data is needed
- generate or suggest the appropriate SQL query
- run the query safely
- return a business-friendly response

A good approach is to use a framework such as LangChain or a similar orchestration pattern.

#### Why an orchestrator is needed

A plain LLM prompt alone is not enough because the model may:
- generate invalid SQL
- query the wrong tables
- expose sensitive logic
- produce hallucinated answers

An orchestrator helps structure the flow:
1. user asks a question
2. orchestrator sends the request to the LLM with schema context
3. LLM proposes a SQL query
4. the system validates the query
5. the query runs against SQL Server
6. the results are returned and summarized

---

### Step 6: Add Guardrails and Safety Controls

Because this is a banking project, guardrails are essential.

The intern should implement the following controls:

#### A. Query Validation
- Restrict SQL generation to read-only operations where possible
- Prevent destructive commands such as DROP, DELETE, UPDATE, or INSERT from being executed by the LLM
- Use parameterized query generation where appropriate

#### B. Schema Awareness
- Provide the LLM with only the relevant tables and columns needed for the task
- Avoid exposing unnecessary or sensitive schema details

#### C. Audit Trail
- Log every question asked
- Log the generated SQL query
- Log the execution time
- Log the result summary
- Save who triggered the request and when

#### D. Human Review for Sensitive Actions
- If a prompt asks for high-risk actions, ask for confirmation or block the action
- For example, if the request involves customer data exposure or a decision that requires approval, the system should route to a safe review path

#### E. Response Grounding
- Every answer should be based on retrieved data
- The system should not answer from the model’s memory alone
- It should present evidence from the warehouse

---

### Step 7: Build a Simple Frontend Experience

The frontend should be simple and focused on the MVP experience.

The user should be able to:
- type a natural language question
- see the answer in a business-friendly format
- view the underlying query or explanation if needed
- inspect the customer list or recommendations returned by the system

A basic interface is enough for the demo.

---

### Step 8: Create a Demo Narrative

The intern should also think about how the project will be presented.

The demo should show:
- how a business user can ask a natural language question
- how the system understands the request
- how it query the warehouse
- how it returns an insight with traceability

This is important because the project is meant to demonstrate value, not just technical complexity.

---

## Suggested Technical Stack for the MVP

The following stack is appropriate for this project:

- Frontend: simple web app or internal dashboard
- Backend: Python or Node.js service
- Database: Microsoft SQL Server
- LLM orchestration: LangChain or a similar framework
- Prompting: structured prompts with schema context
- Logging: file-based or database-based audit logs
- Deployment: local demo environment first, then a cloud-based environment later

---

## Suggested Folder Structure

The repository should eventually look something like this:

- sql/
  - warehouse script
  - setup guide
  - data dictionary
- backend/
  - API services
  - database connection logic
  - orchestration layer
- frontend/
  - UI pages
  - chat experience
- prompts/
  - prompt templates
- logs/
  - audit logs
- docs/
  - architecture notes and business documentation

---

## Recommended Milestones

### Milestone 1: Data Foundation
- Complete the warehouse setup
- Confirm the schema and data load works
- Review the data dictionary

### Milestone 2: Basic Query Layer
- Create backend logic to connect to SQL Server
- Test a few fixed business questions

### Milestone 3: LLM + Orchestrator
- Connect the LLM to the warehouse
- Generate SQL from natural language questions
- Validate and run the query

### Milestone 4: Guardrails and Audit Trail
- Add query restrictions
- Add logging and audit history
- Ensure safe and traceable operations

### Milestone 5: Frontend Demo
- Create a simple UI for the end user
- Demo the experience with realistic business questions

---

## Important Notes for the Intern

The intern should always remember that this is a banking demo with sensitive business context. The system must be:
- safe
- explainable
- auditable
- grounded in real warehouse data

It should not behave like a free-form chatbot that invents answers.

The ideal experience is one where the user asks a natural language question and the system:
1. understands the intent,
2. queries the warehouse accurately,
3. returns evidence-backed results,
4. records what happened for review.

---

## Suggested First Deliverables

For the first version, the intern should focus on these deliverables:

1. A working warehouse from the SQL script
2. A simple backend that can run a few example queries
3. An LLM orchestration flow that turns natural language into SQL
4. Guardrails and audit logging
5. A simple frontend demo page

---

## Final Goal

The final goal of this project is to create a demo-ready ML Hub that allows a business user to ask questions in everyday language and receive trustworthy, warehouse-backed insights about customers, model outputs, and next actions.

This is the foundation for a future enterprise-grade banking AI assistant.
