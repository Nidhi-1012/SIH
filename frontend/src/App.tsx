import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MapViewer } from './components/MapViewer';
import { RouteIntelligence } from './components/RouteIntelligence';
import { AlertsPanel } from './components/AlertsPanel';
import { RiskExplanationModal } from './components/RiskExplanationModal';
import { IncidentFormModal } from './components/IncidentFormModal';
import { api } from './services/api';
import { RoadSegment, IncidentReport, RiskAssessment, RouteRecommendation, Alert, VehicleTelemetry } from './types';
import { Activity, ShieldCheck, MapPin, AlertTriangle, CloudRain, Zap } from 'lucide-react';

export const App: React.FC = () => {
  const [segments, setSegments] = useState<RoadSegment[]>([]);
  const [incidents, setIncidents] = useState<IncidentReport[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [routes, setRoutes] = useState<RouteRecommendation[]>([]);
  const [telemetry, setTelemetry] = useState<VehicleTelemetry | undefined>(undefined);
  const [emergencyMode, setEmergencyMode] = useState<boolean>(false);

  const [selectedSegment, setSelectedSegment] = useState<RoadSegment | null>(null);
  const [riskAssessment, setRiskAssessment] = useState<RiskAssessment | null>(null);
  const [isReportModalOpen, setIsReportModalOpen] = useState<boolean>(false);
  const [isRouteLoading, setIsRouteLoading] = useState<boolean>(false);

  // Fetch initial data
  const fetchData = async () => {
    try {
      const segs = await api.getSegments();
      setSegments(segs);
      const incs = await api.getIncidents();
      setIncidents(incs);
      const alrts = await api.getAlerts();
      setAlerts(alrts);

      // Initial route calculation sample
      if (segs.length > 0 && routes.length === 0) {
        const initialRoutes = await api.planRoute('Guwahati (Assam)', 'Silchar (Assam via NH-6)', 'P0');
        setRoutes(initialRoutes);
      }
    } catch (err) {
      console.warn("API offline - rendering mock data fallback:", err);
      // Fallback mock segments if server isn't running yet
      const fallbackSegs: RoadSegment[] = [
        {
          id: 1, segment_id: 'SEG-NH6-01', road_name: 'NH-6 Guwahati to Khanapara', road_class: 'National Highway',
          district: 'Kamrup Metropolitan', state: 'Assam', start_coords: [26.1445, 91.7362], end_coords: [26.1158, 91.8210],
          length_km: 11.5, terrain_type: 'Plains', landslide_susceptibility: 0.1, base_risk_score: 12, status: 'Open',
          risk_score: 14, confidence: 0.95, last_updated: new Date().toISOString()
        },
        {
          id: 2, segment_id: 'SEG-NH6-02', road_name: 'NH-6 Khanapara to Nongpoh', road_class: 'National Highway',
          district: 'Ri-Bhoi', state: 'Meghalaya', start_coords: [26.1158, 91.8210], end_coords: [25.9001, 91.8805],
          length_km: 28.4, terrain_type: 'Hilly', landslide_susceptibility: 0.65, base_risk_score: 38, status: 'Caution',
          risk_score: 52, confidence: 0.91, last_updated: new Date().toISOString()
        },
        {
          id: 3, segment_id: 'SEG-NH6-03', road_name: 'NH-6 Nongpoh to Umiam Lake', road_class: 'National Highway',
          district: 'Ri-Bhoi', state: 'Meghalaya', start_coords: [25.9001, 91.8805], end_coords: [25.6542, 91.9056],
          length_km: 31.2, terrain_type: 'Landslide Zone', landslide_susceptibility: 0.85, base_risk_score: 68, status: 'Blocked',
          risk_score: 88, confidence: 0.94, last_updated: new Date().toISOString()
        }
      ];
      setSegments(fallbackSegs);
    }
  };

  useEffect(() => {
    fetchData();

    // Poll live simulated vehicle telemetry every 3 seconds
    const interval = setInterval(async () => {
      try {
        const telem = await api.getSimulatedTelemetry();
        setTelemetry(telem);
      } catch (e) {
        // quiet fallback
      }
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const handleSelectSegment = async (seg: RoadSegment) => {
    setSelectedSegment(seg);
    try {
      const risk = await api.getSegmentRisk(seg.segment_id);
      setRiskAssessment(risk);
    } catch (e) {
      setRiskAssessment({
        segment_id: seg.segment_id,
        district: seg.district,
        risk_score: seg.risk_score,
        disruption_prob_6h: 0.45,
        disruption_prob_12h: 0.68,
        disruption_prob_24h: 0.82,
        confidence: 0.90,
        status: seg.status,
        top_factors: [
          { factor: `Monsoon Rainfall (${seg.district})`, impact: '+35 pts risk', type: 'Weather' },
          { factor: 'High Slope Vulnerability', impact: '+22 pts risk', type: 'Terrain' }
        ]
      });
    }
  };

  const handleCalculateRoute = async (origin: string, destination: string, priorityClass: string) => {
    setIsRouteLoading(true);
    try {
      const res = await api.planRoute(origin, destination, priorityClass);
      setRoutes(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRouteLoading(false);
    }
  };

  const handleCreateIncident = async (incidentData: any) => {
    try {
      await api.createIncident(incidentData);
      setIsReportModalOpen(false);
      await fetchData(); // Refresh segments & alerts
    } catch (e) {
      console.error(e);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId);
      setAlerts(alerts.map(a => a.alert_id === alertId ? { ...a, acknowledged: true } : a));
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleEmergency = async () => {
    try {
      const res = await api.toggleEmergencyMode();
      setEmergencyMode(res.emergency_mode);
      // Re-calculate route in P0 emergency mode automatically
      handleCalculateRoute('Guwahati (Assam)', 'Silchar (Assam via NH-6)', 'P0');
    } catch (e) {
      setEmergencyMode(!emergencyMode);
    }
  };

  const unreadAlerts = alerts.filter(a => !a.acknowledged).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        emergencyMode={emergencyMode}
        onToggleEmergency={handleToggleEmergency}
        unreadAlertCount={unreadAlerts}
      />

      <main className="flex-1 p-4 md:p-6 space-y-5 max-w-[1700px] mx-auto w-full">
        {/* Top Summary Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold block uppercase">Monitored Corridors</span>
              <span className="text-xl font-bold text-white mt-0.5 block">10 Segments</span>
            </div>
            <div className="p-2.5 rounded-xl bg-emerald-950 text-emerald-400 border border-emerald-800">
              <MapPin className="h-5 w-5" />
            </div>
          </div>

          <div className="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold block uppercase">Active Blockades</span>
              <span className="text-xl font-bold text-red-400 mt-0.5 block">
                {segments.filter(s => s.status === 'Blocked').length} Critical
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-red-950 text-red-400 border border-red-800">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>

          <div className="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold block uppercase">Weather Feed</span>
              <span className="text-xl font-bold text-teal-300 mt-0.5 block">IMD / Open-Meteo</span>
            </div>
            <div className="p-2.5 rounded-xl bg-teal-950 text-teal-400 border border-teal-800">
              <CloudRain className="h-5 w-5" />
            </div>
          </div>

          <div className="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-slate-400 font-semibold block uppercase">Telemetry Status</span>
              <span className="text-xl font-bold text-emerald-400 mt-0.5 block">Live 3s Refresh</span>
            </div>
            <div className="p-2.5 rounded-xl bg-emerald-950 text-emerald-400 border border-emerald-800">
              <Zap className="h-5 w-5" />
            </div>
          </div>
        </div>

        {/* Main Grid: Interactive Map + Disruption Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 h-[580px]">
          <div className="lg:col-span-2 h-full">
            <MapViewer
              segments={segments}
              incidents={incidents}
              telemetry={telemetry}
              selectedSegment={selectedSegment}
              onSelectSegment={handleSelectSegment}
              onOpenReportModal={() => setIsReportModalOpen(true)}
            />
          </div>

          <div className="h-full">
            <AlertsPanel alerts={alerts} onAcknowledge={handleAcknowledgeAlert} />
          </div>
        </div>

        {/* Route Intelligence Panel */}
        <div>
          <RouteIntelligence
            routes={routes}
            onCalculateRoute={handleCalculateRoute}
            isLoading={isRouteLoading}
          />
        </div>
      </main>

      {/* SHAP Risk Explanation Modal */}
      {selectedSegment && (
        <RiskExplanationModal
          segment={selectedSegment}
          riskAssessment={riskAssessment}
          onClose={() => setSelectedSegment(null)}
        />
      )}

      {/* Field Report Submission Modal */}
      {isReportModalOpen && (
        <IncidentFormModal
          segments={segments}
          onClose={() => setIsReportModalOpen(false)}
          onSubmit={handleCreateIncident}
        />
      )}
    </div>
  );
};
