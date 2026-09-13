import {
  FileSearch, Shield, Zap, Users, Clock,
  Image, FileText, Mail, Database,
  ArrowUpRight, Eye,
} from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

/* ── Mock Data (matches the UI blueprint) ──────────────────── */
const stats = [
  { label: 'Evidence', value: 27, icon: FileSearch, variant: 'evidence' as const },
  { label: 'IOCs', value: 63, icon: Shield, variant: 'ioc' as const },
  { label: 'Events', value: 128, icon: Zap, variant: 'events' as const },
  { label: 'Entities', value: 41, icon: Users, variant: 'entities' as const },
]

const recentEvidence = [
  { name: 'image_01.jpg', type: 'Image', size: '2.3 MB', icon: Image, color: 'var(--color-primary)' },
  { name: 'document.pdf', type: 'Document', size: '1.2 MB', icon: FileText, color: 'var(--color-accent-purple)' },
  { name: 'email_01.eml', type: 'Email', size: '480 KB', icon: Mail, color: 'var(--color-accent-yellow)' },
  { name: 'log.txt', type: 'Log', size: '3.1 MB', icon: Database, color: 'var(--color-accent-green)' },
  { name: 'suspiciousFile.txt', type: 'Text', size: '12 KB', icon: FileText, color: 'var(--color-accent-orange)' },
]

const riskData = [
  { name: 'High', value: 8, color: '#ef4444' },
  { name: 'Medium', value: 21, color: '#f59e0b' },
  { name: 'Low', value: 34, color: '#22c55e' },
]

const timelineEvents = [
  { time: '09:14', desc: 'Email received', type: 'email' },
  { time: '09:18', desc: 'URL accessed', type: 'url' },
  { time: '09:22', desc: 'File downloaded', type: 'file' },
  { time: '09:27', desc: 'Suspicious connection detected', type: 'connection' },
]

export default function DashboardPage() {
  const riskScore = 82

  return (
    <div className="animate-in">
      {/* Page Title */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Dashboard
          </h1>
          <p className="text-muted text-sm">
            Case #I042 — Suspicious Phishing Campaign
          </p>
        </div>
        <div className="flex gap-3">
          <span className="risk-badge high">Under Investigation</span>
          <span className="risk-badge critical">High Priority</span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
            Created: 2025-05-10
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        {stats.map((stat, i) => (
          <div className="stat-card" key={stat.label} style={{ animationDelay: `${i * 80}ms` }}>
            <div className={`stat-card-icon ${stat.variant}`}>
              <stat.icon size={22} />
            </div>
            <div className="stat-card-value">{stat.value}</div>
            <div className="stat-card-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Main Dashboard Grid */}
      <div className="dashboard-grid">
        {/* Left Column: Recent Evidence */}
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Recent Evidence</div>
              <div className="card-subtitle">{recentEvidence.length} files uploaded</div>
            </div>
            <button className="btn btn-secondary btn-sm">
              <Eye size={14} /> View All
            </button>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>File</th>
                <th>Type</th>
                <th>Size</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {recentEvidence.map((file) => (
                <tr key={file.name}>
                  <td>
                    <div className="flex items-center gap-3">
                      <div style={{
                        width: 32, height: 32, borderRadius: 'var(--radius-sm)',
                        background: `${file.color}15`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}>
                        <file.icon size={16} style={{ color: file.color }} />
                      </div>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-sm)' }}>
                        {file.name}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className="risk-badge info">{file.type}</span>
                  </td>
                  <td className="text-muted text-sm">{file.size}</td>
                  <td>
                    <button className="btn btn-secondary btn-sm">
                      <ArrowUpRight size={12} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Right Column: Risk + Timeline */}
        <div className="flex flex-col gap-6">
          {/* Risk Overview */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">Risk Overview</div>
            </div>

            <div className="flex items-center gap-4" style={{ justifyContent: 'center' }}>
              <div style={{ width: 150, height: 150, position: 'relative' }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={riskData}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={65}
                      paddingAngle={4}
                      dataKey="value"
                      strokeWidth={0}
                    >
                      {riskData.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: 'var(--color-bg-card)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--color-text-primary)',
                        fontSize: 'var(--text-sm)',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                {/* Center Score */}
                <div style={{
                  position: 'absolute', top: '50%', left: '50%',
                  transform: 'translate(-50%, -50%)',
                  textAlign: 'center',
                }}>
                  <div style={{
                    fontSize: 'var(--text-2xl)', fontWeight: 800,
                    color: riskScore >= 70 ? 'var(--color-risk-high)' : 'var(--color-risk-medium)',
                  }}>
                    {riskScore}
                  </div>
                  <div style={{ fontSize: '9px', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                    High Risk
                  </div>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                {riskData.map((item) => (
                  <div key={item.name} className="flex items-center gap-2">
                    <div style={{
                      width: 10, height: 10, borderRadius: '50%',
                      background: item.color,
                    }} />
                    <span className="text-sm" style={{ color: 'var(--color-text-secondary)', minWidth: 60 }}>
                      {item.name}
                    </span>
                    <span className="font-bold text-sm">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <Clock size={16} style={{ display: 'inline', marginRight: 8 }} />
                Timeline (Recent Events)
              </div>
              <button className="btn btn-secondary btn-sm">View Full Timeline</button>
            </div>

            <div className="timeline">
              {timelineEvents.map((event, i) => (
                <div className="timeline-event" key={i}>
                  <div className={`timeline-dot ${event.type}`}>
                    {event.type === 'email' && '📧'}
                    {event.type === 'url' && '🔗'}
                    {event.type === 'file' && '📄'}
                    {event.type === 'connection' && '⚡'}
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-time">{event.time}</div>
                    <div className="timeline-desc">{event.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
