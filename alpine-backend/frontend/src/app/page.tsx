export default function HomePage() {
  return (
    <div style={{minHeight: '100vh', background: 'linear-gradient(to bottom right, #1e3a8a, #000)', color: 'white'}}>
      <nav style={{padding: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)'}}>
        <div style={{maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <h1 style={{fontSize: '24px', fontWeight: 'bold'}}>🏔️ Alpine Analytics</h1>
          <a href="/dashboard" style={{background: '#16a34a', padding: '12px 24px', borderRadius: '8px', color: 'white', textDecoration: 'none', fontWeight: 'bold'}}>
            Dashboard →
          </a>
        </div>
      </nav>
      
      <main style={{maxWidth: '1200px', margin: '0 auto', padding: '80px 24px', textAlign: 'center'}}>
        <div style={{marginBottom: '32px'}}>
          <span style={{background: 'rgba(34, 197, 94, 0.2)', color: '#4ade80', padding: '8px 16px', borderRadius: '24px', fontSize: '14px', fontWeight: 'bold', border: '1px solid #16a34a'}}>
            🔥 50% OFF PRE-LAUNCH
          </span>
        </div>
        
        <h2 style={{fontSize: '72px', fontWeight: '900', marginBottom: '24px', lineHeight: '1.1'}}>
          95%+ Win Rate<br />
          <span style={{background: 'linear-gradient(to right, #4ade80, #60a5fa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
            Trading Signals
          </span>
        </h2>
        
        <p style={{fontSize: '24px', marginBottom: '48px', color: '#d1d5db', maxWidth: '900px', margin: '0 auto 48px'}}>
          Complete transparency. SHA-256 verified. Built to help small traders succeed.
        </p>
        
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '32px', marginTop: '64px', maxWidth: '1000px', margin: '64px auto 0'}}>
          <div style={{background: 'rgba(255,255,255,0.05)', padding: '32px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <div style={{fontSize: '48px', marginBottom: '16px'}}>✅</div>
            <h3 style={{fontSize: '36px', fontWeight: 'bold', color: '#4ade80', marginBottom: '8px'}}>95%+</h3>
            <p style={{fontSize: '18px', color: '#d1d5db'}}>Win Rate</p>
            <p style={{fontSize: '14px', color: '#9ca3af', marginTop: '8px'}}>Crush the market with premium signals</p>
          </div>
          
          <div style={{background: 'rgba(255,255,255,0.05)', padding: '32px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <div style={{fontSize: '48px', marginBottom: '16px'}}>🔐</div>
            <h3 style={{fontSize: '36px', fontWeight: 'bold', color: '#60a5fa', marginBottom: '8px'}}>SHA-256</h3>
            <p style={{fontSize: '18px', color: '#d1d5db'}}>Verified</p>
            <p style={{fontSize: '14px', color: '#9ca3af', marginTop: '8px'}}>Cryptographic proof of every signal</p>
          </div>
          
          <div style={{background: 'rgba(255,255,255,0.05)', padding: '32px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.1)'}}>
            <div style={{fontSize: '48px', marginBottom: '16px'}}>💎</div>
            <h3 style={{fontSize: '36px', fontWeight: 'bold', color: '#a78bfa', marginBottom: '8px'}}>$0</h3>
            <p style={{fontSize: '18px', color: '#d1d5db'}}>Minimum</p>
            <p style={{fontSize: '14px', color: '#9ca3af', marginTop: '8px'}}>Help small traders succeed</p>
          </div>
        </div>
        
        <div style={{marginTop: '64px'}}>
          <a 
            href="/dashboard" 
            style={{display: 'inline-block', background: 'linear-gradient(to right, #16a34a, #2563eb)', color: 'white', padding: '20px 48px', borderRadius: '12px', fontSize: '24px', fontWeight: 'bold', textDecoration: 'none', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'}}
          >
            Start Free Trial →
          </a>
          <p style={{fontSize: '14px', color: '#9ca3af', marginTop: '16px'}}>No credit card required</p>
        </div>
      </main>
      
      <footer style={{borderTop: '1px solid rgba(255,255,255,0.1)', marginTop: '80px', padding: '32px'}}>
        <div style={{maxWidth: '1200px', margin: '0 auto', textAlign: 'center', color: '#9ca3af'}}>
          <p style={{fontSize: '14px'}}>© 2025 Alpine Analytics. Private & Confidential.</p>
          <p style={{fontSize: '12px', marginTop: '8px'}}>Not financial advice. Trading involves risk.</p>
        </div>
      </footer>
    </div>
  );
}
