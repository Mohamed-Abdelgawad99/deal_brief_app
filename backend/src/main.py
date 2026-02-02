from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import os

from src.database import get_session, init_db
from src.models import Deal, DealAPIRequest, DealBrief, ProgressStatus
from src.services import compute_text_hash, match_existing_deal_hash, parse_llm_deal_info
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    init_db()
    yield
    # Shutdown: Any cleanup can be done here if necessary

app = FastAPI(lifespan=lifespan,
              title="Deal Briefing API",
              description="API for ingesting and processing investment deal briefs using LLMs",)
logger.info("FastAPI application initialized")

@app.post("/deals/", response_model=Deal)
def ingest_deal(deal_request: DealAPIRequest, session: Session = Depends(get_session)):
    """
    Docstring for ingest_deal
    
    :param deal_request: The API request containing deal information and following the API schema
    :type deal_request: DealAPIRequest
    :param session: The database session for executing queries
    :type session: Session


    """
    logger.info("API call to ingest a new deal")

    # Compute text hash for idempotency
    text_hash = compute_text_hash(deal_request.text)

    # Check for existing deal with the same text hash
    existing_deal = match_existing_deal_hash(session, text_hash)
    if existing_deal:
        logger.info("Deal with the same text hash already exists. Returning existing deal.")
        return existing_deal

    # Parse deal information using LLM
    logger.info("Creating new deal record in the database with PROCESSING status")
    new_deal = Deal(
        raw_text = deal_request.text,
        text_hash = text_hash,
        status = ProgressStatus.PROCESSING
    )
    session.add(new_deal)
    session.commit()
    logger.info(f"New deal record created with ID: {new_deal.id} and status: {new_deal.status}")

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        brief: DealBrief = parse_llm_deal_info(deal_request.text, api_key)

        ## updating the DB record
        new_deal.brief_data = brief.model_dump()
        new_deal.status = ProgressStatus.COMPLETED
        session.add(new_deal)
        session.commit()
        logger.info(f"Deal record with ID: {new_deal.id} updated with COMPLETED status")

    except Exception as e:
        new_deal.status = ProgressStatus.FAILED
        new_deal.error_message = str(e)
        session.add(new_deal)
        session.commit()
        logger.error(f"Deal record with ID: {new_deal.id} updated with FAILED status due to error: {e}")

    return new_deal

@app.get("/deals/history", response_model=list[Deal])
def list_deals(session: Session = Depends(get_session)):
    """
    List 10 last deals in the database.

    :param session: The database session for executing queries
    :type session: Session
    :return: A list of the 10 most recent deals
    :rtype: list[Deal]
    """
    logger.info("Fetching the 10 most recent deals from the database")
    statement = select(Deal).order_by(Deal.created_at.desc()).limit(10)
    results = session.exec(statement).all()
    logger.info(f"Fetched {len(results)} deals from the database")
    return results


@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Deal Briefing API!",
            "endpoints": {
                "/deals/ [POST]": "Ingest a new deal for processing",
                "/deals/history [GET]": "List the 10 most recent deals"
            },
            "status": "Running",
            "Ownership": "Palm AI"}