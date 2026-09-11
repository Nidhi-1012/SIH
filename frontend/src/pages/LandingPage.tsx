import React from 'react';

const LandingPage: React.FC = () => {
  const handleRole = (role: string) => {
    window.location.href = `/login/${role}`;
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#f5f5f7',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif',
      padding: '24px 20px',
    }}>
      {/* Logo & Brand */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{
          width: 64, height: 64, borderRadius: 18,
          background: '#0071e3', margin: '0 auto 16px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 20px rgba(0,113,227,0.3)',
        }}>
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: '#1d1d1f', margin: 0, letterSpacing: '-0.5px' }}>
          NER SafeRoute
        </h1>
        <p style={{ fontSize: 13, color: '#6e6e73', margin: '6px 0 0', fontWeight: 500 }}>
          Smart Logistics & Accessibility Intelligence Platform
        </p>
        <p style={{
          fontSize: 14, color: '#0071e3', margin: '12px 0 0',
          fontStyle: 'italic', fontWeight: 500,
          background: 'rgba(0,113,227,0.07)',
          padding: '8px 16px', borderRadius: 20, display: 'inline-block'
        }}>
          "Safer routes. Smarter logistics. Better connectivity for NER."
        </p>
      </div>

      {/* Role Cards */}
      <div style={{ width: '100%', maxWidth: 380, display: 'flex', flexDirection: 'column', gap: 14 }}>
        
        {/* User */}
        <button onClick={() => handleRole('user')} style={{
          width: '100%', padding: '20px 22px',
          background: '#ffffff', border: '1.5px solid rgba(0,0,0,0.08)',
          borderRadius: 16, cursor: 'pointer', textAlign: 'left',
          display: 'flex', alignItems: 'center', gap: 16,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          transition: 'all 0.15s',
        }}
          onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,113,227,0.15)')}
          onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)')}
        >
          <div style={{
            width: 52, height: 52, borderRadius: 14, flexShrink: 0,
            background: 'rgba(0,113,227,0.1)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', fontSize: 26
          }}>👤</div>
          <div>
            <div style={{ fontSize: 17, fontWeight: 700, color: '#1d1d1f', marginBottom: 3 }}>Login as User</div>
            <div style={{ fontSize: 12.5, color: '#86868b', lineHeight: 1.4 }}>Village residents & general public</div>
          </div>
          <svg style={{ marginLeft: 'auto', flexShrink: 0 }} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0071e3" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </button>

        {/* Driver */}
        <button onClick={() => handleRole('driver')} style={{
          width: '100%', padding: '20px 22px',
          background: '#ffffff', border: '1.5px solid rgba(0,0,0,0.08)',
          borderRadius: 16, cursor: 'pointer', textAlign: 'left',
          display: 'flex', alignItems: 'center', gap: 16,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          transition: 'all 0.15s',
        }}
          onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 4px 20px rgba(52,199,89,0.2)')}
          onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)')}
        >
          <div style={{
            width: 52, height: 52, borderRadius: 14, flexShrink: 0,
            background: 'rgba(52,199,89,0.1)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', fontSize: 26
          }}>🚚</div>
          <div>
            <div style={{ fontSize: 17, fontWeight: 700, color: '#1d1d1f', marginBottom: 3 }}>Login as Driver</div>
            <div style={{ fontSize: 12.5, color: '#86868b', lineHeight: 1.4 }}>Truck drivers & transport operators</div>
          </div>
          <svg style={{ marginLeft: 'auto', flexShrink: 0 }} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34c759" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </button>

        {/* Officer */}
        <button onClick={() => handleRole('officer')} style={{
          width: '100%', padding: '20px 22px',
          background: '#ffffff', border: '1.5px solid rgba(0,0,0,0.08)',
          borderRadius: 16, cursor: 'pointer', textAlign: 'left',
          display: 'flex', alignItems: 'center', gap: 16,
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          transition: 'all 0.15s',
        }}
          onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 4px 20px rgba(255,159,10,0.2)')}
          onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)')}
        >
          <div style={{
            width: 52, height: 52, borderRadius: 14, flexShrink: 0,
            background: 'rgba(255,159,10,0.1)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', fontSize: 26
          }}>👮</div>
          <div>
            <div style={{ fontSize: 17, fontWeight: 700, color: '#1d1d1f', marginBottom: 3 }}>Login as Officer</div>
            <div style={{ fontSize: 12.5, color: '#86868b', lineHeight: 1.4 }}>Highway officials & field officers</div>
          </div>
          <svg style={{ marginLeft: 'auto', flexShrink: 0 }} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff9f0a" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </button>
      </div>

      {/* Footer */}
      <p style={{ marginTop: 40, fontSize: 11.5, color: '#98989d', textAlign: 'center', lineHeight: 1.6 }}>
        Government of India · Smart Logistics Initiative<br/>
        North Eastern Region · SIH26002
      </p>
    </div>
  );
};

export default LandingPage;
