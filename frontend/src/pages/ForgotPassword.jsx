import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/auth/forgot-password', { email })
      setSent(true)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <span className="auth-logo">⚡</span>
          <h1>EnergyWise</h1>
          <p>Predict your electricity bill before it arrives</p>
        </div>
        <div className="auth-form">
          <h2>Forgot Password</h2>
          {sent ? (
            <div>
              <div className="alert alert-success">
                If that email is registered, a reset link has been sent. Check your inbox.
              </div>
              <p className="auth-footer" style={{ marginTop: '1rem' }}>
                <Link to="/login">← Back to Sign In</Link>
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {error && <div className="alert alert-error">{error}</div>}
              <p className="text-muted" style={{ marginBottom: '1rem', fontSize: '.9rem' }}>
                Enter your registered email and we'll send you a password reset link.
              </p>
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                />
              </div>
              <button type="submit" className="btn-primary btn-full" disabled={loading}>
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
              <p className="auth-footer">
                <Link to="/login">← Back to Sign In</Link>
              </p>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
