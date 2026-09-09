import React, { useState } from 'react';
import { X, AlertTriangle, Send, MapPin, Camera } from 'lucide-react';
import { RoadSegment } from '../types';

interface IncidentFormModalProps {
  segments: RoadSegment[];
  onClose: () => void;
  onSubmit: (incidentData: any) => void;
}

export const IncidentFormModal: React.FC<IncidentFormModalProps> = ({
  segments,
  onClose,
  onSubmit
}) => {
  const [selectedSegmentId, setSelectedSegmentId] = useState(segments[1]?.segment_id || 'SEG-NH6-02');
  const [incidentType, setIncidentType] = useState('Landslide');
  const [severity, setSeverity] = useState('Critical');
  const [notes, setNotes] = useState('');
  const [reporter, setReporter] = useState('Field Officer (Ri-Bhoi Post)');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const seg = segments.find(s => s.segment_id === selectedSegmentId) || segments[0];
    
    onSubmit({
      segment_id: selectedSegmentId,
      incident_type: incidentType,
      severity: severity,
      lat: seg.start_lat + 0.05,
      lon: seg.start_lon + 0.05,
      notes: notes || 'Severe mudslide reported across both highway lanes.',
      reporter: reporter
    });
  };

  return (
    <div className="fixed inset-0 z-[600] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel w-full max-w-lg rounded-2xl border border-slate-700 p-6 shadow-2xl space-y-5 relative">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-red-950 border border-red-800 text-red-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-display font-bold text-base text-white">Submit Field Incident Report</h2>
              <p className="text-xs text-slate-400">Triggers real-time map update & automated rerouting</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-slate-900 text-slate-400 hover:text-white border border-slate-800 transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Affected Road Segment</label>
            <select
              value={selectedSegmentId}
              onChange={(e) => setSelectedSegmentId(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-red-500"
            >
              {segments.map((seg) => (
                <option key={seg.segment_id} value={seg.segment_id}>
                  {seg.road_name} ({seg.district})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Incident Type</label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-red-500"
              >
                <option value="Landslide">Landslide</option>
                <option value="Flash Flood">Flash Flood</option>
                <option value="Mudslide">Mudslide</option>
                <option value="Bridge Damage">Bridge Damage</option>
                <option value="Rockfall">Rockfall</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Severity Level</label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-red-400 font-bold focus:outline-none focus:border-red-500"
              >
                <option value="Critical">Critical (Road Blocked)</option>
                <option value="High">High (Single Lane)</option>
                <option value="Medium">Medium (Caution)</option>
                <option value="Low">Low (Informational)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Field Observations / Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., Heavy debris accumulation near milepost 34. Road blocked completely."
              rows={3}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-red-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Reporter Name / Agency</label>
            <input
              type="text"
              value={reporter}
              onChange={(e) => setReporter(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-red-500"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex items-center space-x-2 px-5 py-2 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-xs shadow-lg glow-red"
            >
              <Send className="h-3.5 w-3.5" />
              <span>SUBMIT INCIDENT REPORT</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
