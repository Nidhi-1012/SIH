from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class RoadSegmentBase(BaseModel):
    segment_id: str
    road_name: str
    road_class: str
    district: str
    state: str
    start_coords: List[float]
    end_coords: List[float]
    bridge_id: Optional[str] = None
    length_km: float
    terrain_type: str
    landslide_susceptibility: float
    base_risk_score: float
    status: str

class RoadSegmentResponse(RoadSegmentBase):
    id: int
    risk_score: float
    confidence: float
    last_updated: datetime

    class Config:
        from_attributes = True

class IncidentCreate(BaseModel):
    segment_id: Optional[str] = None
    incident_type: str = Field(..., description="Landslide, Flood, Heavy Rain, Road Blockage, Accident, Damaged Road, Bridge Problem, Other")
    severity: str = Field(..., description="Low, Medium, High, Critical")
    lat: float
    lon: float
    photo_url: Optional[str] = None
    notes: Optional[str] = None
    reporter: Optional[str] = None

class IncidentResponse(IncidentCreate):
    id: int
    incident_id: str
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True

class WeatherResponse(BaseModel):
    district: str
    rainfall_1h: float
    rainfall_6h: float
    rainfall_24h: float
    forecast_24h_rain: float
    wind_speed: float
    temperature: float
    source: str
    timestamp: datetime

    class Config:
        from_attributes = True

class RiskAssessment(BaseModel):
    segment_id: str
    district: str
    risk_score: float # 0 to 100
    disruption_prob_6h: float
    disruption_prob_12h: float
    disruption_prob_24h: float
    confidence: float
    status: str
    top_factors: List[dict] # e.g. [{"factor": "Heavy Rain 24h", "impact": "+35%"}, ...]

class RouteQuery(BaseModel):
    origin: str
    destination: str
    priority_class: str = "P1" # P0, P1, P2, P3
    avoid_blocked: bool = True

class RouteRecommendation(BaseModel):
    route_id: str
    name: str
    distance_km: float
    eta_minutes: float
    overall_risk_score: float
    reliability_percentage: float
    recommendation_label: str # "Recommended", "Caution", "Avoid - Blocked"
    segments: List[RoadSegmentResponse]
    score_breakdown: dict
    geometry_points: Optional[List[List[float]]] = None
    turn_instructions: Optional[List[dict]] = None

class AlertResponse(BaseModel):
    id: int
    alert_id: str
    title: str
    message: str
    severity: str
    category: str
    segment_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    acknowledged: bool
    timestamp: datetime

    class Config:
        from_attributes = True
