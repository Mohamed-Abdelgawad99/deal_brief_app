# Deal Brief App

A lightweight internal tool that turns unstructured text into a consistent “deal brief” the team can scan quickly, plus a basic UI to browse recent deals.


## 🚀 Quick Deployment

Pre-built Docker images are automatically published to GitHub Container Registry. To deploy using pre-built images:

```bash
# Create a directory for deployment
mkdir deal-brief-deployment && cd deal-brief-deployment

# Download the deployment docker-compose file (see DEPLOYMENT.md)
# Add your .env file with OPENAI_API_KEY
# Run the application
docker compose up -d
```

**📖 For detailed deployment instructions**, including cloud platform guides and production best practices, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Tech Stack 
- **UV Package Manager**: uv to easliy mange dependencies and replicate environments
- **Backend**: FastAPI, SQLModel, SQLAlchemy, PostgreSQL, OpenAI API, Instructor, Uvicorn

- **Frontend**: Streamlit, Pandas

- **Deployment**: Docker, Docker Compose

## Repository Structure

```
deal_brief_app/
├── 📁 backend/                     # FastAPI Backend Service
│   ├── 📄 pyproject.toml           # Python dependencies (uv package manager)
│   ├── 📄 Dockerfile               # Backend container configuration
│   ├── 📄 alembic.ini              # Database migration configuration
│   ├── 📄 .dockerignore            # Docker build exclusions
│   ├── 📄 .python-version          # Python version specification
│   ├── 📁 src/                     # Source code directory
│   │   ├── 📄 __init__.py          # Package initialization
│   │   ├── 📄 main.py              # FastAPI application & API endpoints
│   │   ├── 📄 models.py            # SQLModel database models & schemas
│   │   ├── 📄 database.py          # Database connection & session management
│   │   ├── 📄 services.py          # Business logic & LLM processing
│   │   └── 📁 utils/               # Utility modules
│   │       └── 📄 logger.py        # Logging configuration
│   ├── 📁 alembic/                 # Database migration management
│   │   ├── 📄 env.py               # Alembic environment configuration
│   │   ├── 📄 script.py.mako       # Migration script template
│   │   └── 📁 versions/            # Database migration scripts
│   │       └── 📄 9bc70fe03354_init_db.py
│   └── 📁 tests/                   # Unit tests
│       ├── 📄 __init__.py
│       └── 📄 test_ingest.py       # API endpoint tests
│
├── 📁 frontend/                    # Streamlit Frontend Application
│   ├── 📄 main.py                  # Entry point
│   ├── 📄 app.py                   # Main Streamlit application
│   ├── 📄 pyproject.toml           # Frontend dependencies
│   ├── 📄 Dockerfile               # Frontend container configuration
│   └── 📄 .python-version          # Python version specification
│
├── 📄 docker-compose.yaml          # Multi-service orchestration
├── 📄 .env                         # Environment variables (not in git)
├── 📄 .gitignore                   # Git exclusions
└── 📄 README.md                    # Project documentation
```   

## Setup Instructions
1. **Clone repo from github**
    ```bash
    git clone <repository_url>
    cd deal_brief_app
    ```

    There are two ways to continue with setup either UV for the backend and frontend and docker for the DB or use docker compose to setup everything.

2. **Using Docker compose**  In the project root directory run:

    ```bash
    docker compose up
    ```
    This will create and start the containers for the backend, frontend, and PostgreSQL database.

    **Note**: Ensure to add your OpenAI API Key to the `.env` file located in the project root directory before running the `docker compose up` command.

3. **Using uv (uvicorn/streamlit) and Docker for DB**

   - **Database Setup**:
     Ensure Docker is running and execute the following command in the project root directory to start the PostgreSQL database container:
     ```bash
     docker compose up -d db
     ```
   
   - **Backend Setup**:
     ```bash
     cd backend
     uv env install
     uv run src.main:app --reload --host 0.0.0.0
     ```
    - **Frontend Setup**:
      In a new terminal run:
        ```bash
        cd frontend
        uv env install
        streamlit run main.py --server.address=0.0.0.0
        ```

## Backend API Endpoints
- `POST /deals/`: Send the unstructured deal text to this endpoint to receive a structured deal brief in response frm the LLM.

    Sample Request Body:
    ```json
    {
        "text": "Founders: Maya Chen & Rob Diaz… building carbon-aware payments… raising $3.5m seed…"
    }
    ```

    Sample Response Body:
    ```json
    {
    "raw_text": "Founders: Maya Chen & Rob Diaz… building carbon-aware payments… raising $3.5m seed…",
    "status": "COMPLETED",
    "brief_data": {
        "tags": [
        "fintech",
        "payments",
        "carbon-aware",
        "seed"
        ],
        "stage": "Seed",
        "sector": "fintech/payments (carbon-aware)",
        "summary": [
        "Founders: Maya Chen and Rob Diaz",
        "Product: carbon-aware payments platform",
        "Sector: fintech/payments with sustainability focus",
        "Stage: Seed; raising $3.5M",
        "Geography: Undisclosed",
        "Traction: Not disclosed",
        "Competitive edge: Carbon-aware payments differentiation for ESG-aligned users",
        "Use of proceeds: product development and market validation",
        "Team: Core founding pair with domain expertise in payments",
        "Investment thesis: Early-stage fintech with sustainability angle and large green finance TAM"
        ],
        "founders": [
        "Maya Chen",
        "Rob Diaz"
        ],
        "geography": "Undisclosed",
        "round_size": "$3.5M",
        "company_name": "Unknown",
        "notable_metrics": [
        "Seed round target: $3.5M",
        "Founding team: Maya Chen & Rob Diaz",
        "Product concept: carbon-aware payments",
        "Early-stage concept, no disclosed traction",
        "Geography: Undisclosed"
        ]
    },
    "text_hash": "fd63a3c085518bf3fc815a95868b0e07d82d96f5a2bd0bf7fc1bd9d71ea228e9",
    "id": 18,
    "error_message": null,
    "created_at": "2026-02-03T10:22:09.556392"
    }
    ```

- `GET /deals/history`: Retrurns a list of the most recent 10 deals processed and stored in the database. 

- `DELETE /deals/{deal_id}`: Deletes a specific deal from the database using its unique ID.


## 🌐 Deployment

This application is ready for deployment on GitHub and various cloud platforms. Pre-built Docker images are automatically published to GitHub Container Registry on every commit to the main branch.

### Available Docker Images

- **Backend**: `ghcr.io/mohamed-abdelgawad99/deal_brief_app/backend:latest`
- **Frontend**: `ghcr.io/mohamed-abdelgawad99/deal_brief_app/frontend:latest`

### Deployment Guides

For comprehensive deployment instructions including:
- Using pre-built Docker images
- Deploying to AWS, GCP, Azure
- Kubernetes deployment
- Production best practices
- Security considerations

Please refer to **[DEPLOYMENT.md](DEPLOYMENT.md)**.

## 📦 CI/CD

The repository includes GitHub Actions workflows that automatically:
- Build Docker images for backend and frontend
- Run tests and security checks
- Publish images to GitHub Container Registry
- Tag images with version numbers and commit SHAs

Images are built on:
- Every push to `main` branch
- Every pull request (build only, no publish)
- Git tags (versioned releases)
