import { useState } from 'react'
import cytoscape from 'cytoscape'
import CytoscapeComponent from 'react-cytoscapejs'
import { Filter, Maximize2, Network, Shield, Layers } from 'lucide-react'

// Mock Data for the graph
const mockElements = [
  // Nodes
  { data: { id: 'ev1', label: 'email_01.eml', type: 'evidence', risk: 45 } },
  { data: { id: 'ev2', label: 'wire_instructions.pdf', type: 'evidence', risk: 95 } },
  { data: { id: 'ent1', label: 'John Doe', type: 'person', risk: 10 } },
  { data: { id: 'ent2', label: 'Shell Corp LLC', type: 'organization', risk: 80 } },
  { data: { id: 'ioc1', label: '192.168.100.45', type: 'ipv4', risk: 100 } },
  { data: { id: 'ioc2', label: 'ceo-urgent@company.com', type: 'email', risk: 98 } },
  { data: { id: 'ioc3', label: 'company-portal.com', type: 'domain', risk: 85 } },
  { data: { id: 'ioc4', label: '45.33.22.11', type: 'ipv4', risk: 95 } },
  { data: { id: 'ioc5', label: 'f2a4b...', type: 'sha256', risk: 100 } },

  // Edges
  { data: { source: 'ev1', target: 'ioc2', label: 'CONTAINS' } },
  { data: { source: 'ev1', target: 'ev2', label: 'ATTACHED_TO' } },
  { data: { source: 'ev2', target: 'ent2', label: 'MENTIONS' } },
  { data: { source: 'ev2', target: 'ent1', label: 'MENTIONS' } },
  { data: { source: 'ev2', target: 'ioc5', label: 'HASH' } },
  { data: { source: 'ioc2', target: 'ioc3', label: 'PART_OF' } },
  { data: { source: 'ioc3', target: 'ioc4', label: 'RESOLVES_TO' } },
  { data: { source: 'ioc4', target: 'ioc1', label: 'COMMUNICATES_WITH' } },
]

// Cytoscape Stylesheet
const cyStylesheet: any[] = [
  {
    selector: 'node',
    style: {
      label: 'data(label)',
      'background-color': '#151d35',
      'border-width': 2,
      'border-color': '#3884ff',
      color: '#e2e8f0',
      'text-valign': 'bottom',
      'text-margin-y': 6,
      'font-size': 10,
      'font-family': 'Inter',
      width: 40,
      height: 40,
      'text-outline-width': 2,
      'text-outline-color': '#0a0e1a',
    },
  },
  {
    selector: 'node[type = "evidence"]',
    style: { 'border-color': '#3884ff', 'background-color': 'rgba(56, 132, 255, 0.2)' },
  },
  {
    selector: 'node[type = "ipv4"]',
    style: { 'border-color': '#ef4444', 'background-color': 'rgba(239, 68, 68, 0.2)' },
  },
  {
    selector: 'node[type = "domain"]',
    style: { 'border-color': '#f97316', 'background-color': 'rgba(249, 115, 22, 0.2)' },
  },
  {
    selector: 'node[type = "email"]',
    style: { 'border-color': '#eab308', 'background-color': 'rgba(234, 179, 8, 0.2)' },
  },
  {
    selector: 'node[type = "organization"]',
    style: { 'border-color': '#22c55e', 'background-color': 'rgba(34, 197, 94, 0.2)' },
  },
  {
    selector: 'node[risk >= 90]',
    style: {
      'border-color': '#ef4444',
      'border-width': 3,
      'shadow-blur': 15,
      'shadow-color': '#ef4444',
      'shadow-opacity': 0.8,
    },
  },
  {
    selector: 'edge',
    style: {
      width: 1.5,
      'line-color': 'rgba(56, 132, 255, 0.3)',
      'target-arrow-color': 'rgba(56, 132, 255, 0.3)',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      label: 'data(label)',
      'font-size': 8,
      'text-rotation': 'autorotate',
      'text-margin-y': -8,
      color: '#94a3b8',
      'text-outline-width': 2,
      'text-outline-color': '#0a0e1a',
    },
  },
]

export default function InvestigationGraphPage() {
  const [cy, setCy] = useState<cytoscape.Core | null>(null)

  const handleCenter = () => {
    if (cy) {
      cy.fit()
      cy.center()
    }
  }

  return (
    <div className="animate-in" style={{ height: 'calc(100vh - var(--header-height) - 4rem)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Investigation Graph
          </h1>
          <p className="text-muted text-sm">Case #I042 — Cross-evidence Correlation</p>
        </div>
        <div className="flex gap-3">
          <button className="btn btn-secondary btn-sm" onClick={handleCenter}>
            <Maximize2 size={14} /> Center Graph
          </button>
          <button className="btn btn-secondary btn-sm">
            <Filter size={14} /> Filter Nodes
          </button>
          <button className="btn btn-primary btn-sm">
            <Network size={14} /> Run Layout
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 'var(--space-4)', flex: 1, minHeight: 0 }}>
        {/* Graph Container */}
        <div className="card" style={{ flex: 1, padding: 0, position: 'relative', overflow: 'hidden' }}>
          {/* Cyber grid background */}
          <div style={{
            position: 'absolute', inset: 0,
            backgroundImage: `
              linear-gradient(rgba(56, 132, 255, 0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(56, 132, 255, 0.05) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
            pointerEvents: 'none',
          }} />
          
          <CytoscapeComponent
            elements={mockElements}
            stylesheet={cyStylesheet}
            style={{ width: '100%', height: '100%', position: 'absolute', inset: 0 }}
            layout={{ name: 'cose', padding: 50, idealEdgeLength: 100 }}
            cy={(instance: cytoscape.Core) => setCy(instance)}
            wheelSensitivity={0.1}
          />
        </div>

        {/* Sidebar / Legend */}
        <div className="card" style={{ width: 300, overflowY: 'auto' }}>
          <div className="card-title mb-4">Graph Legend</div>
          
          <div className="flex flex-col gap-3 mb-6">
            <div className="flex items-center gap-3">
              <div style={{ width: 14, height: 14, borderRadius: '50%', border: '2px solid #3884ff', background: 'rgba(56, 132, 255, 0.2)' }} />
              <span className="text-sm">Evidence File</span>
            </div>
            <div className="flex items-center gap-3">
              <div style={{ width: 14, height: 14, borderRadius: '50%', border: '2px solid #ef4444', background: 'rgba(239, 68, 68, 0.2)' }} />
              <span className="text-sm">IP Address (IOC)</span>
            </div>
            <div className="flex items-center gap-3">
              <div style={{ width: 14, height: 14, borderRadius: '50%', border: '2px solid #f97316', background: 'rgba(249, 115, 22, 0.2)' }} />
              <span className="text-sm">Domain / URL</span>
            </div>
            <div className="flex items-center gap-3">
              <div style={{ width: 14, height: 14, borderRadius: '50%', border: '2px solid #22c55e', background: 'rgba(34, 197, 94, 0.2)' }} />
              <span className="text-sm">Organization / Person</span>
            </div>
            <div className="flex items-center gap-3 mt-2">
              <div style={{ width: 14, height: 14, borderRadius: '50%', border: '3px solid #ef4444', boxShadow: '0 0 10px #ef4444' }} />
              <span className="text-sm text-risk-high font-bold">Critical Risk Node</span>
            </div>
          </div>

          <div className="card-title mb-4" style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-muted)' }}>
            Selected Node Details
          </div>
          
          <div style={{ padding: 'var(--space-3)', background: 'var(--color-bg-tertiary)', borderRadius: 'var(--radius-md)' }}>
            <div className="flex items-center gap-2 mb-2">
              <Shield size={16} color="var(--color-risk-high)" />
              <span className="font-bold">192.168.100.45</span>
            </div>
            <div className="text-sm text-muted mb-3">Type: IPv4 Address</div>
            
            <div className="flex flex-col gap-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted">Risk Score</span>
                <span className="font-bold" style={{ color: 'var(--color-risk-high)' }}>100/100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">First Seen</span>
                <span>2025-05-10</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">VT Score</span>
                <span>5/94</span>
              </div>
            </div>

            <button className="btn btn-primary btn-sm w-full mt-4">
              <Layers size={14} /> View Evidence
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
