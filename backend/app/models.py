import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(String, unique=True, index=True, nullable=False)
    road_name = Column(String, nullable=False)
    road_class = Column(String, default="National Highway")
    district = Column(String, index=True, nullable=False)
    state = Column(String, default="Assam")
    
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    
    bridge_id = Column(String, nullable=True)
    length_km = Column(Float, default=10.0)
    terrain_type = Column(String, default="Hilly")
    landslide_susceptibility = Column(Float, default=0.5)
    base_risk_score = Column(Float, default=20.0)
    
    # Live status state machine: Open, Caution, Blocked, Unknown
    status = Column(String, default="Open")
    risk_score = Column(Float, default=15.0)  # 0 to 100
    confidence = Column(Float, default=0.90)   # 0.0 to 1.0
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def start_coords(self):
        return [self.start_lat, self.start_lon]

    @property
    def end_coords(self):
        return [self.end_lat, self.end_lon]

    incidents = relationship("IncidentReport", back_populates="segment")

class IncidentReport(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String, unique=True, index=True)
    segment_id = Column(String, ForeignKey("road_segments.segment_id"))
    
    incident_type = Column(String, nullable=False) # Landslide, Flash Flood, Bridge Damage, Mudslide, Blockade
    severity = Column(String, nullable=False)      # Low, Medium, High, Critical
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    photo_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    reporter = Column(String, default="Field Officer")
    client_report_id = Column(String, unique=True, index=True, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Verified")

    segment = relationship("RoadSegment", back_populates="incidents")

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String, index=True, nullable=False)
    rainfall_1h = Column(Float, default=0.0)
    rainfall_6h = Column(Float, default=0.0)
    rainfall_24h = Column(Float, default=0.0)
    forecast_24h_rain = Column(Float, default=0.0)
    wind_speed = Column(Float, default=0.0)
    temperature = Column(Float, default=25.0)
    source = Column(String, default="Open-Meteo API / IMD Adapter")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class VehicleTelemetry(Base):
    __tablename__ = "vehicle_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, index=True, nullable=False)
    shipment_id = Column(String, index=True, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=40.0)
    heading = Column(Float, default=0.0)
    is_simulated = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    driver_code = Column(String, unique=True, index=True, nullable=False)  # stable DRV-001, DRV-002, ...
    supabase_user_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, default="Warning") # Info, Warning, Urgent, Critical
    category = Column(String, default="Road Blocked") # Road Blocked, High Risk, ETA Breach, Emergency Corridor
    segment_id = Column(String, nullable=True)
    vehicle_id = Column(String, nullable=True)
    acknowledged = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(String, unique=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    priority_class = Column(String, default="P1") # P0 (Medical/Rescue), P1 (Food/Relief), P2 (Agri), P3 (General)
    cargo_type = Column(String, default="Emergency Medicines")
    vehicle_id = Column(String, nullable=True)
    assigned_route_json = Column(JSON, nullable=True)
    status = Column(String, default="In Transit") # Pending, In Transit, Rerouted, Delivered
    eta_timestamp = Column(DateTime, nullable=True)
