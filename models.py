from pydantic import BaseModel, Field, conint, HttpUrl
from typing import Dict, Any

class HealthCheckResponse(BaseModel):
    """
    Response model for the API health check endpoint.
    """
    status: str
    message: str
    timestamp: str

class WebhookPayload(BaseModel):
    event_type: str
    data: Dict[str, Any]

class VideoProcessingPayload(BaseModel):
    video_url: HttpUrl
    user_id: str
    processing_strategy: str