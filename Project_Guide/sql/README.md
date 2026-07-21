# SQL Setup Guide for ML Hub

This folder contains the data warehouse setup materials for the ML Hub project.

## What this folder is for

This is the starting point for the intern. Before building the AI experience, the intern must first create a working warehouse that contains realistic banking demo data.

## Files to review

- [../../sql/ml_hub_warehouse.sql](../../sql/ml_hub_warehouse.sql) - the full SQL script that creates the warehouse and loads demo data
- [../../README.md](../../README.md) - the warehouse setup guide for the intern
- [../../DATA_DICTIONARY.md](../../DATA_DICTIONARY.md) - the data dictionary for the warehouse tables

## Step-by-step instructions

### 1. Install or access SQL Server

If the intern does not already have a SQL Server instance, they can use one of the following options:
- a shared SQL Server instance provided by the team
- Azure SQL Database
- a local SQL Server instance running in Docker on the Mac

For a Mac-based local setup, Docker is the easiest option.

### 2. Install VS Code and the SQL Server extension

The intern should:
1. Install Visual Studio Code on the Mac
2. Open the Extensions view
3. Search for "SQL Server"
4. Install the Microsoft SQL Server extension
5. Install SQL Tools if prompted

### 3. Connect to SQL Server from VS Code

The intern will need:
- server name or IP address
- port number if needed
- SQL login credentials

Example local connection details for Docker:
- Server: localhost,1433
- Authentication: SQL Login
- User: sa
- Password: YourStrongPassword123!

### 4. Run the warehouse SQL script

Once connected, the intern should open [../../sql/ml_hub_warehouse.sql](../../sql/ml_hub_warehouse.sql) and execute it.

The script will:
- create the ML_HUB_DEMO database
- create the warehouse tables
- load about 100,000 realistic customer records
- create indexes and relationships

### 5. Validate the result

After execution, the intern should verify that:
- the database exists
- the main tables were created
- sample rows are present in the customer and model output tables

### 6. Review the data dictionary

Before moving to the AI layer, the intern should study [../../DATA_DICTIONARY.md](../../DATA_DICTIONARY.md) so they understand:
- the customer model
- the relationship manager model
- the product model
- the model output tables for churn, CLV, recommendations, lending, and fraud

### 7. Prepare for the next phase

Once the warehouse is working, the intern is ready to move to the backend and AI layer.

The next step is to connect a language model to the warehouse through an orchestration layer so that the system can translate business questions into SQL and return safe, evidence-backed results.

## Expected outcome

After this step is complete, the intern should have a working demo warehouse that can support:
- customer-level analysis
- segment-level analysis
- churn and recommendation questions
- RMOs and customer ownership review
- future AI-powered querying

## Next step

Go back to [../README.md](../README.md) for the full project vision, architecture guidance, and the planned workflow for the AI layer, guardrails, and audit trail.
