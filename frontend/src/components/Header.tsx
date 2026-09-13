import { Search, Bell, User } from 'lucide-react'

export default function Header() {
  return (
    <header className="header">
      {/* Search Bar */}
      <div className="header-search">
        <Search size={16} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
        <input
          type="text"
          placeholder="Search evidence, IOCs, entities, cases..."
          id="global-search"
        />
        <kbd style={{
          fontSize: '10px',
          padding: '2px 6px',
          background: 'var(--color-bg-tertiary)',
          borderRadius: '4px',
          color: 'var(--color-text-muted)',
          border: '1px solid var(--color-border)',
          flexShrink: 0,
        }}>⌘K</kbd>
      </div>

      {/* Actions */}
      <div className="header-actions">
        <button
          className="btn btn-secondary btn-sm"
          style={{ position: 'relative' }}
          id="notifications-btn"
        >
          <Bell size={16} />
          <span style={{
            position: 'absolute', top: -4, right: -4,
            width: 16, height: 16, borderRadius: '50%',
            background: 'var(--color-risk-high)',
            fontSize: '9px', fontWeight: 700,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'white',
          }}>3</span>
        </button>

        <button className="btn btn-secondary btn-sm" id="user-menu-btn">
          <User size={16} />
        </button>
      </div>
    </header>
  )
}
