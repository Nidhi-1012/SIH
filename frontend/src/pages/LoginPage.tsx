import React from 'react';

type Role = 'user' | 'driver' | 'officer';

const roleConfig: Record<Role, { emoji: string; title: string; subtitle: string; color: string; bg: string; desc: string }> = {
  user: {
    emoji: '👤',
    title: 'User Login',
    subtitle: 'General Public',
    color: '#0071e3',
    bg: 'rgba(0,113,227,0.08)',
    desc: 'Access safe route planning, live alerts, and hazard maps for your journey.',
  },
  driver: {
    emoji: '🚚',
    title: 'Driver Login',
    subtitle: 'Transport Operators',
    color: '#34c759',
    bg: 'rgba(52,199,89,0.08)',
    desc: 'Access logistics tracking, delivery routes, and critical road condition updates.',
  },
  officer: {
    emoji: '👮',
    title: 'Officer Login',
    subtitle: 'Highway Officials',
    color: '#ff9f0a',
    bg: 'rgba(255,159,10,0.08)',
    desc: 'Access the admin dashboard, incident approval, and field monitoring tools.',
  },
};

interface LoginPageProps {
  role: Role;
}

const LoginPage: React.FC<LoginPageProps> = ({ role }) => {
  const cfg = roleConfig[role];

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
      {/* Back */}
      <button onClick={() => window.location.href = '/'} style={{
        position: 'fixed', top: 16, left: 16, background: '#fff',
        border: 'none', padding: '10px 16px', borderRadius: 12,
        cursor: 'pointer', fontSize: 14, fontWeight: 600, color: '#1d1d1f',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)', display: 'flex', alignItems: 'center', gap: 6,
      }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        Back
      </button>

      {/* Icon */}
      <div style={{
        width: 72, height: 72, borderRadius: 20, background: cfg.bg,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 36, marginBottom: 16, border: `1.5px solid ${cfg.color}22`,
      }}>
        {cfg.emoji}
      </div>

      <h1 style={{ fontSize: 26, fontWeight: 800, color: '#1d1d1f', margin: '0 0 4px', letterSpacing: '-0.4px' }}>
        {cfg.title}
      </h1>
      <p style={{ fontSize: 13, color: '#86868b', margin: '0 0 6px', fontWeight: 500 }}>{cfg.subtitle}</p>
      <p style={{ fontSize: 13.5, color: '#444', textAlign: 'center', maxWidth: 300, lineHeight: 1.5, margin: '0 0 32px' }}>
        {cfg.desc}
      </p>

      {/* Login Form (placeholder — auth not implemented yet) */}
      <div style={{
        width: '100%', maxWidth: 380, background: '#fff',
        borderRadius: 18, padding: '28px 24px',
        boxShadow: '0 4px 24px rgba(0,0,0,0.07)',
        border: '1px solid rgba(0,0,0,0.06)',
      }}>
        <div style={{ marginBottom: 16 }}>
          <label style={{ fontSize: 12, fontWeight: 600, color: '#86868b', display: 'block', marginBottom: 6 }}>
            EMAIL / PHONE NUMBER
          </label>
          <input
            type="text"
            placeholder="Enter your email or phone"
            style={{
              width: '100%', padding: '13px 14px', fontSize: 15,
              border: '1.5px solid rgba(0,0,0,0.1)', borderRadius: 10,
              background: '#f5f5f7', color: '#1d1d1f', outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>
        <div style={{ marginBottom: 24 }}>
          <label style={{ fontSize: 12, fontWeight: 600, color: '#86868b', display: 'block', marginBottom: 6 }}>
            PASSWORD
          </label>
          <input
            type="password"
            placeholder="Enter your password"
            style={{
              width: '100%', padding: '13px 14px', fontSize: 15,
              border: '1.5px solid rgba(0,0,0,0.1)', borderRadius: 10,
              background: '#f5f5f7', color: '#1d1d1f', outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>

        <button
          onClick={() => window.location.href = '/app'}
          style={{
            width: '100%', padding: '15px', fontSize: 16, fontWeight: 700,
            background: cfg.color, color: '#fff', border: 'none',
            borderRadius: 12, cursor: 'pointer',
            boxShadow: `0 4px 16px ${cfg.color}44`,
          }}
        >
          Continue as {cfg.subtitle.split(' ')[0]}
        </button>

        <p style={{ textAlign: 'center', fontSize: 11.5, color: '#98989d', marginTop: 16 }}>
          Authentication will be enabled in the next step.
        </p>
      </div>

      <p style={{ marginTop: 28, fontSize: 11.5, color: '#98989d', textAlign: 'center' }}>
        NER SafeRoute · Government of India · SIH26002
      </p>
    </div>
  );
};

export default LoginPage;
