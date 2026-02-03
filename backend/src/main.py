from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import os


from src.database import get_session, init_db, engine
from src.models import Deal, DealAPIRequest, DealBrief, ProgressStatus
from src.services import compute_text_hash, match_existing_deal_hash, parse_llm_deal_info
from src.utils.logger import logger
from src.seed_data import SEED_TEXT, SEED_BRIEF_DATA


def seed_data():
    """
    Seed initial data into the database
    """
    logger.info("Seeding initial data into the database")
    with Session(engine) as session:

        seed_text_hash = compute_text_hash(SEED_TEXT)
        existing = match_existing_deal_hash(session, seed_text_hash)
        if existing:
            logger.info("Seed data already exists in the database. Skip seeding.")
            return
        logger.info("Seeding initial record to the DB")

        seed_deal = Deal(
            raw_text=SEED_TEXT,
            text_hash=seed_text_hash,
            status=ProgressStatus.COMPLETED,
            brief_data=SEED_BRIEF_DATA
        )
        session.add(seed_deal)
        session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    #Initialize the database
    init_db()
    seed_data()
    yield

app = FastAPI(lifespan=lifespan,
              title="Deal Briefing API",
              description="API for ingesting and processing investment deal briefs using LLMs",)
logger.info("FastAPI application initialized")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://localhost:*", # in production this will be more restircted by specifying a specifc origins
    allow_credentials=True,
    allow_methods= ["*"],
    allow_headers= ["*"],
)


@app.post("/deals/", response_model=Deal)
def ingest_deal(deal_request: DealAPIRequest, session: Session = Depends(get_session)):
    """
    Docstring for ingest_deal
    
    :param deal_request: The API request containing deal information and following the API schema
    :type deal_request: DealAPIRequest schema
    :param session: The database session for executing queries
    :type session: Session
    """
    logger.info("API call to ingest a new deal")

    # Compute text hash
    text_hash = compute_text_hash(deal_request.text)

    # Check for existing deal with the same text hash
    existing_deal = match_existing_deal_hash(session, text_hash)
    if existing_deal:
        logger.info("Deal with the same text hash already exists. Checking deal status...")
        # IF there is an existing deal with same hash with complete status, I return the result stored in DB 
        if existing_deal.status == ProgressStatus.COMPLETED:
            logger.info("Existing deal processing is COMPLETED. Returning existing deal.")
            return existing_deal
        # If existing dal exist with failed status, I delete the record and reprocess the deal 
        elif existing_deal.status == ProgressStatus.FAILED:
            logger.warning(f"Existing deal found with status: {existing_deal.status}. Reprocessing the deal and updating the record if necessary.")
            session.delete(existing_deal)
            session.commit()
        # If the eisting deal is in pending or processing status, I return the deal as is and wait for the processing to finish.
        elif existing_deal.status in [ProgressStatus.PENDING, ProgressStatus.PROCESSING]:
            logger.info(f"Existing deal found with status: {existing_deal.status}. Returning existing deal for ongoing processing.")
            return existing_deal

    # Creating a new DB record with the new deal info and PROCESSING status
    logger.info("Creating new deal record in the database with PROCESSING status")
    new_deal = Deal(
        raw_text = deal_request.text,
        text_hash = text_hash,
        status = ProgressStatus.PROCESSING
    )
    session.add(new_deal)
    session.commit()
    logger.info(f"New deal record created with ID: {new_deal.id} and status: {new_deal.status}")

    # LLM request logic to get the deal brief
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable not set")
            return HTTPException(status_code=500, detail="Server configuration error")

        brief: DealBrief = parse_llm_deal_info(deal_request.text, api_key)

        ## updating the DB record
        new_deal.brief_data = brief.model_dump()
        new_deal.status = ProgressStatus.COMPLETED
        session.add(new_deal)
        session.commit()
        logger.info(f"Deal record with ID: {new_deal.id} updated with COMPLETED status")

    except Exception as e:
        new_deal.status = ProgressStatus.FAILED
        new_deal.error_message = "LLM processing error, try again later"
        session.add(new_deal)
        session.commit()
        logger.error(f"Deal record with ID: {new_deal.id} updated with FAILED status due to error: {e}")
        return HTTPException(status_code=500, detail="Error processing deal with LLM")

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
    try:
        statement = select(Deal).order_by(Deal.created_at.desc()).limit(10)
        results = session.exec(statement).all()
        logger.info(f"Fetched {len(results)} deals from the database")
    except Exception as e:
        logger.error(f"Error fetching deals records from database : {e}")
        raise HTTPException(status_code=500, detail="Error fetching deals from database")
    return results


@app.delete("/deals/{deal_id}", response_model=dict)
def delete_deal(deal_id: int, session: Session = Depends(get_session)):
    """
    Delete a deal by its ID.

    :param deal_id: The ID of the deal to delete
    :type deal_id: int
    :param session: The database session for executing queries
    :type session: Session
    :return: A dictionary indicating the result of the deletion
    :rtype: dict
    """
    logger.info(f"Attempting to delete deal with ID: {deal_id}")
    deal = session.get(Deal, deal_id)
    if not deal:
        logger.warning(f"Deal with ID: {deal_id} not found")
        return {"error": "Deal not found"}

    session.delete(deal)
    session.commit()
    logger.info(f"Deal with ID: {deal_id} deleted successfully")
    return {"message": "Deal deleted successfully"}

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