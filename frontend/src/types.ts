export interface RoadSegment {
  id: number;
  segment_id: str;
  road_name: string;
  road_class: string;
  district: string;
  state: string;
  start_coords: [number, number];
  end_coords: [number, number];
  bridge_id?: string;
  length_km: number;
  terrain_type: string;
  landslide_susceptibility: number;
  base_risk_score: number;
  status: 'Open' | 'Caution' | 'Blocked' | 'Unknown';
  risk_score: number;
  confidence: number;
  last_updated: string;
}

export interface IncidentReport {
  id: number;
  incident_id: string;
  segment_id: string;
  incident_type: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  lat: number;
  lon: number;
  photo_url?: string;
  notes?: string;
  reporter: string;
  timestamp: string;
  status: string;
}

export interface RiskFactor {
  factor: string;
  impact: string;
  type: string;
}

export interface RiskAssessment {
  segment_id: string;
  district: string;
  risk_score: number;
  disruption_prob_6h: number;
  disruption_prob_12h: number;
  disruption_prob_24h: number;
  confidence: number;
  status: string;
  top_factors: RiskFactor[];
}

export interface RouteRecommendation {
  route_id: string;
  name: string;
  distance_km: number;
  eta_minutes: number;
  overall_risk_score: number;
  reliability_percentage: number;
  recommendation_label: string;
  segments: RoadSegment[];
  score_breakdown: {
    time_weight: number;
    distance_weight: number;
    risk_weight: number;
    priority_class: string;
  };
}

export interface Alert {
  id: number;
  alert_id: string;
  title: string;
  message: string;
  severity: 'Info' | 'Warning' | 'Urgent' | 'Critical';
  category: string;
  segment_id?: string;
  vehicle_id?: string;
  acknowledged: boolean;
  timestamp: string;
}

export interface VehicleTelemetry {
  vehicle_id: string;
  shipment_id: string;
  lat: number;
  lon: number;
  speed_kmh: number;
  heading: number;
  cargo: string;
  is_simulated: boolean;
  timestamp: string;
}
