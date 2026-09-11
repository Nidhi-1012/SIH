import httpx
import logging
import os
import json
import uuid
import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config import settings
from app.database import engine, get_db, Base
from app.models import RoadSegment, IncidentReport, WeatherObservation, VehicleTelemetry, Alert, Shipment
from app.schemas import (
    RoadSegmentResponse, IncidentCreate, IncidentResponse, 
    WeatherResponse, RiskAssessment, RouteQuery, RouteRecommendation, AlertResponse
)
from app.services.weather_service import get_district_weather
from app.services.risk_model_service import calculate_segment_risk
from app.services.routing_service import calculate_candidate_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AI-Based Smart Logistics & Accessibility Intelligence Platform for North East Region (SIH26002)"
)

# Enable CORS for frontend dashboard & mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Emergency Mode Global State
EMERGENCY_MODE = False

@app.on_event("startup")
def seed_database():
    """Load pilot corridor seed dataset into database if empty."""
    db = next(get_db())
    if db.query(RoadSegment).count() == 0:
        possible_paths = ["../data/pilot_corridor.json", "./data/pilot_corridor.json", "data/pilot_corridor.json"]
        seed_file = next((p for p in possible_paths if os.path.exists(p)), None)
        if seed_file:
            with open(seed_file, "r") as f:
                data = json.load(f)
                for seg in data.get("road_segments", []):
                    db_seg = RoadSegment(
                        segment_id=seg["segment_id"],
                        road_name=seg["road_name"],
                        road_class=seg["road_class"],
                        district=seg["district"],
                        state=seg["state"],
                        start_lat=seg["start_coords"][0],
                        start_lon=seg["start_coords"][1],
                        end_lat=seg["end_coords"][0],
                        end_lon=seg["end_coords"][1],
                        bridge_id=seg.get("bridge_id"),
                        length_km=seg.get("length_km", 10.0),
                        terrain_type=seg.get("terrain_type", "Hilly"),
                        landslide_susceptibility=seg.get("landslide_susceptibility", 0.5),
                        base_risk_score=seg.get("base_risk_score", 20.0),
                        status=seg.get("status", "Open"),
                        risk_score=seg.get("base_risk_score", 20.0),
                        confidence=0.90
                    )
                    db.add(db_seg)
                db.commit()

        # Seed initial starter alerts
        if db.query(Alert).count() == 0:
            db.add(Alert(
                alert_id="ALT-INIT-01",
                title="Landslide Caution on NH-6",
                message="Increased soil saturation detected in Ri-Bhoi district. Drivers advised to maintain safe speed.",
                severity="Warning",
                category="High Risk",
                segment_id="SEG-NH6-03",
                acknowledged=False
            ))
            db.commit()

@app.get("/health")
def health_check():
    import redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"disconnected ({str(e)})"

    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "connected (PostgreSQL/PostGIS)"
    except Exception as e:
        db_status = f"disconnected ({str(e)})"

    return {
        "status": "healthy",
        "database": db_status,
        "redis": redis_status,
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "emergency_mode": EMERGENCY_MODE,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# 1. Road Segments Endpoints
@app.get("/api/v1/segments", response_model=List[RoadSegmentResponse])
def get_segments(db: Session = Depends(get_db)):
    return db.query(RoadSegment).all()

@app.get("/api/v1/segments/{segment_id}/risk", response_model=RiskAssessment)
async def get_segment_risk_assessment(segment_id: str, db: Session = Depends(get_db)):
    segment = db.query(RoadSegment).filter(RoadSegment.segment_id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Road segment not found")
        
    weather = await get_district_weather(segment.district)
    incidents = db.query(IncidentReport).filter(
        IncidentReport.segment_id == segment_id,
        IncidentReport.status == "Verified"
    ).all()
    
    risk_data = calculate_segment_risk(segment, weather.get("rainfall_24h", 0.0), incidents)
    return risk_data


logger = logging.getLogger("admin_auth")

SUPABASE_URL = "https://xtdrczsmgvjsyoeqmwvk.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0ZHJjenNtZ3Zqc3lvZXFtd3ZrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwNzkwNjIsImV4cCI6MjEwNDY1NTA2Mn0.W235P2PkflTcUbcxhJaoz8JehpirwclHEAFR0m9De8I"

async def verify_admin_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Gatekeeper: Verifies incoming request has a valid Supabase JWT Bearer token
    issued to an authorized administrator.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Registered Administrator session required to authorize or dismiss hazard reports."
        )
    
    token = authorization.split(" ")[1]
    url = f"{SUPABASE_URL}/auth/v1/user"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(
                url, 
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_ANON_KEY
                }
            )
            if res.status_code != 200:
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid or expired Administrator credentials. Please sign in to the Admin Portal."
                )
            user_data = res.json()
            logger.info(f"Verified Admin action by: {user_data.get('email')}")
            return user_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Supabase auth check error: {e}")
        raise HTTPException(status_code=401, detail="Authentication verification service offline.")

# 2. Incident Reporting API & Admin Verification Workflow (PRD §6.6 Field Reports)
@app.post("/api/v1/incidents", response_model=IncidentResponse)
def create_incident_report(inc: IncidentCreate, db: Session = Depends(get_db)):
    """
    Submits a new hazard report. Stored with status='Pending' for Admin review.
    Road segments are not altered and public alerts are not triggered until approved.
    """
    # Auto-match to nearest road segment if not explicitly provided
    segment_id = inc.segment_id
    if not segment_id:
        all_segs = db.query(RoadSegment).all()
        closest = min(
            all_segs, 
            key=lambda s: ((s.start_lat - inc.lat)**2 + (s.start_lon - inc.lon)**2)
        )
        segment_id = closest.segment_id if closest else "SEG-NH6-02"

    inc_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
    db_inc = IncidentReport(
        incident_id=inc_id,
        segment_id=segment_id,
        incident_type=inc.incident_type,
        severity=inc.severity,
        lat=inc.lat,
        lon=inc.lon,
        photo_url=inc.photo_url,
        notes=inc.notes,
        reporter=inc.reporter or "Citizen / Field Reporter",
        status="Pending"  # Stored as Pending for Admin Approval
    )
    db.add(db_inc)
    db.commit()
    db.refresh(db_inc)
    return db_inc

@app.get("/api/v1/incidents", response_model=List[IncidentResponse])
def get_incidents(status: Optional[str] = Query(None, description="Filter by status: Pending, Verified, Rejected"), db: Session = Depends(get_db)):
    query = db.query(IncidentReport)
    if status:
        query = query.filter(IncidentReport.status == status)
    return query.order_by(IncidentReport.timestamp.desc()).all()

@app.post("/api/v1/incidents/{incident_id}/approve", response_model=IncidentResponse)
async def approve_incident_report(incident_id: str, admin_user: dict = Depends(verify_admin_user), db: Session = Depends(get_db)):
    """
    Admin approval endpoint: marks hazard as Verified, updates road segment state,
    and publishes the alert to the live public feed & map.
    """
    incident = db.query(IncidentReport).filter(IncidentReport.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident report not found")
    
    incident.status = "Verified"

    # State Machine & Risk Score Update on Road Segment
    segment = db.query(RoadSegment).filter(RoadSegment.segment_id == incident.segment_id).first()
    if segment:
        is_severe = incident.severity in ["Critical", "High"] or incident.incident_type in ["Landslide", "Bridge Damage"]
        if incident.severity == "Critical":
            segment.status = "Blocked"
            segment.risk_score = min(segment.risk_score + 40.0, 98.0)
        elif is_severe:
            segment.status = "Caution"
            segment.risk_score = min(segment.risk_score + 25.0, 90.0)
        segment.last_updated = datetime.datetime.utcnow()

        # Trigger Official Live Broadcast Alert
        db.add(Alert(
            alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
            title=f"Verified {incident.incident_type} on {segment.road_name}",
            message=f"{incident.severity} severity hazard verified by Admin on {segment.road_name} ({segment.district}). {incident.notes or 'Proceed with extreme caution or seek alternate routes.'}",
            severity="Critical" if incident.severity == "Critical" else "Urgent",
            category="Road Blocked" if segment.status == "Blocked" else "Hazard Verified",
            segment_id=segment.segment_id,
            acknowledged=False
        ))

    db.commit()
    db.refresh(incident)
    return incident

@app.post("/api/v1/incidents/{incident_id}/reject", response_model=IncidentResponse)
async def reject_incident_report(incident_id: str, admin_user: dict = Depends(verify_admin_user), db: Session = Depends(get_db)):
    """
    Admin rejection endpoint: marks report as Rejected (false alarm / spam).
    No road changes or public alerts are created.
    """
    incident = db.query(IncidentReport).filter(IncidentReport.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident report not found")
    
    incident.status = "Rejected"
    db.commit()
    db.refresh(incident)
    return incident

# 3. Weather Ingestion API
@app.get("/api/v1/weather/{district}", response_model=WeatherResponse)
async def get_weather(district: str):
    data = await get_district_weather(district)
    return data

@app.post("/api/v1/weather/sync")
async def sync_all_districts_weather(db: Session = Depends(get_db)):
    """
    Syncs live IMD / Open-Meteo weather for all 10 pilot corridor districts,
    re-evaluates risk scores & status state machines across all road segments.
    """
    segments = db.query(RoadSegment).all()
    districts = set(s.district for s in segments)
    
    synced_results = {}
    for dist in districts:
        weather = await get_district_weather(dist)
        synced_results[dist] = weather
        
        db.add(WeatherObservation(
            district=dist,
            rainfall_1h=weather.get("rainfall_1h", 0.0),
            rainfall_6h=weather.get("rainfall_6h", 0.0),
            rainfall_24h=weather.get("rainfall_24h", 0.0),
            forecast_24h_rain=weather.get("forecast_24h_rain", 0.0),
            wind_speed=weather.get("wind_speed", 0.0),
            temperature=weather.get("temperature", 22.0),
            source=weather.get("source", "Open-Meteo API")
        ))

        dist_segments = [s for s in segments if s.district == dist]
        for seg in dist_segments:
            incidents = db.query(IncidentReport).filter(
                IncidentReport.segment_id == seg.segment_id,
                IncidentReport.status == "Verified"
            ).all()
            risk_info = calculate_segment_risk(seg, weather.get("rainfall_24h", 0.0), incidents)
            seg.risk_score = risk_info["risk_score"]
            seg.status = risk_info["status"]
            seg.confidence = risk_info["confidence"]
            seg.last_updated = datetime.datetime.utcnow()

    db.commit()
    return {
        "status": "synced",
        "districts_synced": len(districts),
        "weather_data": synced_results
    }

# 4. Risk-Aware Multi-Objective Routing API (PRD §6.3)
@app.post("/api/v1/route", response_model=List[RouteRecommendation])
def plan_route(query: RouteQuery, db: Session = Depends(get_db)):
    all_segments = db.query(RoadSegment).all()
    routes = calculate_candidate_routes(
        origin=query.origin,
        destination=query.destination,
        priority_class=query.priority_class,
        all_segments=all_segments
    )
    return routes

# 5. Alerts API
@app.get("/api/v1/alerts", response_model=List[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.timestamp.desc()).all()

@app.post("/api/v1/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}

# 6. Emergency Mode Toggle & Multilingual Safety Layer (PRD §6.7.1, §6.8)
@app.get("/api/v1/alerts/multilingual/{intent_key}")
def get_multilingual_alert(intent_key: str):
    from app.services.translation_service import get_multilingual_alert_payload
    return {
        "intent_key": intent_key,
        "translations": get_multilingual_alert_payload(intent_key)
    }

@app.post("/api/v1/emergency-mode/toggle")
def toggle_emergency_mode(db: Session = Depends(get_db)):
    global EMERGENCY_MODE
    EMERGENCY_MODE = not EMERGENCY_MODE
    from app.services.translation_service import get_multilingual_alert_payload
    
    translations = get_multilingual_alert_payload("EMERGENCY_MODE")
    if EMERGENCY_MODE:
        db.add(Alert(
            alert_id=f"ALT-EMERGENCY-{uuid.uuid4().hex[:4].upper()}",
            title="EMERGENCY MODE ACTIVATED (P0/P1)",
            message=f"{translations['en']} | {translations['hi']}",
            severity="Critical",
            category="Emergency Mode",
            acknowledged=False
        ))
        db.commit()

    return {
        "emergency_mode": EMERGENCY_MODE,
        "message": f"Emergency Mode is now {'ENABLED' if EMERGENCY_MODE else 'DISABLED'}. Priority P0 medical/relief corridors active.",
        "multilingual_broadcast": translations
    }

# 7. Telemetry & Live Vehicle Tracking API
@app.post("/api/v1/telemetry")
def ingest_vehicle_telemetry(data: dict, db: Session = Depends(get_db)):
    vehicle_id = data.get("vehicle_id", "VEH-MED-01")
    shipment_id = data.get("shipment_id", "SHIP-P0-MEDICINE-901")
    lat = float(data.get("lat", 26.1445))
    lon = float(data.get("lon", 91.7362))
    speed = float(data.get("speed_kmh", 40.0))
    heading = float(data.get("heading", 0.0))
    is_sim = bool(data.get("is_simulated", True))

    telemetry = VehicleTelemetry(
        vehicle_id=vehicle_id,
        shipment_id=shipment_id,
        lat=lat,
        lon=lon,
        speed_kmh=speed,
        heading=heading,
        is_simulated=is_sim
    )
    db.add(telemetry)
    
    # Check nearest segment and evaluate high-risk entry trigger
    all_segs = db.query(RoadSegment).all()
    if all_segs:
        closest = min(all_segs, key=lambda s: ((s.start_lat - lat)**2 + (s.start_lon - lon)**2))
        from app.services.alert_engine import evaluate_alert_triggers
        evaluate_alert_triggers(db, segment=closest, telemetry=telemetry)

    db.commit()
    return {
        "status": "ingested",
        "vehicle_id": vehicle_id,
        "lat": lat,
        "lon": lon,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@app.get("/api/v1/telemetry/simulate")
def simulate_vehicle_telemetry(vehicle_id: str = "VEH-MED-01"):
    # Generate live moving coordinates along Guwahati-Shillong NH6 corridor
    now = datetime.datetime.utcnow()
    progress = (now.second % 60) / 60.0
    
    start_lat, start_lon = 26.1445, 91.7362 # Guwahati
    end_lat, end_lon = 25.5788, 91.8933     # Shillong
    
    current_lat = start_lat + (end_lat - start_lat) * progress
    current_lon = start_lon + (end_lon - start_lon) * progress
    
    return {
        "vehicle_id": vehicle_id,
        "shipment_id": "SHIP-P0-MEDICINE-901",
        "lat": round(current_lat, 5),
        "lon": round(current_lon, 5),
        "speed_kmh": round(42.5 + (now.second % 10), 1),
        "heading": 175.0,
        "cargo": "P0 Emergency Medicines (Vaccines)",
        "is_simulated": True,
        "timestamp": now.isoformat()
    }

# Mount mobile web app static files
mobile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../mobile"))
if os.path.exists(mobile_path):
    app.mount("/mobile", StaticFiles(directory=mobile_path, html=True), name="mobile")
