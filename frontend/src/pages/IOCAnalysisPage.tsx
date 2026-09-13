import { useState } from 'react'
import { Shield, Search } from 'lucide-react'

const mockIOCs = [
  { id: 1, value: '192.168.100.45', type: 'ip', threat_level: 'critical', confidence: 95, source: 'Network Log', matches: 'Cobalt Strike C2' },
  { id: 2, value: 'evil-updates-cdn.com', type: 'domain', threat_level: 'high', confidence: 88, source: 'DNS Tunnel', matches: 'Domain Fronting' },
  { id: 3, value: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a', type: 'hash', threat_level: 'critical', confidence: 99, source: 'Memory Dump', matches: 'LockBit 3.0 Ransomware' },
  { id: 4, value: 'powershell.exe -enc JABzAD0ATg...', type: 'command', threat_level: 'high', confidence: 90, source: 'EVTX Log', matches: 'Base64 Encoded Download' },
  { id: 5, value: '185.220.101.5', type: 'ip', threat_level: 'medium', confidence: 75, source: 'VirusTotal', matches: 'Tor Exit Node' },
  { id: 6, value: 'finance-verification-portal.net', type: 'domain', threat_level: 'critical', confidence: 96, source: 'Phishing Email', matches: 'Credential Harvester' },
]

export default function IOCAnalysisPage() {
  const [filterType, setFilterType] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  const filtered = mockIOCs.filter((ioc) => {
    const matchesType = filterType === 'all' || ioc.type === filterType
    const matchesSearch = ioc.value.toLowerCase().includes(searchTerm.toLowerCase()) || ioc.matches.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesType && matchesSearch
  })

  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: 1400, margin: '0 auto' }}>
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 10 }}>
          <Shield size={28} style={{ color: 'var(--color-primary)' }} />
          IOC Extraction & Threat Intelligence
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', marginTop: 4, fontSize: 'var(--text-sm)' }}>
          Automated Indicator of Compromise extraction, VirusTotal / MISP correlation, and threat scoring.
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <div style={{ display: 'flex', gap: 8, background: 'var(--color-bg-tertiary)', padding: 4, borderRadius: 'var(--radius-md)' }}>
          {['all', 'ip', 'domain', 'hash', 'command'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              style={{
                padding: '6px 14px',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                background: filterType === t ? 'var(--color-primary)' : 'transparent',
                color: filterType === t ? 'white' : 'var(--color-text-secondary)',
                fontWeight: 600,
                fontSize: 'var(--text-xs)',
                cursor: 'pointer',
                textTransform: 'uppercase'
              }}
            >
              {t}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '6px 14px', minWidth: 260 }}>
          <Search size={16} style={{ color: 'var(--color-text-tertiary)' }} />
          <input
            type="text"
            placeholder="Search IOCs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ background: 'transparent', border: 'none', outline: 'none', color: 'white', fontSize: 'var(--text-sm)', width: '100%' }}
          />
        </div>
      </div>

      <div className="card" style={{ overflowX: 'auto', border: '1px solid var(--color-border)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 'var(--text-sm)' }}>
          <thead>
            <tr style={{ background: 'var(--color-bg-tertiary)', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)', textTransform: 'uppercase' }}>
              <th style={{ padding: '12px 16px' }}>IOC Indicator</th>
              <th style={{ padding: '12px 16px' }}>Type</th>
              <th style={{ padding: '12px 16px' }}>Severity</th>
              <th style={{ padding: '12px 16px' }}>Threat Match</th>
              <th style={{ padding: '12px 16px' }}>Source</th>
              <th style={{ padding: '12px 16px' }}>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((ioc) => (
              <tr key={ioc.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-accent-cyan)' }}>
                  {ioc.value}
                </td>
                <td style={{ padding: '14px 16px', textTransform: 'uppercase', fontSize: 'var(--text-xs)' }}>
                  {ioc.type}
                </td>
                <td style={{ padding: '14px 16px' }}>
                  <span style={{
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    background: ioc.threat_level === 'critical' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                    color: ioc.threat_level === 'critical' ? 'var(--color-risk-critical)' : 'var(--color-risk-medium)'
                  }}>
                    {ioc.threat_level}
                  </span>
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--color-text-primary)', fontWeight: 500 }}>
                  {ioc.matches}
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--color-text-secondary)' }}>
                  {ioc.source}
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--color-accent-green)', fontWeight: 700 }}>
                  {ioc.confidence}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
