from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field

# Common Models
class Message(BaseModel):
    """Represents a single message in a conversation thread."""
    role: Literal["user", "rep", "system", "prospect"]
    content: str
    timestamp: datetime


# 1. Prospect Research Models
class ProspectResearchRequest(BaseModel):
    """Request payload for generating a prospect brief."""
    linkedin_url: str
    company_website: str
    prospect_name: str

class ProspectBrief(BaseModel):
    """A comprehensive research summary of a prospect."""
    summary: str
    pain_points: List[str]
    trigger_events: List[str]
    talking_points: List[str]
    conversation_starter: str
    confidence_score: float = Field(ge=0.0, le=1.0)


# 2. Message Optimizer Models
class MessageOptimizeRequest(BaseModel):
    """Request payload to optimize a sales message."""
    draft_message: str
    prospect_brief_id: str
    channel: Literal["email", "linkedin", "sms"]

class OptimizedMessage(BaseModel):
    """The result of an optimized sales message."""
    original: str
    rewritten: str
    changes: List[str]
    channel_specific_notes: str


# 3. Objection Simulator Models
class ObjectionSimulateRequest(BaseModel):
    """Request payload to generate realistic objections based on persona."""
    product_description: str
    target_persona: str

class SimulatedObjections(BaseModel):
    """Generated objections from a simulated persona."""
    objections: List[str]

class ObjectionRespondRequest(BaseModel):
    """Request payload to score a rep's response to an objection."""
    objection: str
    rep_response: str

class ObjectionScore(BaseModel):
    """Scoring and feedback for a rep's objection handling."""
    clarity: int = Field(ge=0, le=10)
    empathy: int = Field(ge=0, le=10)
    forward_momentum: int = Field(ge=0, le=10)
    overall_score: int = Field(ge=0, le=30)
    improvement_tips: List[str]


# 4. Follow-up Strategist Models
class FollowUpStrategizeRequest(BaseModel):
    """Request payload to generate a follow-up strategy."""
    lead_id: str
    conversation_history: List[Message]

class FollowUpPlan(BaseModel):
    """A strategy and scheduled task for following up with a lead."""
    recommended_channel: Literal["email", "linkedin", "sms", "call"]
    optimal_send_time: datetime
    tone_shift: str
    draft_message: str
    task_id: str


# 5. A/B Email Tester Models
class ABTestGenerateRequest(BaseModel):
    """Request payload to generate A/B variants of a message."""
    base_message: str
    prospect_brief_id: str
    num_variants: int = Field(default=3, ge=1, le=5)

class ABVariant(BaseModel):
    """A single A/B test variant with predicted metrics."""
    angle: str
    content: str
    estimated_open_rate: float = Field(ge=0.0, le=100.0)
    estimated_reply_rate: float = Field(ge=0.0, le=100.0)
    reasoning: str

class ABTestResult(BaseModel):
    """The complete result of an A/B test generation request."""
    variants: List[ABVariant]
    recommended_variant_index: int
    reasoning: str


# 6. Sales Call Prep Models
class CallPrepRequest(BaseModel):
    """Request payload to generate a brief before a sales call."""
    lead_id: str
    meeting_time: datetime
    calendar_event_id: str

class ObjectionResponse(BaseModel):
    """An objection paired with a suggested response."""
    objection: str
    suggested_response: str

class CallBrief(BaseModel):
    """A pre-call summary and intelligence brief."""
    executive_summary: str
    likely_objections: List[ObjectionResponse]
    competitive_intel_notes: str
    recommended_opening_question: str
    key_metrics_to_mention: List[str]


# 7. Response Analyzer Models
class ResponseAnalyzeRequest(BaseModel):
    """Request payload to analyze an incoming prospect message."""
    lead_id: str
    incoming_message: str

class ResponseAnalysis(BaseModel):
    """Analysis of an incoming message and recommended next steps."""
    sentiment: Literal["positive", "neutral", "negative"]
    intent: Literal["interested", "stalling", "objecting", "ghosting", "other"]
    buying_signal_strength: int = Field(ge=0, le=100)
    urgency_score: int = Field(ge=0, le=100)
    next_action: Literal[
        "send_proposal", 
        "schedule_call", 
        "send_case_study", 
        "re_engage_later", 
        "escalate_to_manager"
    ]
    draft_response: str
