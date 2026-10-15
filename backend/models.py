"""Pydantic data schemas for MuryaAI voice resolution pipeline."""
from typing import Optional, Any
from pydantic import BaseModel, Field

class ChannelType(str):
    WEB = "web"
    IVR = "ivr_phone"
    WHATSAPP = "whatsapp_voice"

class NigerianLanguage(str):
    HAUSA = "hausa"
    YORUBA = "yoruba"
    IGBO = "igbo"
    NIGERIAN_ENGLISH = "nigerian_english"

class TextQueryRequest(BaseModel):
    text: str = Field(..., description="Query in Hausa, Yoruba, Igbo, or Nigerian-accented English")
    language: Optional[str] = Field(None, description="Optional forced language code: hausa, yoruba, igbo, nigerian_english")
    channel: str = Field(default="web", description="Channel: web, ivr_phone, whatsapp_voice")
    caller_id: Optional[str] = Field(default="08031234567", description="Caller phone number")

class VoiceQueryRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio payload")
    audio_format: str = Field(default="audio/webm", description="MIME format of audio")
    language: Optional[str] = Field(default=None, description="Optional specified language")
    channel: str = Field(default="web", description="Channel: web, ivr_phone, whatsapp_voice")
    caller_id: Optional[str] = Field(default="08031234567", description="Caller phone number")
    transcription_hint: Optional[str] = Field(default=None, description="Client-side transcribed speech if available")

class ExtractedEntities(BaseModel):
    domain: str = Field(..., description="'banking_pos', 'electricity_disco', or 'general_support'")
    intent: str = Field(..., description="Classified intent, e.g., 'failed_pos_debit', 'missing_meter_token'")
    amount: Optional[float] = None
    account_or_phone: Optional[str] = None
    meter_number: Optional[str] = None
    rrn: Optional[str] = None
    disco: Optional[str] = None
    urgency: str = "medium"

class ResolutionAction(BaseModel):
    action_type: str = Field(..., description="e.g. 'instant_token_recovered', 'cbn_dispute_ticket_logged', 'reversal_verified'")
    ticket_id: str
    status: str
    details: dict[str, Any]
    sla_hours: int = 24

class VoiceQueryResponse(BaseModel):
    session_id: str
    channel: str
    detected_language: str
    language_confidence: float
    transcription: str
    translated_english: Optional[str] = None
    entities: ExtractedEntities
    resolution_action: ResolutionAction
    response_text_local: str
    response_text_en: str
    audio_base64: Optional[str] = None
    latency_ms: dict[str, float]
    natlas_engine_used: str

class BenchmarkItem(BaseModel):
    id: str
    language: str
    domain: str
    audio_text: str
    expected_intent: str
    actual_intent: Optional[str] = None
    accuracy_pass: bool = False
    latency_ms: float = 0.0
