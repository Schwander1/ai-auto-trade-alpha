'use client';

import { useEffect, useState } from 'react';

export default function DashboardPage() {
  const [signals, setSignals] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://91.98.153.49:8001';
        const [signalsRes, statsRes] = await Promise.all([
          fetch(`${apiUrl}/api/signals?premium_only=true&limit=5`),
          fetch(`${apiUrl}/api/stats`)
        ]);
        const signalsData = await signalsRes.json();
        const statsData = await statsRes.json();
        setSignals(signalsData);
        setStats(statsData);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{minHeight: '100vh', background: '#111827', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{fontSize: '24px'}}>Loading signals...</div>
      </div>
    );
  }

  return (
    <div style={{minHeight: '100vh', background: 'linear-gradient(to bottom right, #111827, #000)', color: 'white'}}>
      <nav style={{padding: '24px', borderBottom: '1px solid #374151'}}>
        <div style={{maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <h1 style={{fontSize: '24px', fontWeight: 'bold'}}>🏔️ Alpine Analytics</h1>
          <a href="/" style={{color: '#9ca3af', textDecoration: 'none'}}>← Home</a>
        </div>
      </nav>
      
      <main style={{maxWidth: '1400px', margin: '0 auto', padding: '32px 24px'}}>
        <h2 style={{fontSize: '36px', fontWeight: 'bold', marginBottom: '32px'}}>Premium Signals Dashboard</h2>
        
        {stats && (
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginBottom: '32px'}}>
            <div style={{background: 'rgba(34, 197, 94, 0.2)', border: '1px solid #16a34a', borderRadius: '8px', padding: '24px'}}>
              <div style={{fontSize: '36px', fontWeight: 'bold'}}>{stats.win_rate}%</div>
              <div style={{fontSize: '14px', color: '#d1d5db'}}>Win Rate</div>
            </div>
            <div style={{background: 'rgba(59, 130, 246, 0.2)', border: '1px solid #2563eb', borderRadius: '8px', padding: '24px'}}>
              <div style={{fontSize: '36px', fontWeight: 'bold'}}>{stats.total_signals}</div>
              <div style={{fontSize: '14px', color: '#d1d5db'}}>Total Signals</div>
            </div>
            <div style={{background: 'rgba(168, 85, 247, 0.2)', border: '1px solid #9333ea', borderRadius: '8px', padding: '24px'}}>
              <div style={{fontSize: '36px', fontWeight: 'bold'}}>{stats.premium_count}</div>
              <div style={{fontSize: '14px', color: '#d1d5db'}}>Premium</div>
            </div>
            <div style={{background: 'rgba(249, 115, 22, 0.2)', border: '1px solid #ea580c', borderRadius: '8px', padding: '24px'}}>
              <div style={{fontSize: '36px', fontWeight: 'bold'}}>{stats.avg_confidence}%</div>
              <div style={{fontSize: '14px', color: '#d1d5db'}}>Avg Confidence</div>
            </div>
          </div>
        )}
        
        <div style={{display: 'flex', flexDirection: 'column', gap: '16px'}}>
          {signals.map((signal: any) => (
            <div key={signal.id} style={{background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '24px'}}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
                <div>
                  <span style={{fontSize: '24px', fontWeight: 'bold'}}>{signal.symbol}</span>
                  <span style={{marginLeft: '16px', padding: '4px 12px', borderRadius: '4px', background: signal.action === 'BUY' ? '#16a34a' : '#dc2626', fontSize: '14px', fontWeight: 'bold'}}>
                    {signal.action}
                  </span>
                  <span style={{marginLeft: '8px', padding: '4px 12px', borderRadius: '4px', background: '#9333ea', fontSize: '14px'}}>
                    {signal.type}
                  </span>
                </div>
                <div style={{textAlign: 'right'}}>
                  <div style={{fontSize: '36px', fontWeight: 'bold', color: '#4ade80'}}>{signal.confidence}%</div>
                  <div style={{fontSize: '12px', color: '#9ca3af'}}>Confidence</div>
                </div>
              </div>
              
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', fontSize: '14px'}}>
                <div>
                  <div style={{color: '#9ca3af'}}>Entry</div>
                  <div style={{fontSize: '20px', fontWeight: 'bold'}}>${signal.entry.toLocaleString()}</div>
                </div>
                <div>
                  <div style={{color: '#9ca3af'}}>Stop Loss</div>
                  <div style={{fontSize: '20px', fontWeight: 'bold', color: '#ef4444'}}>${signal.stop_loss.toLocaleString()}</div>
                </div>
                <div>
                  <div style={{color: '#9ca3af'}}>Take Profit</div>
                  <div style={{fontSize: '20px', fontWeight: 'bold', color: '#22c55e'}}>${signal.take_profit.toLocaleString()}</div>
                </div>
              </div>
              
              <div style={{marginTop: '16px', fontSize: '12px', color: '#6b7280'}}>
                {signal.timestamp} • ID: {signal.id}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
