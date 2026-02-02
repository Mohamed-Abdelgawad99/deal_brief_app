import hashlib
import instructor 
from json_repair import repair_json
from openai import OpenAI
from sqlmodel import Session, select
from src.models import Deal, DealBrief, ProgressStatus


def compute_text_hash(text:str) -> str:
    """Compute SHA256 hash of the input text for idempotency"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def match_existing_deal_hash(session: Session, text_hash: str) -> Deal:
    """Check if a deal with the same text hash already exists in the DB"""
    statement = select(Deal).where(Deal.text_hash == text_hash)
    result = session.exec(statement).first()
    return result

def parse_llm_deal_info(text: str, api_key: str) -> DealBrief:
    """Use LLM to parse unstructured deal text into structured DealBrief"""
    
    client = instructor.from_openai(OpenAI(api_key=api_key))

    system_prompt = (
        "You are a VC analyst assistant. Extract structured data from the text below. "
        "Output valid JSON matching the schema. If fields are missing, make reasonable inferences or leave null."
    )

    try:
        response = client.chat.completions.create(
            model = "gpt-5-nano",
            response_model = DealBrief,
            max_retries = 3,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"The unstructred deal text is: \n{text}"}
            ]
        )

        return response
    except Exception as e:
        raise e