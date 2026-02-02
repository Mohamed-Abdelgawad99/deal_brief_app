# backend/tests/test_ingest.py
import pytest
from src.models import DealBrief

# This tests if your Pydantic model correctly handles data
# effectively validating your schema logic.

def test_valid_deal_brief_structure():
    """Test that valid JSON data fits our Schema"""
    fake_llm_output = {
        "summary": ["Bullet 1", "Bullet 2"],
        "founders": ["Alice", "Bob"],
        "company_name": "Acme AI",
        "sector": "Fintech",
        "geography": "USA",
        "stage": "Seed",
        "round_size": "5M",
        "notable_metrics": ["Metric 1", "Metric 2"],
        "tags": ["Fintech", "AI"]
    }
    
    # Test to check the correctness of the shcema
    brief = DealBrief(**fake_llm_output)
    assert brief.company_name == "Acme AI"
    assert len(brief.summary) == 2

def test_invalid_deal_brief_missing_field():
    """Catch invalid data"""
    bad_output = {
        "summary": ["Bullet 1"]
    }
    
    with pytest.raises(ValueError):
        DealBrief(**bad_output)