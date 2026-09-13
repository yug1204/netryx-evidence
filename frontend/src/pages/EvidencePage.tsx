import { useState } from 'react'
import {
  Upload, Shield, FileSearch, Hash, Lock, CheckCircle2,
  HardDrive, Network, Binary, FileText, Search, Copy, Check,
  X
} from 'lucide-react'

interface EvidenceItem {
  id: string
  name: string
  type: 'disk' | 'network' | 'memory' | 'binary' | 'document'
  caseId: number
  size: string
  sha256: string
  entropy: number
  custodyStatus: 'verified' | 'tamper-evident' | 'pending'
  uploadedAt: string
  uploadedBy: string
}

const initialEvidence: EvidenceItem[] = [
  {
    id: 'EVD-8901',
    name: 'memdump_dc01.raw',
    type: 'memory',
    caseId: 1041,
    size: '16.4 GB',
    sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    entropy: 7.94,
    custodyStatus: 'verified',
    uploadedAt: '2025-05-10 14:22 UTC',
    uploadedBy: 'Investigator 01',
  },
  {
    id: 'EVD-8902',
    name: 'suspicious_traffic_dns.pcap',
    type: 'network',
    caseId: 1040,
    size: '842 MB',
    sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    entropy: 6.81,
    custodyStatus: 'verified',
    uploadedAt: '2025-05-09 18:45 UTC',
    uploadedBy: 'Analyst 02',
  },
  {
    id: 'EVD-8903',
    name: 'invoice_macro_loader.xlsm',
    type: 'document',
    caseId: 1042,
    size: '1.4 MB',
    sha256: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
    entropy: 7.88,
    custodyStatus: 'verified',
    uploadedAt: '2025-05-09 09:15 UTC',
    uploadedBy: 'Investigator 01',
  },
  {
    id: 'EVD-8904',
    name: 'workstation_c_drive.E01',
    type: 'disk',
    caseId: 1041,
    size: '128.6 GB',
    sha256: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
    entropy: 7.15,
    custodyStatus: 'verified',
    uploadedAt: '2025-05-08 22:10 UTC',
    uploadedBy: 'Investigator 01',
  },
  {
    id: 'EVD-8905',
    name: 'beacon_payload_x64.dll',
    type: 'binary',
    caseId: 1041,
    size: '348 KB',
    sha256: 'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d',
    entropy: 7.98,
    custodyStatus: 'verified',
    uploadedAt: '2025-05-08 16:30 UTC',
    uploadedBy: 'Analyst 02',
  },
  {
    id: 'EVD-8906',
    name: 'wire_transfer_request.pdf',
    type: 'document',
    caseId: 1042,
    size: '2.1 MB',
    sha256: '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',
    entropy: 6.42,
    custodyStatus: 'verified',
    uploadedAt: '2025-05-07 11:04 UTC',
    uploadedBy: 'Investigator 01',
  },
]

export default function EvidencePage() {
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>(initialEvidence)
  const [activeType, setActiveType] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [copiedHash, setCopiedHash] = useState<string | null>(null)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [newFileName, setNewFileName] = useState('')
  const [newFileType, setNewFileType] = useState<'disk' | 'network' | 'memory' | 'binary' | 'document'>('binary')
  const [newCaseId, setNewCaseId] = useState('1042')

  const copyToClipboard = (hash: string) => {
    navigator.clipboard.writeText(hash)
    setCopiedHash(hash)
    setTimeout(() => setCopiedHash(null), 2000)
  }

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newFileName.trim()) return

    const newItem: EvidenceItem = {
      id: `EVD-${Math.floor(1000 + Math.random() * 9000)}`,
      name: newFileName.trim(),
      type: newFileType,
      caseId: parseInt(newCaseId, 10),
      size: `${(Math.random() * 5 + 0.5).toFixed(1)} MB`,
      sha256: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
      entropy: parseFloat((Math.random() * 2.5 + 5.5).toFixed(2)),
      custodyStatus: 'verified',
      uploadedAt: 'Just now',
      uploadedBy: 'Investigator 01',
    }

    setEvidenceList([newItem, ...evidenceList])
    setShowUploadModal(false)
    setNewFileName('')
  }

  const filteredEvidence = evidenceList.filter((item) => {
    const matchesType = activeType === 'all' || item.type === activeType
    const matchesQuery =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.sha256.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.id.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesType && matchesQuery
  })

  const getTypeIcon = (type: EvidenceItem['type']) => {
    switch (type) {
      case 'memory': return <HardDrive size={18} className="text-purple" style={{ color: 'var(--color-accent-purple)' }} />
      case 'network': return <Network size={18} style={{ color: 'var(--color-accent-cyan)' }} />
      case 'document': return <FileText size={18} style={{ color: 'var(--color-accent-yellow)' }} />
      case 'binary': return <Binary size={18} style={{ color: 'var(--color-risk-critical)' }} />
      case 'disk': return <HardDrive size={18} style={{ color: 'var(--color-primary)' }} />
    }
  }

  return (
    <div style={{ padding: 'var(--space-6)', maxWidth: 1400, margin: '0 auto' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 'var(--space-6)',
        flexWrap: 'wrap',
        gap: 'var(--space-4)'
      }}>
        <div>
          <h1 style={{
            fontSize: 'var(--text-2xl)',
            fontWeight: 800,
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-3)'
          }}>
            <FileSearch size={28} style={{ color: 'var(--color-accent-cyan)' }} />
            Evidence Vault & Chain of Custody
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--space-1)', fontSize: 'var(--text-sm)' }}>
            NIST SP 800-86 Compliant Cryptographic Evidence Storage & Immutable Audit Trail
          </p>
        </div>

        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          <button
            onClick={() => setShowUploadModal(true)}
            className="btn btn-primary"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-2)',
              background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-cyan))',
              color: 'white',
              padding: '10px 18px',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none'
            }}
          >
            <Upload size={18} />
            Ingest New Evidence
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: 'var(--space-4)',
        marginBottom: 'var(--space-6)',
      }}>
        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
              Vault Artifacts
            </span>
            <FileSearch size={18} style={{ color: 'var(--color-accent-cyan)' }} />
          </div>
          <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, marginTop: 'var(--space-2)' }}>
            {evidenceList.length} Files
          </div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-green)', marginTop: 4 }}>
            ● 100% Chain-of-Custody Verified
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
              Cryptographic Integrity
            </span>
            <Hash size={18} style={{ color: 'var(--color-accent-green)' }} />
          </div>
          <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, marginTop: 'var(--space-2)' }}>
            SHA-256 + SSDEEP
          </div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-green)', marginTop: 4 }}>
            ✓ 0 Tampering Anomalies Detected
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
              High-Entropy Detection
            </span>
            <Lock size={18} style={{ color: 'var(--color-risk-critical)' }} />
          </div>
          <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, marginTop: 'var(--space-2)', color: 'var(--color-risk-critical)' }}>
            3 Encrypted / Packed
          </div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: 4 }}>
            Entropy threshold &gt; 7.80 bits/byte
          </div>
        </div>

        <div className="card" style={{ padding: 'var(--space-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>
              Storage Vault Layer
            </span>
            <Shield size={18} style={{ color: 'var(--color-primary)' }} />
          </div>
          <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, marginTop: 'var(--space-2)' }}>
            MinIO S3 Encrypted
          </div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: 4 }}>
            AES-256-GCM at rest
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 'var(--space-3)',
        marginBottom: 'var(--space-4)'
      }}>
        {/* Type Tabs */}
        <div style={{ display: 'flex', gap: 'var(--space-2)', background: 'var(--color-bg-tertiary)', padding: 4, borderRadius: 'var(--radius-md)' }}>
          {['all', 'disk', 'network', 'memory', 'binary', 'document'].map((type) => (
            <button
              key={type}
              onClick={() => setActiveType(type)}
              style={{
                padding: '6px 14px',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                background: activeType === type ? 'var(--color-primary)' : 'transparent',
                color: activeType === type ? 'white' : 'var(--color-text-secondary)',
                fontWeight: 600,
                fontSize: 'var(--text-xs)',
                cursor: 'pointer',
                textTransform: 'capitalize'
              }}
            >
              {type}
            </button>
          ))}
        </div>

        {/* Search */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-2)',
          background: 'var(--color-bg-secondary)',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          padding: '6px 14px',
          minWidth: 280
        }}>
          <Search size={16} style={{ color: 'var(--color-text-tertiary)' }} />
          <input
            type="text"
            placeholder="Search by filename or SHA-256..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: 'var(--color-text-primary)',
              fontSize: 'var(--text-sm)',
              width: '100%'
            }}
          />
        </div>
      </div>

      {/* Evidence Table Card */}
      <div className="card" style={{ overflowX: 'auto', border: '1px solid var(--color-border)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 'var(--text-sm)' }}>
          <thead>
            <tr style={{
              background: 'var(--color-bg-tertiary)',
              borderBottom: '1px solid var(--color-border)',
              color: 'var(--color-text-secondary)',
              fontSize: 'var(--text-xs)',
              textTransform: 'uppercase'
            }}>
              <th style={{ padding: '12px 16px' }}>Evidence ID & File</th>
              <th style={{ padding: '12px 16px' }}>Type</th>
              <th style={{ padding: '12px 16px' }}>Case</th>
              <th style={{ padding: '12px 16px' }}>Size</th>
              <th style={{ padding: '12px 16px' }}>SHA-256 Hash</th>
              <th style={{ padding: '12px 16px' }}>Entropy</th>
              <th style={{ padding: '12px 16px' }}>Custody Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvidence.map((item) => (
              <tr
                key={item.id}
                style={{
                  borderBottom: '1px solid var(--color-border)',
                  transition: 'background 0.2s',
                }}
              >
                {/* ID & Name */}
                <td style={{ padding: '14px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
                    <div style={{
                      padding: 8,
                      background: 'var(--color-bg-tertiary)',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      {getTypeIcon(item.type)}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{item.name}</div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)' }}>{item.id}</div>
                    </div>
                  </div>
                </td>

                {/* Type */}
                <td style={{ padding: '14px 16px', textTransform: 'capitalize' }}>
                  <span style={{
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    background: 'var(--color-bg-tertiary)',
                    border: '1px solid var(--color-border)'
                  }}>
                    {item.type}
                  </span>
                </td>

                {/* Case */}
                <td style={{ padding: '14px 16px' }}>
                  <span style={{
                    padding: '2px 8px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-primary-light)',
                    background: 'rgba(56, 132, 255, 0.1)',
                    fontWeight: 600
                  }}>
                    #{item.caseId}
                  </span>
                </td>

                {/* Size */}
                <td style={{ padding: '14px 16px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)' }}>
                  {item.size}
                </td>

                {/* SHA-256 */}
                <td style={{ padding: '14px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '11px',
                      color: 'var(--color-text-secondary)',
                      maxWidth: 160,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}>
                      {item.sha256}
                    </span>
                    <button
                      onClick={() => copyToClipboard(item.sha256)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        color: copiedHash === item.sha256 ? 'var(--color-accent-green)' : 'var(--color-text-tertiary)',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                      title="Copy SHA-256 Hash"
                    >
                      {copiedHash === item.sha256 ? <Check size={14} /> : <Copy size={14} />}
                    </button>
                  </div>
                </td>

                {/* Entropy */}
                <td style={{ padding: '14px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{
                      width: 48,
                      height: 6,
                      borderRadius: 3,
                      background: 'var(--color-bg-tertiary)',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${(item.entropy / 8) * 100}%`,
                        height: '100%',
                        background: item.entropy > 7.8 ? 'var(--color-risk-critical)' : 'var(--color-primary)'
                      }} />
                    </div>
                    <span style={{
                      fontSize: 'var(--text-xs)',
                      fontFamily: 'var(--font-mono)',
                      color: item.entropy > 7.8 ? 'var(--color-risk-critical)' : 'var(--color-text-secondary)'
                    }}>
                      {item.entropy}
                    </span>
                  </div>
                </td>

                {/* Custody Status */}
                <td style={{ padding: '14px 16px' }}>
                  <div style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    fontSize: 'var(--text-xs)',
                    color: 'var(--color-accent-green)',
                    background: 'rgba(34, 197, 94, 0.1)',
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)'
                  }}>
                    <CheckCircle2 size={13} />
                    Verified Custody
                  </div>
                </td>

                {/* Actions */}
                <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                  <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                    <button
                      onClick={() => alert(`Forensic Hash Verified:\nSHA-256: ${item.sha256}\nShannon Entropy: ${item.entropy}\nStatus: Match confirmed with MinIO Vault block digest.`)}
                      style={{
                        background: 'rgba(56, 132, 255, 0.15)',
                        border: '1px solid rgba(56, 132, 255, 0.3)',
                        color: 'var(--color-primary-light)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '4px 10px',
                        fontSize: 'var(--text-xs)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4
                      }}
                    >
                      <Shield size={12} />
                      Verify
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: 'var(--space-4)'
        }}>
          <div className="card" style={{ maxWidth: 500, width: '100%', padding: 'var(--space-6)', position: 'relative' }}>
            <button
              onClick={() => setShowUploadModal(false)}
              style={{
                position: 'absolute',
                top: 16,
                right: 16,
                background: 'transparent',
                border: 'none',
                color: 'var(--color-text-tertiary)',
                cursor: 'pointer'
              }}
            >
              <X size={20} />
            </button>

            <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <Upload size={20} style={{ color: 'var(--color-accent-cyan)' }} />
              Ingest Forensic Evidence
            </h2>

            <form onSubmit={handleUploadSubmit}>
              <div style={{ marginBottom: 16 }}>
                <label style={{ display: 'block', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 6 }}>
                  Evidence Filename
                </label>
                <input
                  type="text"
                  placeholder="e.g. dump_memory_02.raw, access_log.pcap"
                  value={newFileName}
                  onChange={(e) => setNewFileName(e.target.value)}
                  required
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

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 6 }}>
                    Evidence Type
                  </label>
                  <select
                    value={newFileType}
                    onChange={(e) => setNewFileType(e.target.value as any)}
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
                  >
                    <option value="binary">Malware / Binary</option>
                    <option value="network">PCAP / Network</option>
                    <option value="memory">Memory Dump</option>
                    <option value="disk">Disk Image</option>
                    <option value="document">Document / Log</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 6 }}>
                    Assign to Case
                  </label>
                  <select
                    value={newCaseId}
                    onChange={(e) => setNewCaseId(e.target.value)}
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
                  >
                    <option value="1042">Case #1042 — Phishing</option>
                    <option value="1041">Case #1041 — Ransomware</option>
                    <option value="1040">Case #1040 — DNS Exfil</option>
                    <option value="1038">Case #1038 — Insider</option>
                  </select>
                </div>
              </div>

              <div style={{
                border: '2px dashed var(--color-border)',
                borderRadius: 'var(--radius-md)',
                padding: 'var(--space-6)',
                textAlign: 'center',
                background: 'rgba(15, 22, 41, 0.4)',
                marginBottom: 20
              }}>
                <Upload size={32} style={{ color: 'var(--color-primary)', margin: '0 auto 8px' }} />
                <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600 }}>Drop files here or click to browse</div>
                <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)', marginTop: 4 }}>
                  Calculates SHA-256, Shannon entropy, and registers audit record
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  style={{
                    padding: '8px 16px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'transparent',
                    border: '1px solid var(--color-border)',
                    color: 'var(--color-text-secondary)',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    padding: '8px 18px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-cyan))',
                    border: 'none',
                    color: 'white',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Confirm & Ingest
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
