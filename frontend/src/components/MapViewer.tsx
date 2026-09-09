import React from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import { RoadSegment, IncidentReport, VehicleTelemetry } from '../types';
import { AlertTriangle, ShieldAlert, Truck, Info } from 'lucide-react';

interface MapViewerProps {
  segments: RoadSegment[];
  incidents: IncidentReport[];
  telemetry?: VehicleTelemetry;
  selectedSegment: RoadSegment | null;
  onSelectSegment: (segment: RoadSegment) => void;
  onOpenReportModal: () => void;
}

// Custom vehicle marker icon
const vehicleIcon = L.divIcon({
  className: 'custom-vehicle-marker',
  html: `<div style="background-color: #22c55e; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 3px solid #0f172a; box-shadow: 0 0 15px rgba(34, 197, 94, 0.8);">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#090d16" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
        </div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

// Custom incident marker icon
const incidentIcon = L.divIcon({
  className: 'custom-incident-marker',
  html: `<div style="background-color: #ef4444; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #ffffff; box-shadow: 0 0 15px rgba(239, 68, 68, 0.9);" class="animate-bounce">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
        </div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14]
});

export const MapViewer: React.FC<MapViewerProps> = ({
  segments,
  incidents,
  telemetry,
  selectedSegment,
  onSelectSegment,
  onOpenReportModal
}) => {
  // Center of North East logistics hub (Guwahati / Meghalaya border)
  const center: [number, number] = [26.0, 92.1];

  const getSegmentColor = (status: string, riskScore: number) => {
    if (status === 'Blocked') return '#ef4444'; // Red
    if (status === 'Caution' || riskScore >= 45) return '#f59e0b'; // Amber
    return '#22c55e'; // Green
  };

  return (
    <div className="relative w-full h-full rounded-2xl overflow-hidden glass-panel border border-slate-800 shadow-2xl">
      <MapContainer center={center} zoom={8} scrollWheelZoom={true} className="w-full h-full">
        {/* Dark theme map tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Road Segment Polylines */}
        {segments.map((seg) => {
          const positions: [number, number][] = [
            [seg.start_coords[0], seg.start_coords[1]],
            [seg.end_coords[0], seg.end_coords[1]]
          ];
          const color = getSegmentColor(seg.status, seg.risk_score);
          const isSelected = selectedSegment?.segment_id === seg.segment_id;

          return (
            <React.Fragment key={seg.segment_id}>
              <Polyline
                positions={positions}
                pathOptions={{
                  color: color,
                  weight: isSelected ? 8 : 5,
                  opacity: isSelected ? 1.0 : 0.85,
                  dashArray: seg.status === 'Blocked' ? '8, 8' : undefined
                }}
                eventHandlers={{
                  click: () => onSelectSegment(seg)
                }}
              >
                <Popup className="bg-slate-900 text-slate-100 rounded-xl">
                  <div className="p-1 space-y-2">
                    <h3 className="font-bold text-sm text-white">{seg.road_name}</h3>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">District:</span>
                      <span className="font-semibold text-emerald-400">{seg.district}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">Status:</span>
                      <span className={`font-bold px-2 py-0.5 rounded ${
                        seg.status === 'Blocked' ? 'bg-red-950 text-red-400' :
                        seg.status === 'Caution' ? 'bg-amber-950 text-amber-400' : 'bg-emerald-950 text-emerald-400'
                      }`}>
                        {seg.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">AI Risk Score:</span>
                      <span className="font-bold text-white">{seg.risk_score} / 100</span>
                    </div>
                    <button
                      onClick={() => onSelectSegment(seg)}
                      className="w-full mt-2 py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold rounded-lg text-xs transition"
                    >
                      View AI Explanation
                    </button>
                  </div>
                </Popup>
              </Polyline>

              {/* Endpoint Circle Markers */}
              <CircleMarker
                center={positions[0]}
                radius={4}
                pathOptions={{ color: color, fillColor: '#090d16', fillOpacity: 1, weight: 2 }}
              />
            </React.Fragment>
          );
        })}

        {/* Field Incident Markers */}
        {incidents.map((inc) => (
          <Marker key={inc.incident_id} position={[inc.lat, inc.lon]} icon={incidentIcon}>
            <Popup>
              <div className="p-1">
                <span className="text-[10px] uppercase font-bold text-red-400 bg-red-950 px-1.5 py-0.5 rounded">
                  {inc.severity} Severity
                </span>
                <h4 className="font-bold text-sm text-white mt-1">{inc.incident_type}</h4>
                <p className="text-xs text-slate-300 mt-1">{inc.notes || 'Field obstacle reported.'}</p>
                <div className="text-[11px] text-slate-400 mt-2">Reporter: {inc.reporter}</div>
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Live Vehicle Telemetry Pin */}
        {telemetry && (
          <Marker position={[telemetry.lat, telemetry.lon]} icon={vehicleIcon}>
            <Popup>
              <div className="p-1">
                <div className="flex items-center space-x-1 text-emerald-400 font-bold text-xs">
                  <Truck className="h-4 w-4" />
                  <span>{telemetry.vehicle_id}</span>
                </div>
                <div className="text-xs text-slate-200 mt-1">Cargo: {telemetry.cargo}</div>
                <div className="text-xs text-slate-400">Speed: {telemetry.speed_kmh} km/h</div>
                <span className="inline-block mt-1 text-[10px] font-bold text-amber-400 bg-amber-950/60 px-1.5 py-0.5 rounded">
                  SIMULATED GPS FEED
                </span>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {/* Floating Action Button for Field Report Submission */}
      <div className="absolute top-4 right-4 z-[500]">
        <button
          onClick={onOpenReportModal}
          className="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-xl shadow-lg glow-red transition transform hover:scale-105"
        >
          <AlertTriangle className="h-4 w-4" />
          <span className="text-xs">REPORT FIELD INCIDENT</span>
        </button>
      </div>

      {/* Map Legend */}
      <div className="absolute bottom-4 left-4 z-[500] glass-panel p-3 rounded-xl border border-slate-800 text-xs space-y-1.5 shadow-xl">
        <div className="font-bold text-slate-300 text-[11px] uppercase tracking-wider mb-1">Road Network Status</div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
          <span className="text-slate-300">Open (Normal Traffic)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-amber-500"></span>
          <span className="text-slate-300">Caution (High Rain / Slope Risk)</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-red-500"></span>
          <span className="text-slate-300">Blocked (Landslide / Bridge Cut)</span>
        </div>
      </div>
    </div>
  );
};
