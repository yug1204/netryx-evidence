import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FolderOpen,
  FileSearch,
  Shield,
  Network,
  Clock,
  FileText,
  Bot,
  Settings,
} from 'lucide-react'

const navItems = [
  { label: 'MAIN', items: [
    { to: '/dashboard', icon: LayoutDashboard, text: 'Dashboard' },
    { to: '/cases', icon: FolderOpen, text: 'Cases' },
    { to: '/evidence', icon: FileSearch, text: 'Evidence' },
  ]},
  { label: 'ANALYSIS', items: [
    { to: '/ioc-analysis', icon: Shield, text: 'IOC Analysis' },
    { to: '/investigation-graph', icon: Network, text: 'Investigation Graph' },
    { to: '/timeline', icon: Clock, text: 'Timeline' },
  ]},
  { label: 'INTELLIGENCE', items: [
    { to: '/reports', icon: FileText, text: 'Reports' },
    { to: '/ai-assistant', icon: Bot, text: 'AI Assistant' },
    { to: '/settings', icon: Settings, text: 'Settings' },
  ]},
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">N</div>
        <div>
          <div className="sidebar-brand-text">NETRYX EVIDENCE</div>
          <div className="sidebar-brand-sub">Intelligence Platform</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        {navItems.map((section) => (
          <div key={section.label}>
            <div className="sidebar-section-label">{section.label}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'active' : ''}`
                }
              >
                <item.icon className="sidebar-link-icon" size={20} />
                <span>{item.text}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* User Status */}
      <div style={{
        padding: 'var(--space-4) var(--space-6)',
        borderTop: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-3)',
      }}>
        <div style={{
          width: 32, height: 32,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-cyan))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 'var(--text-xs)', fontWeight: 700, color: 'white',
        }}>
          I1
        </div>
        <div>
          <div style={{ fontSize: 'var(--text-sm)', fontWeight: 600 }}>Investigator 01</div>
          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-green)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--color-accent-green)', display: 'inline-block' }} />
            Online
          </div>
        </div>
      </div>
    </aside>
  )
}
