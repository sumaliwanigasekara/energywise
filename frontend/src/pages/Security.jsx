import { useState } from 'react'
import api from '../services/api'

export default function Security() {
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' })
  const [pwShow, setPwShow] = useState({ current: false, newPw: false, confirm: false })
  const [pwError, setPwError] = useState('')
  const [pwSuccess, setPwSuccess] = useState('')
  const [pwSaving, setPwSaving] = useState(false)

  const handleChangePassword = async e => {
    e.preventDefault()
    setPwError('')
    setPwSuccess('')
    if (pwForm.newPw !== pwForm.confirm) {
      setPwError('New passwords do not match.')
      return
    }
    setPwSaving(true)
    try {
      await api.put('/auth/change-password', { current_password: pwForm.current, new_password: pwForm.newPw })
      setPwSuccess('Password changed successfully!')
      setPwForm({ current: '', newPw: '', confirm: '' })
      setTimeout(() => setPwSuccess(''), 4000)
    } catch (err) {
      setPwError(err.response?.data?.error || 'Failed to change password.')
    } finally {
      setPwSaving(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Security</h1>
          <p className="text-muted">Manage your account security settings</p>
        </div>
      </div>

      <div className="card" style={{ maxWidth: '480px' }}>
        <h3 style={{ marginBottom: '.25rem' }}>🔒 Change Password</h3>
        <p className="text-muted" style={{ marginBottom: '1rem', fontSize: '.88rem' }}>
          Update your account password. You'll need to enter your current password to confirm.
        </p>
        <form onSubmit={handleChangePassword}>
          {pwError   && <div className="alert alert-error"   style={{ marginBottom: '.75rem' }}>{pwError}</div>}
          {pwSuccess && <div className="alert alert-success" style={{ marginBottom: '.75rem' }}>{pwSuccess}</div>}
          {[
            { key: 'current', label: 'Current Password',     placeholder: 'Enter current password',  ac: 'current-password' },
            { key: 'newPw',   label: 'New Password',         placeholder: 'At least 6 characters',   ac: 'new-password' },
            { key: 'confirm', label: 'Confirm New Password', placeholder: 'At least 6 characters',   ac: 'new-password' },
          ].map(({ key, label, placeholder, ac }) => (
            <div className="form-group" key={key}>
              <label>{label}</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={pwShow[key] ? 'text' : 'password'}
                  value={pwForm[key]}
                  onChange={e => setPwForm(f => ({ ...f, [key]: e.target.value }))}
                  placeholder={placeholder}
                  autoComplete={ac}
                  required
                  style={{ paddingRight: '2.5rem', width: '100%', boxSizing: 'border-box' }}
                />
                <button type="button" tabIndex={-1}
                  onClick={() => setPwShow(s => ({ ...s, [key]: !s[key] }))}
                  style={{
                    position: 'absolute', right: '.6rem', top: '50%',
                    transform: 'translateY(-50%)', background: 'none',
                    border: 'none', cursor: 'pointer', color: '#64748b', fontSize: '1rem', padding: 0,
                  }}>
                  {pwShow[key] ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
          ))}
          <button type="submit" className="btn-primary btn-full" disabled={pwSaving}>
            {pwSaving ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>
    </div>
  )
}
