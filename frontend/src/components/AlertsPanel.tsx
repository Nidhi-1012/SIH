import React from 'react';
import { Alert } from '../types';
import { ShieldAlert, BellRing, CheckCircle, AlertCircle, Info } from 'lucide-react';

interface AlertsPanelProps {
  alerts: Alert[];
  onAcknowledge: (alertId: string) => void;
}

export const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts, onAcknowledge }) => {
  return (
    <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-3 h-full flex flex-col shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center space-x-2">
          <BellRing className="h-4 w-4 text-red-400" />
          <h2 className="font-display font-bold text-sm text-white">Live Disruption Alerts</h2>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 border border-slate-800">
          {alerts.length} Active
        </span>
      </div>

      <div className="overflow-y-auto space-y-2.5 flex-1 pr-1 max-h-[350px]">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">No active disruption alerts</div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.alert_id}
              className={`p-3 rounded-xl border transition ${
                alert.acknowledged
                  ? 'bg-slate-900/40 border-slate-800/80 opacity-60'
                  : alert.severity === 'Critical'
                  ? 'bg-red-950/40 border-red-800/60 glow-red'
                  : 'bg-amber-950/30 border-amber-800/50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-extrabold uppercase ${
                      alert.severity === 'Critical' ? 'bg-red-900 text-red-300' : 'bg-amber-900 text-amber-300'
                    }`}>
                      {alert.severity}
                    </span>
                    <h3 className="font-bold text-xs text-white">{alert.title}</h3>
                  </div>
                  <p className="text-xs text-slate-300">{alert.message}</p>
                  <span className="text-[10px] text-slate-500 block">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {!alert.acknowledged && (
                  <button
                    onClick={() => onAcknowledge(alert.alert_id)}
                    className="ml-2 p-1.5 rounded-lg bg-slate-800 hover:bg-emerald-950 hover:text-emerald-400 text-slate-400 text-[10px] font-bold border border-slate-700 transition"
                  >
                    Ack
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
