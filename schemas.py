from typing import Optional, Literal
from pydantic import BaseModel, Field

class AllocationItem(BaseModel):
    label: str
    percent: float = Field(ge=0, le=100)
class ProcessStep(BaseModel):
    title: str
    description: str
class MarketValue(BaseModel):
    year: int
    value: str                     


class MarketSegment(BaseModel):
    category: str                   
    leader_text: str                
    leader_value: str               
    fast_text: str                  
    fast_cagr: str                  


class MarketDriver(BaseModel):
    driver: str
    impact: str                    
    relevance: str                  
    timeline: str                  
    term: Literal["short", "medium", "long"] = "medium"  


class MarketData(BaseModel):
    title: str = "Market Overview"
    cagr: Optional[str] = None     
    start: Optional[MarketValue] = None
    end: Optional[MarketValue] = None
    segments: Optional[list[MarketSegment]] = None
    drivers: Optional[list[MarketDriver]] = None


class CompetitorGroup(BaseModel):
    category: str                 
    names: list[str]


class ExtractedFacts(BaseModel):
    company_name: str
    one_liner: Optional[str] = None
    tagline: Optional[str] = None  
    ask_amount: Optional[str] = None
    allocation: Optional[list[AllocationItem]] = None
    process_steps: Optional[list[ProcessStep]] = None
    market: Optional[MarketData] = None
    competitors: Optional[list[CompetitorGroup]] = None


class DeckPlan(BaseModel):
    slide_types: list[str]