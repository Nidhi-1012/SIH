import axios from 'axios';
import { RoadSegment, IncidentReport, RiskAssessment, RouteRecommendation, Alert, VehicleTelemetry } from '../types';

const API_BASE = '/api/v1';

export const api = {
  // Road Segments
  getSegments: async (): Promise<RoadSegment[]> => {
    const res = await axios.get(`${API_BASE}/segments`);
    return res.data;
  },

  getSegmentRisk: async (segmentId: string): Promise<RiskAssessment> => {
    const res = await axios.get(`${API_BASE}/segments/${segmentId}/risk`);
    return res.data;
  },

  // Incidents
  getIncidents: async (): Promise<IncidentReport[]> => {
    const res = await axios.get(`${API_BASE}/incidents`);
    return res.data;
  },

  createIncident: async (incidentData: {
    segment_id?: string;
    incident_type: string;
    severity: string;
    lat: number;
    lon: number;
    notes?: string;
    photo_url?: string;
    reporter?: string;
  }): Promise<IncidentReport> => {
    const res = await axios.post(`${API_BASE}/incidents`, incidentData);
    return res.data;
  },

  // Route Planning
  planRoute: async (origin: string, destination: string, priorityClass: string = "P1"): Promise<RouteRecommendation[]> => {
    const res = await axios.post(`${API_BASE}/route`, {
      origin,
      destination,
      priority_class: priorityClass,
      avoid_blocked: true
    });
    return res.data;
  },

  // Alerts
  getAlerts: async (): Promise<Alert[]> => {
    const res = await axios.get(`${API_BASE}/alerts`);
    return res.data;
  },

  acknowledgeAlert: async (alertId: string): Promise<void> => {
    await axios.post(`${API_BASE}/alerts/${alertId}/acknowledge`);
  },

  // Emergency Mode Toggle
  toggleEmergencyMode: async (): Promise<{ emergency_mode: boolean; message: string }> => {
    const res = await axios.post(`${API_BASE}/emergency-mode/toggle`);
    return res.data;
  },

  // Simulated Telemetry
  getSimulatedTelemetry: async (vehicleId: string = "VEH-MED-01"): Promise<VehicleTelemetry> => {
    const res = await axios.get(`${API_BASE}/telemetry/simulate?vehicle_id=${vehicleId}`);
    return res.data;
  }
};
