import React, { useState } from 'react';
import { RouteRecommendation } from '../types';
import { Navigation, Clock, ShieldCheck, AlertTriangle, CheckCircle2, Sliders, Layers } from 'lucide-react';

interface RouteIntelligenceProps {
  routes: RouteRecommendation[];
  onCalculateRoute: (origin: string, destination: string, priorityClass: string) => void;
  isLoading: boolean;
}

export const RouteIntelligence: React.FC<RouteIntelligenceProps> = ({
  routes,
  onCalculateRoute,
  isLoading
}) => {
  const [origin, setOrigin] = useState('Guwahati (Assam)');
  const [destination, setDestination] = useState('Silchar (Assam via NH-6)');
  const [priorityClass, setPriorityClass] = useState('P0');

  const handlePrioritySelect = (pClass: string) => {
    setPriorityClass(pClass);
    onCalculateRoute(origin, destination, pClass);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCalculateRoute(origin, destination, priorityClass);
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 shadow-xl">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2">
          <Navigation className="h-5 w-5 text-emerald-400" />
          <div>
            <h2 className="font-display font-bold text-base text-white">AI Risk-Aware Route Intelligence</h2>
            <p className="text-xs text-slate-400">PRD §6.3 Multi-Objective Score: RouteScore = wT·T + wD·D + wR·R + wC·C</p>
          </div>
        </div>

        {/* Priority Class Selector Pills */}
        <div className="flex items-center space-x-1.5 bg-slate-900/90 p-1 rounded-xl border border-slate-800">
          {[
            { id: 'P0', label: 'P0 Emergency', color: 'text-red-400 bg-red-950/60 border-red-800' },
            { id: 'P1', label: 'P1 Relief', color: 'text-amber-400 bg-amber-950/60 border-amber-800' },
            { id: 'P2', label: 'P2 Agri', color: 'text-teal-300 bg-teal-950/60 border-teal-800' },
            { id: 'P3', label: 'P3 Freight', color: 'text-slate-300 bg-slate-800 border-slate-700' }
          ].map((p) => (
            <button
              key={p.id}
              onClick={() => handlePrioritySelect(p.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition border ${
                priorityClass === p.id ? p.color : 'text-slate-400 border-transparent hover:text-white'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Controls */}
      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <div>
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Origin Logistics Hub</label>
          <select
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="Guwahati (Assam)">Guwahati (Assam)</option>
            <option value="Tezpur (Assam)">Tezpur (Assam)</option>
            <option value="Shillong (Meghalaya)">Shillong (Meghalaya)</option>
          </select>
        </div>

        <div>
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Destination Corridor</label>
          <select
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="Silchar (Assam via NH-6)">Silchar (Assam via NH-6)</option>
            <option value="Tawang (Arunachal Pradesh via NH-13)">Tawang (Arunachal Pradesh)</option>
            <option value="Imphal (Manipur via NH-2)">Imphal (Manipur via NH-2)</option>
          </select>
        </div>

        <div>
          <label className="text-[11px] font-semibold text-slate-400 block mb-1">Active Cargo Class</label>
          <input
            type="text"
            disabled
            value={`${priorityClass} Priority Active`}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-emerald-400 font-bold"
          />
        </div>

        <div className="flex items-end">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2 px-4 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-slate-950 font-extrabold rounded-xl text-xs transition shadow-lg glow-emerald"
          >
            {isLoading ? 'Ranking Candidate Routes...' : 'RANK CANDIDATE ROUTES'}
          </button>
        </div>
      </form>

      {/* Candidate Route Comparison Cards */}
      <div className="space-y-3 pt-2">
        {routes.map((route, idx) => (
          <div
            key={route.route_id || idx}
            className={`p-4 rounded-xl border transition duration-200 ${
              route.recommendation_label.includes('Recommended')
                ? 'bg-slate-900/90 border-emerald-500/50 glow-emerald'
                : route.recommendation_label.includes('Avoid')
                ? 'bg-slate-900/60 border-red-900/50 opacity-70'
                : 'bg-slate-900/60 border-slate-800'
            }`}
          >
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
              <div className="flex items-start space-x-3">
                {route.recommendation_label.includes('Recommended') ? (
                  <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <h3 className="font-bold text-sm text-white">{route.name}</h3>
                  <div className="flex items-center space-x-3 text-xs text-slate-400 mt-1">
                    <span className="flex items-center space-x-1">
                      <Clock className="h-3.5 w-3.5 text-slate-400" />
                      <span>ETA: {route.eta_minutes} mins</span>
                    </span>
                    <span>•</span>
                    <span>Distance: {route.distance_km} km</span>
                    <span>•</span>
                    <span className="text-slate-300 font-medium">
                      RouteScore: <strong className="text-emerald-400">{route.score_breakdown?.composite_route_score || '0.42'}</strong>
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-4 w-full md:w-auto justify-between md:justify-end">
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 block uppercase">Overall Risk</span>
                  <span className={`text-sm font-extrabold ${
                    route.overall_risk_score >= 60 ? 'text-red-400' :
                    route.overall_risk_score >= 35 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {route.overall_risk_score} / 100
                  </span>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-slate-400 block uppercase">Reliability</span>
                  <span className="text-sm font-extrabold text-emerald-400">
                    {route.reliability_percentage}%
                  </span>
                </div>

                <span className={`px-3 py-1.5 rounded-lg text-xs font-bold ${
                  route.recommendation_label.includes('Recommended')
                    ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    : route.recommendation_label.includes('Avoid')
                    ? 'bg-red-950 text-red-400 border border-red-800'
                    : 'bg-amber-950 text-amber-400 border border-amber-800'
                }`}>
                  {route.recommendation_label}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
