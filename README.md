# FastAPI Restaurant Review App

A simple restaurant review web application built with FastAPI and PostgreSQL.

## Environment & Versions

- **Python**: 3.12.13
- **FastAPI**: 0.111.1
- **PostgreSQL**: Azure Database for PostgreSQL (Flexible Server)
- **Server**: Gunicorn with Uvicorn worker
- **Runtime**: Linux (Ubuntu)

## Quick Start - Local Development

### Prerequisites
- Python 3.12+
- PostgreSQL 14+
- pip / virtualenv

### Setup

```shell
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt
pip install -e src

# Set environment variables (create .env file)
export DBHOST=localhost
export DBNAME=restaurants
export DBUSER=postgres
export DBPASS=<your_password>

# Initialize database
python3 src/fastapi_app/seed_data.py

# Start dev server
python3 -m uvicorn fastapi_app:app --reload --port=8000
```

Visit `http://localhost:8000` in your browser.

## Azure Deployment

Deployed via Azure Pipelines to:
- **App Service**: Linux Web App (Python 3.12)
- **Database**: Azure Database for PostgreSQL (Flexible Server)
- **Region**: East US

### Required Environment Variables (App Settings)

```
AZURE_POSTGRESQL_CONNECTIONSTRING=host=<host>.postgres.database.azure.com port=5432 dbname=<db> user=<user> password=<password> sslmode=require
APPLICATIONINSIGHTS_CONNECTION_STRING=<if using Application Insights>
```

## Project Structure

```
src/
├── fastapi_app/
│   ├── app.py              # FastAPI application
│   ├── models.py           # Database models (Restaurant, Review)
│   └── seed_data.py        # Database initialization
├── requirements.txt        # Dependencies
├── gunicorn.conf.py        # Gunicorn configuration
└── entrypoint.sh          # Startup script
```

## Notes

- Database connection string automatically detected from `AZURE_POSTGRESQL_CONNECTIONSTRING` or individual `DB_*` environment variables
- SSL mode set to `require` for secure database connections
- Seed data script handles gracefully if database is unavailable at startup
    ```

1. When you see the message `Your application running on port 8000 is available.`, click **Open in Browser**.

## Running locally

If you're running the app inside VS Code or GitHub Codespaces, you can use the "Run and Debug" button to start the app.

```sh
python3 -m uvicorn fastapi_app:app --reload --port=8000
```

## Deployment

This repo is set up for deployment on Azure via Azure App Service.

Steps for deployment:

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/) and create an Azure Subscription.
2. Install the [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd). (If you open this repository in Codespaces or with the VS Code Dev Containers extension, that part will be done for you.)
3. Login to Azure:

    ```shell
    azd auth login
    ```

4. Provision and deploy all the resources:

    ```shell
    azd up
    ```

    It will prompt you to provide an `azd` environment name (like "myapp"), select a subscription from your Azure account, and select a location (like "eastus"). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location can help, as there may be availability constraints for some of the resources.

5. When `azd` has finished deploying, you'll see an endpoint URI in the command output. Visit that URI, and you should see the front page of the app! 🎉

6. When you've made any changes to the app code, you can just run:

    ```shell
    azd deploy
    ```

## Getting help

If you're working with this project and running into issues, please post in [Issues](/issues).
