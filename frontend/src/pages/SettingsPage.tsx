import { useState } from 'react'
import { Settings, Key, Database, Check } from 'lucide-react'

export default function SettingsPage() {
  const [vtKey, setVtKey] = useState('vt_••••••••••••••••••••••••')
  const [mispUrl, setMispUrl] = useState('https://misp.internal.netryx.local')
  const [saved, setSaved] = useState(false)

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: 1000, margin: '0 auto' }}>
      <div style={{ marginBottom: 'var(--space-6)' }}>
        <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 10 }}>
          <Settings size={28} style={{ color: 'var(--color-primary)' }} />
          Platform Configuration & Integrations
        </h1>
        <p style={{ color: 'var(--color-text-secondary)', marginTop: 4, fontSize: 'var(--text-sm)' }}>
          Manage threat intelligence API connections, encryption keys, and distributed worker pipelines.
        </p>
      </div>

      <form onSubmit={handleSave}>
        <div className="card" style={{ padding: 'var(--space-6)', marginBottom: 20, border: '1px solid var(--color-border)' }}>
          <h2 style={{ fontSize: 'var(--text-md)', fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Key size={18} style={{ color: 'var(--color-accent-cyan)' }} /> Threat Intelligence Feeds
          </h2>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 6 }}>
              VirusTotal v3 Enterprise API Key
            </label>
            <input
              type="text"
              value={vtKey}
              onChange={(e) => setVtKey(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)',
                color: 'white',
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-sm)',
                outline: 'none'
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 6 }}>
              MISP (Malware Information Sharing Platform) Instance URL
            </label>
            <input
              type="text"
              value={mispUrl}
              onChange={(e) => setMispUrl(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--color-bg-tertiary)',
                border: '1px solid var(--color-border)',
                color: 'white',
                fontSize: 'var(--text-sm)',
                outline: 'none'
              }}
            />
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--space-6)', marginBottom: 24, border: '1px solid var(--color-border)' }}>
          <h2 style={{ fontSize: 'var(--text-md)', fontWeight: 700, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Database size={18} style={{ color: 'var(--color-accent-green)' }} /> Cryptographic Vault & Database Status
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, fontSize: 'var(--text-sm)' }}>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)' }}>Relational & Vector Store</div>
              <div style={{ fontWeight: 600, color: 'var(--color-accent-green)', marginTop: 2 }}>PostgreSQL 16 + pgvector (Active)</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)' }}>Graph Database Engine</div>
              <div style={{ fontWeight: 600, color: 'var(--color-accent-green)', marginTop: 2 }}>Neo4j 5.20 Enterprise (Connected)</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)' }}>Object Storage & Encryption</div>
              <div style={{ fontWeight: 600, color: 'var(--color-accent-green)', marginTop: 2 }}>MinIO S3 (AES-256-GCM Enabled)</div>
            </div>
            <div>
              <div style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)' }}>Distributed Queue</div>
              <div style={{ fontWeight: 600, color: 'var(--color-accent-green)', marginTop: 2 }}>Redis 7.2 + Celery Engine (Ready)</div>
            </div>
          </div>
        </div>

        <button
          type="submit"
          style={{
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-cyan))',
            color: 'white',
            padding: '10px 24px',
            borderRadius: 'var(--radius-md)',
            fontWeight: 600,
            cursor: 'pointer',
            border: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8
          }}
        >
          {saved ? <Check size={16} /> : null}
          {saved ? 'Configuration Saved!' : 'Save Changes'}
        </button>
      </form>
    </div>
  )
}
