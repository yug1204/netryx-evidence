import { Clock, Terminal } from 'lucide-react'

const events = [
  { time: '2025-05-10 14:22:15 UTC', title: 'PowerShell Payload Execution', severity: 'critical', desc: 'Base64 encoded command spawned by cmd.exe downloading payload from 192.168.100.45', source: 'Sysmon Event ID 1' },
  { time: '2025-05-10 14:15:02 UTC', title: 'Suspicious DLL Injected into explorer.exe', severity: 'critical', desc: 'Process injection detected targeting PID 4812 using VirtualAllocEx', source: 'Memory Forensics' },
  { time: '2025-05-10 13:48:29 UTC', title: 'Credential Dumping Attempt', severity: 'high', desc: 'LSASS memory accessed by non-standard process handle', source: 'EDR Alert' },
  { time: '2025-05-10 12:30:11 UTC', title: 'Spear Phishing Attachment Opened', severity: 'high', desc: 'User opened wire_transfer_request.pdf containing embedded macro dropper', source: 'Outlook Log' },
  { time: '2025-05-10 12:28:44 UTC', title: 'Phishing Email Received', severity: 'medium', desc: 'Incoming email from external spoofed domain with failed SPF/DMARC checks', source: 'Exchange Gateway' },
]

export default function TimelinePage() {
  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 10 }}>
          <Clock size={28} style={{ color: 'var(--color-accent-green)' }} />
          Chronological Attack Timeline
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', marginTop: 4, fontSize: 'var(--text-sm)' }}>
          Unified multi-source forensic chronology mapping initial access to lateral movement.
        </p>
      </div>

      <div style={{ position: 'relative', paddingLeft: 28 }}>
        <div style={{ position: 'absolute', left: 8, top: 0, bottom: 0, width: 2, background: 'var(--color-border)' }} />
        {events.map((ev, i) => (
          <div key={i} style={{ marginBottom: 28, position: 'relative' }}>
            <div style={{
              position: 'absolute',
              left: -28,
              top: 4,
              width: 18,
              height: 18,
              borderRadius: '50%',
              background: ev.severity === 'critical' ? 'var(--color-risk-critical)' : 'var(--color-risk-medium)',
              border: '3px solid var(--color-bg-primary)',
              boxShadow: '0 0 10px rgba(239, 68, 68, 0.4)'
            }} />
            <div className="card" style={{ padding: 'var(--space-4)', border: '1px solid var(--color-border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-xs)', color: 'var(--color-accent-cyan)' }}>
                  {ev.time}
                </span>
                <span style={{
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '10px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  background: ev.severity === 'critical' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                  color: ev.severity === 'critical' ? 'var(--color-risk-critical)' : 'var(--color-risk-medium)'
                }}>
                  {ev.severity}
                </span>
              </div>
              <h3 style={{ fontSize: 'var(--text-md)', fontWeight: 700, marginBottom: 4 }}>{ev.title}</h3>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', marginBottom: 8 }}>{ev.desc}</p>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Terminal size={12} /> Source: {ev.source}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
