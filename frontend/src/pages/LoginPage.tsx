import { useState } from 'react'
import { Shield, Lock, Eye, EyeOff } from 'lucide-react'

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Integrate with auth API
    window.location.href = '/dashboard'
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--color-bg-primary)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Animated Background Grid */}
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: `
          linear-gradient(rgba(56, 132, 255, 0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(56, 132, 255, 0.03) 1px, transparent 1px)
        `,
        backgroundSize: '60px 60px',
      }} />

      {/* Glow Effect */}
      <div style={{
        position: 'absolute',
        width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(56, 132, 255, 0.08) 0%, transparent 70%)',
        top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
        borderRadius: '50%',
      }} />

      {/* Login Card */}
      <div className="card animate-in" style={{
        width: 420,
        padding: 'var(--space-10)',
        position: 'relative',
        zIndex: 1,
        boxShadow: 'var(--shadow-glow-strong)',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
          <div style={{
            width: 56, height: 56, margin: '0 auto var(--space-4)',
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-accent-cyan))',
            borderRadius: 'var(--radius-lg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 20px rgba(56, 132, 255, 0.3)',
          }}>
            <Shield size={28} color="white" />
          </div>
          <h1 style={{
            fontSize: 'var(--text-xl)', fontWeight: 800,
            letterSpacing: '-0.02em', marginBottom: 'var(--space-1)',
          }}>
            NETRYX EVIDENCE
          </h1>
          <p style={{
            fontSize: 'var(--text-xs)', color: 'var(--color-accent-cyan)',
            textTransform: 'uppercase', letterSpacing: '0.15em', fontWeight: 600,
          }}>
            Intelligence Platform
          </p>
        </div>

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label className="form-label" htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              className="input"
              placeholder="investigator@netryx.io"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="login-password">Password</label>
            <div style={{ position: 'relative' }}>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                className="input"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{ paddingRight: 44 }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute', right: 12, top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: 'var(--color-text-muted)',
                }}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg w-full"
            id="login-submit"
            style={{ marginTop: 'var(--space-2)' }}
          >
            <Lock size={16} /> Sign In
          </button>
        </form>

        <p style={{
          textAlign: 'center', marginTop: 'var(--space-6)',
          fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)',
        }}>
          AI + Cybersecurity + Digital Forensics + Graph Intelligence
        </p>
      </div>
    </div>
  )
}
