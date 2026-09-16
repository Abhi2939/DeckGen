from typing import Optional
from pydantic import BaseModel,Field

class AllocationItem(BaseModel):
    label: str
    percent: float = Field(ge=0,le=100)

class ProcessStep(BaseModel):
    title: str
    description: str

class ExtractedFacts(BaseModel):

    company_name: str
    one_liner: Optional[str] = None
    ask_amount: Optional[str] = None
    allocation: Optional[list[AllocationItem]] = None
    process_steps: Optional[list[ProcessStep]] = None

class DeckPlan(BaseModel):
    slide_types: list[str]