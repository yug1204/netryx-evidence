import { useState } from 'react'
import {
  Plus, Search, FolderOpen, AlertTriangle,
  ChevronRight, Clock, Shield,
} from 'lucide-react'

/* ── Mock Cases ────────────────────────────────────────────── */
const mockCases = [
  {
    id: 1042,
    title: 'Suspicious Phishing Campaign',
    priority: 'high',
    status: 'under_investigation',
    risk_score: 82,
    evidence_count: 27,
    ioc_count: 63,
    created_at: '2025-05-10',
    assigned_to: 'Investigator 01',
  },
  {
    id: 1041,
    title: 'Ransomware Incident — Finance Dept',
    priority: 'critical',
    status: 'open',
    risk_score: 95,
    evidence_count: 45,
    ioc_count: 112,
    created_at: '2025-05-08',
    assigned_to: 'Analyst 02',
  },
  {
    id: 1040,
    title: 'Data Exfiltration via DNS Tunneling',
    priority: 'high',
    status: 'pending_review',
    risk_score: 71,
    evidence_count: 18,
    ioc_count: 34,
    created_at: '2025-05-05',
    assigned_to: 'Investigator 01',
  },
  {
    id: 1039,
    title: 'Credential Stuffing Attack — Portal',
    priority: 'medium',
    status: 'closed',
    risk_score: 45,
    evidence_count: 12,
    ioc_count: 28,
    created_at: '2025-05-01',
    assigned_to: 'Analyst 03',
  },
  {
    id: 1038,
    title: 'Suspicious Insider Activity',
    priority: 'medium',
    status: 'under_investigation',
    risk_score: 58,
    evidence_count: 8,
    ioc_count: 15,
    created_at: '2025-04-28',
    assigned_to: 'Investigator 01',
  },
]

const statusLabels: Record<string, string> = {
  open: 'Open',
  under_investigation: 'Under Investigation',
  pending_review: 'Pending Review',
  closed: 'Closed',
}

const statusColors: Record<string, string> = {
  open: 'info',
  under_investigation: 'medium',
  pending_review: 'high',
  closed: 'low',
}

export default function CasesListPage() {
  const [search, setSearch] = useState('')

  const filtered = mockCases.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="animate-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Cases
          </h1>
          <p className="text-muted text-sm">{mockCases.length} investigations</p>
        </div>
        <button className="btn btn-primary" id="create-case-btn">
          <Plus size={16} /> New Case
        </button>
      </div>

      {/* Search & Filters */}
      <div className="card mb-6">
        <div className="flex items-center gap-4">
          <div className="header-search" style={{ flex: 1 }}>
            <Search size={16} style={{ color: 'var(--color-text-muted)' }} />
            <input
              type="text"
              placeholder="Search cases..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              id="case-search"
            />
          </div>
          <select className="input" style={{ width: 180 }} id="status-filter">
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="under_investigation">Under Investigation</option>
            <option value="pending_review">Pending Review</option>
            <option value="closed">Closed</option>
          </select>
          <select className="input" style={{ width: 150 }} id="priority-filter">
            <option value="">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Cases Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Case</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Risk</th>
              <th>Evidence</th>
              <th>IOCs</th>
              <th>Assigned</th>
              <th>Created</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => (
              <tr key={c.id} style={{ cursor: 'pointer' }}>
                <td>
                  <div className="flex items-center gap-3">
                    <div style={{
                      width: 36, height: 36, borderRadius: 'var(--radius-md)',
                      background: 'rgba(56, 132, 255, 0.1)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      <FolderOpen size={18} style={{ color: 'var(--color-primary)' }} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)' }}>
                        #{c.id}
                      </div>
                      <div style={{
                        fontSize: 'var(--text-sm)',
                        color: 'var(--color-text-primary)',
                        maxWidth: 280,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}>
                        {c.title}
                      </div>
                    </div>
                  </div>
                </td>
                <td>
                  <span className={`risk-badge ${c.priority}`}>
                    {c.priority === 'critical' && <AlertTriangle size={10} />}
                    {c.priority}
                  </span>
                </td>
                <td>
                  <span className={`risk-badge ${statusColors[c.status]}`}>
                    {statusLabels[c.status]}
                  </span>
                </td>
                <td>
                  <div className="flex items-center gap-2">
                    <div style={{
                      width: 40, height: 6, borderRadius: 'var(--radius-full)',
                      background: 'var(--color-bg-tertiary)',
                      overflow: 'hidden',
                    }}>
                      <div style={{
                        width: `${c.risk_score}%`,
                        height: '100%',
                        borderRadius: 'var(--radius-full)',
                        background: c.risk_score >= 70 ? 'var(--color-risk-high)' :
                          c.risk_score >= 40 ? 'var(--color-risk-medium)' : 'var(--color-risk-low)',
                        transition: 'width 0.5s ease',
                      }} />
                    </div>
                    <span className="text-mono text-sm" style={{
                      color: c.risk_score >= 70 ? 'var(--color-risk-high)' :
                        c.risk_score >= 40 ? 'var(--color-risk-medium)' : 'var(--color-risk-low)',
                      fontWeight: 600,
                    }}>
                      {c.risk_score}
                    </span>
                  </div>
                </td>
                <td>
                  <span className="flex items-center gap-1 text-sm">
                    <Shield size={12} style={{ color: 'var(--color-text-muted)' }} />
                    {c.evidence_count}
                  </span>
                </td>
                <td>
                  <span className="flex items-center gap-1 text-sm">
                    <Shield size={12} style={{ color: 'var(--color-risk-high)' }} />
                    {c.ioc_count}
                  </span>
                </td>
                <td className="text-sm text-muted">{c.assigned_to}</td>
                <td>
                  <span className="flex items-center gap-1 text-sm text-muted">
                    <Clock size={12} />
                    {c.created_at}
                  </span>
                </td>
                <td>
                  <button className="btn btn-secondary btn-sm">
                    <ChevronRight size={14} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
