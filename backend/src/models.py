from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB

class ProgressStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# LLM output schema
class DealBrief(SQLModel):
    summary: List[str] = Field(description="10-bullet investment brief")
    founders: List[str] = Field(description="List of founders")
    company_name: str = Field(description="Name of the company")
    sector: str = Field(description="Sector of the company")
    geography: str = Field(default=None, description="Geographical location of the company")
    stage: str = Field(description="Stage of the company; Seed / Series A")
    round_size: str = Field(description="Round size in USD")
    notable_metrics: List[str] = Field(description="Notable metrics about the company")
    tags: List[str] = Field(description="fintech/deep tech/climate tech + stage (Seed vs Series A)")

# --- API request/response schemas ---
class DealAPIRequest(SQLModel):
    text: str = Field(max_length=10000, description="Raw deal text blob")


class Deal(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    raw_text: str = Field(description="Raw deal text blob", sa_column_kwargs={"unique": False})
    text_hash: str = Field(index = True, unique = True, description="SHA256 hash for idempotency")

    # Tracking info
    status: ProgressStatus = Field(default=ProgressStatus.PENDING, description="Processing status of the deal")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")

    # Brief data >> LLM output
    brief_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB), description="Structured brief data extracted by LLM")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the deal was created")