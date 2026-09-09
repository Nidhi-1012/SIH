import datetime
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Alert, RoadSegment, VehicleTelemetry, Shipment

# Alert Cooldown Cache: (category, segment_id) -> last_alert_timestamp
ALERT_COOLDOWN_CACHE = {}
COOLDOWN_MINUTES = 15.0

def evaluate_alert_triggers(
    db: Session,
    segment: Optional[RoadSegment] = None,
    telemetry: Optional[VehicleTelemetry] = None,
    shipment: Optional[Shipment] = None,
    eta_delay_minutes: float = 0.0
) -> Optional[Alert]:
    """
    Evaluates PRD §6.5 Alert Triggers with 15-minute cooldown window:
    1. Road Blocked Trigger
    2. High Disruption Probability Trigger (>60%)
    3. ETA Breach Trigger (>30 min delay)
    4. High-Risk Corridor Entry Trigger
    """
    now = datetime.datetime.utcnow()

    # Trigger 1: Road Blocked
    if segment and segment.status == "Blocked":
        key = ("ROAD_BLOCKED", segment.segment_id)
        if is_cooldown_expired(key, now):
            alert = create_alert(
                db,
                title=f"Road Blocked: {segment.road_name}",
                message=f"Critical blockage verified in {segment.district} district. Rerouting active shipments.",
                severity="Critical",
                category="Road Blocked",
                segment_id=segment.segment_id
            )
            ALERT_COOLDOWN_CACHE[key] = now
            return alert

    # Trigger 2: High Disruption Risk Score (> 60.0)
    if segment and segment.risk_score >= 60.0 and segment.status != "Blocked":
        key = ("HIGH_RISK", segment.segment_id)
        if is_cooldown_expired(key, now):
            alert = create_alert(
                db,
                title=f"High Disruption Risk ({segment.risk_score}/100)",
                message=f"Heavy weather / slope instability on {segment.road_name} ({segment.district}). Caution recommended.",
                severity="Warning",
                category="High Risk",
                segment_id=segment.segment_id
            )
            ALERT_COOLDOWN_CACHE[key] = now
            return alert

    # Trigger 3: ETA Breach (> 30 minutes delay)
    if eta_delay_minutes >= 30.0 and shipment:
        key = ("ETA_BREACH", shipment.shipment_id)
        if is_cooldown_expired(key, now):
            alert = create_alert(
                db,
                title=f"ETA Breach: Shipment {shipment.shipment_id}",
                message=f"Priority {shipment.priority_class} cargo delayed by {round(eta_delay_minutes)} mins due to route disruption.",
                severity="Urgent",
                category="ETA Breach",
                vehicle_id=shipment.vehicle_id
            )
            ALERT_COOLDOWN_CACHE[key] = now
            return alert

    # Trigger 4: High-Risk Corridor Entry
    if telemetry and segment and segment.risk_score >= 61.0:
        key = ("HIGH_RISK_ENTRY", f"{telemetry.vehicle_id}_{segment.segment_id}")
        if is_cooldown_expired(key, now):
            alert = create_alert(
                db,
                title=f"Vehicle Entry into High-Risk Corridor",
                message=f"Vehicle {telemetry.vehicle_id} entered high-risk zone {segment.road_name} ({segment.risk_score}/100 risk).",
                severity="Urgent",
                category="Corridor Entry",
                segment_id=segment.segment_id,
                vehicle_id=telemetry.vehicle_id
            )
            ALERT_COOLDOWN_CACHE[key] = now
            return alert

    return None

def is_cooldown_expired(key: tuple, now: datetime.datetime) -> bool:
    if key not in ALERT_COOLDOWN_CACHE:
        return True
    last_time = ALERT_COOLDOWN_CACHE[key]
    return (now - last_time).total_seconds() >= (COOLDOWN_MINUTES * 60.0)

def create_alert(
    db: Session,
    title: str,
    message: str,
    severity: str,
    category: str,
    segment_id: Optional[str] = None,
    vehicle_id: Optional[str] = None
) -> Alert:
    alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
    alert = Alert(
        alert_id=alert_id,
        title=title,
        message=message,
        severity=severity,
        category=category,
        segment_id=segment_id,
        vehicle_id=vehicle_id,
        acknowledged=False
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
