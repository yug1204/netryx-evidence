import { FileText, Download, CheckCircle2, Printer } from 'lucide-react'

const reports = [
  { id: 'REP-2025-01', title: 'Executive Threat Brief — Case #1041 Ransomware', date: '2025-05-10', type: 'Executive Summary', status: 'Approved', format: 'PDF' },
  { id: 'REP-2025-02', title: 'Technical Forensics & IOC Dossier — Case #1042', date: '2025-05-09', type: 'Full Technical Report', status: 'Under Review', format: 'PDF / DOCX' },
  { id: 'REP-2025-03', title: 'Chain of Custody Legal Manifest — Vault Batch #89', date: '2025-05-08', type: 'NIST Compliance Audit', status: 'Signed & Certified', format: 'PDF' },
]

export default function ReportsPage() {
  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-6)', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 10 }}>
            <FileText size={28} style={{ color: 'var(--color-accent-yellow)' }} />
            Forensic Reports & Documentation
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 4, fontSize: 'var(--text-sm)' }}>
            NIST SP 800-86 compliant incident summaries, IOC dossiers, and executive threat briefs.
          </p>
        </div>

        <button
          onClick={() => alert('Generating fresh incident report... PDF will be ready in 15 seconds.')}
          style={{
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-cyan))',
            color: 'white',
            padding: '10px 18px',
            borderRadius: 'var(--radius-md)',
            fontWeight: 600,
            cursor: 'pointer',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}
        >
          <Printer size={16} /> Generate New Report
        </button>
      </div>

      <div className="card" style={{ overflowX: 'auto', border: '1px solid var(--color-border)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 'var(--text-sm)' }}>
          <thead>
            <tr style={{ background: 'var(--color-bg-tertiary)', borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', fontSize: 'var(--text-xs)', textTransform: 'uppercase' }}>
              <th style={{ padding: '12px 16px' }}>Report ID & Title</th>
              <th style={{ padding: '12px 16px' }}>Type</th>
              <th style={{ padding: '12px 16px' }}>Date</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'right' }}>Download</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '14px 16px' }}>
                  <div style={{ fontWeight: 600 }}>{r.title}</div>
                  <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)' }}>{r.id}</div>
                </td>
                <td style={{ padding: '14px 16px', color: 'var(--color-text-secondary)' }}>{r.type}</td>
                <td style={{ padding: '14px 16px', color: 'var(--color-text-secondary)' }}>{r.date}</td>
                <td style={{ padding: '14px 16px' }}>
                  <span style={{
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-accent-green)',
                    background: 'rgba(34, 197, 94, 0.1)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4
                  }}>
                    <CheckCircle2 size={12} /> {r.status}
                  </span>
                </td>
                <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                  <button
                    onClick={() => alert(`Downloading ${r.title} [${r.format}]...`)}
                    style={{
                      background: 'rgba(56, 132, 255, 0.15)',
                      border: '1px solid rgba(56, 132, 255, 0.3)',
                      color: 'var(--color-primary-light)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '4px 10px',
                      fontSize: 'var(--text-xs)',
                      cursor: 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4
                    }}
                  >
                    <Download size={12} /> {r.format}
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
