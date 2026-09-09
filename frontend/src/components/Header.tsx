import React from 'react';
import { ShieldAlert, Activity, Navigation, Radio, Bell } from 'lucide-react';

interface HeaderProps {
  emergencyMode: boolean;
  onToggleEmergency: () => void;
  unreadAlertCount: number;
}

export const Header: React.FC<HeaderProps> = ({ emergencyMode, onToggleEmergency, unreadAlertCount }) => {
  return (
    <header className="glass-panel px-6 py-3.5 flex flex-col md:flex-row items-center justify-between gap-4 border-b border-slate-800 shadow-xl sticky top-0 z-40">
      <div className="flex items-center space-x-3.5">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-950">
          <Navigation className="h-5 w-5 text-slate-950 font-bold" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="font-display font-extrabold text-xl tracking-tight text-white">
              NER-LINK <span className="text-emerald-400">AI</span>
            </h1>
            <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800">
              SIH26002
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium">
            Smart Logistics & Accessibility Intelligence Platform — North East Region
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Realtime Engine Status */}
        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-slate-300 font-medium">AI Risk Engine Active</span>
        </div>

        {/* Emergency Mode Toggle Button */}
        <button
          onClick={onToggleEmergency}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all duration-300 shadow-lg ${
            emergencyMode 
              ? 'bg-gradient-to-r from-red-600 to-rose-600 text-white glow-red animate-pulse'
              : 'bg-slate-900 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-500'
          }`}
        >
          <ShieldAlert className="h-4 w-4" />
          <span>{emergencyMode ? 'EMERGENCY MODE ACTIVE (P0)' : 'ENABLE EMERGENCY MODE'}</span>
        </button>

        {/* Notification Bell Badge */}
        <div className="relative">
          <button className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition">
            <Bell className="h-4 w-4" />
            {unreadAlertCount > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white rounded-full text-[10px] font-extrabold flex items-center justify-center animate-bounce">
                {unreadAlertCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};
