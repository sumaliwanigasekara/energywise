import { useEffect, useState } from 'react'
import api from '../services/api'

const OTHER_APPLIANCES = [
  { key: 'fan',    label: 'Ceiling / Table Fan', icon: '🌀', countField: 'fan_count',    hoursField: 'fan_hours_per_day',     desc: 'Total fans in household' },
  { key: 'fridge', label: 'Refrigerator',         icon: '🧊', countField: 'fridge_count', hoursField: null,                    desc: 'Runs 24/7 automatically' },
  { key: 'washer', label: 'Washing Machine',       icon: '🫧', countField: null,           hoursField: 'washer_hours_per_day',  desc: 'Average daily usage hours' },
  { key: 'heater', label: 'Water Heater',          icon: '🚿', countField: null,           hoursField: 'heater_hours_per_day',  desc: 'Average daily usage hours' },
  { key: 'other',  label: 'Other Appliances',      icon: '🔌', countField: null,           hoursField: 'other_hours_per_day',   desc: 'TV, iron, microwave, etc.' },
]

const HOUR_FIELDS = ['fan_hours_per_day', 'washer_hours_per_day', 'heater_hours_per_day', 'other_hours_per_day']

const DEFAULT = {
  fan_count: 0, fan_hours_per_day: 0,
  fridge_count: 1,
  washer_hours_per_day: 0,
  heater_hours_per_day: 0,
  other_hours_per_day: 0,
}

const DEFAULT_AC = { tons: 1.5, hours_per_day: 0 }

function toDaily(profile) {
  const out = { ...profile }
  HOUR_FIELDS.forEach(f => {
    const monthly = f.replace('_per_day', '_per_month')
    out[f] = profile[monthly] != null ? +(profile[monthly] / 30).toFixed(1) : 0
  })
  return out
}

function toMonthly(profile) {
  const out = { ...profile }
  HOUR_FIELDS.forEach(f => {
    const monthly = f.replace('_per_day', '_per_month')
    out[monthly] = Math.round((profile[f] || 0) * 30)
    delete out[f]
  })
  return out
}

export default function Appliances() {
  const [profile, setProfile] = useState(DEFAULT)
  const [acUnits, setAcUnits] = useState([])
  const [exists, setExists] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/appliances')
      .then(r => {
        const d = r.data
        setProfile(toDaily(d))
        // Restore individual AC list, or build a single entry from aggregated values
        if (d.ac_units && d.ac_units.length > 0) {
          setAcUnits(d.ac_units)
        } else if (d.ac_count > 0) {
          setAcUnits(Array.from({ length: d.ac_count }, () => ({
            tons: d.ac_tons ?? 1.5,
            hours_per_day: +((d.ac_hours_per_month || 0) / 30).toFixed(1),
          })))
        }
        setExists(true)
      })
      .catch(err => { if (err.response?.status !== 404) setError('Failed to load profile.') })
  }, [])

  const set = (field, value) => {
    const num = Math.max(0, parseFloat(value) || 0)
    setProfile(p => ({ ...p, [field]: num }))
  }
  const increment = field => setProfile(p => ({ ...p, [field]: (p[field] || 0) + 1 }))
  const decrement = field => setProfile(p => ({ ...p, [field]: Math.max(0, (p[field] || 0) - 1) }))

  const addAC = () => setAcUnits(u => [...u, { ...DEFAULT_AC }])
  const removeAC = i => setAcUnits(u => u.filter((_, idx) => idx !== i))
  const setAC = (i, field, value) =>
    setAcUnits(u => u.map((unit, idx) => idx === i ? { ...unit, [field]: parseFloat(value) || 0 } : unit))

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSaved(false)
    try {
      const payload = { ...toMonthly(profile), ac_units: acUnits }
      if (exists) {
        await api.put('/appliances', payload)
      } else {
        await api.post('/appliances', payload)
        setExists(true)
      }
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch {
      setError('Failed to save. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>My Appliances</h1>
          <p className="text-muted">Set up your home appliance profile — saved for future predictions</p>
        </div>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? 'Saving...' : saved ? '✓ Saved!' : 'Save Profile'}
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {saved && <div className="alert alert-success">Appliance profile saved successfully!</div>}

      {/* Air Conditioners — dynamic list */}
      <div className="card form-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '.5rem' }}>
              <span style={{ fontSize: '1.4rem' }}>❄️</span>
              <strong>Air Conditioners</strong>
            </div>
            <p className="text-muted" style={{ marginTop: '.2rem' }}>Add each AC unit separately if they have different tonnage</p>
          </div>
          <button className="btn-primary" type="button" onClick={addAC}>+ Add AC</button>
        </div>

        {acUnits.length === 0 && (
          <p style={{ color: '#94a3b8', fontSize: '.9rem', marginTop: '.5rem' }}>
            No ACs added yet — click "+ Add AC" to add one.
          </p>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '.75rem', marginTop: acUnits.length ? '.75rem' : 0 }}>
          {acUnits.map((unit, i) => (
            <div key={i} className="ac-unit-row">
              <span className="ac-unit-label">AC {i + 1}</span>

              <div className="ac-unit-field">
                <label>Capacity (tons)</label>
                <select value={unit.tons} onChange={e => setAC(i, 'tons', e.target.value)}>
                  <option value="0.75">0.75 ton</option>
                  <option value="1.0">1.0 ton</option>
                  <option value="1.5">1.5 ton</option>
                  <option value="2.0">2.0 ton</option>
                  <option value="2.5">2.5 ton</option>
                </select>
              </div>

              <div className="ac-unit-field">
                <label>Hours per day</label>
                <input type="number" min="0" max="24" step="0.5"
                  value={unit.hours_per_day}
                  onChange={e => setAC(i, 'hours_per_day', e.target.value)}
                  placeholder="e.g. 6" />
              </div>

              <div className="ac-unit-monthly">
                ≈ {Math.round(unit.hours_per_day * 30)} hrs/month
              </div>

              <button type="button" className="btn-danger-sm" onClick={() => removeAC(i)}>Remove</button>
            </div>
          ))}
        </div>
      </div>

      {/* Other appliances */}
      <div className="appliances-grid">
        {OTHER_APPLIANCES.map(app => (
          <div className="appliance-card" key={app.key}>
            <div className="appliance-header">
              <span className="appliance-icon">{app.icon}</span>
              <div>
                <div className="appliance-name">{app.label}</div>
                <div className="appliance-desc">{app.desc}</div>
              </div>
            </div>

            {app.countField && (
              <div className="appliance-row">
                <label>Number of units</label>
                <div className="counter">
                  <button className="counter-btn" onClick={() => decrement(app.countField)}>−</button>
                  <span className="counter-val">{profile[app.countField] || 0}</span>
                  <button className="counter-btn" onClick={() => increment(app.countField)}>+</button>
                </div>
              </div>
            )}

            {app.hoursField && (
              <div className="appliance-row">
                <label>Hours used per day</label>
                <input
                  type="number" min="0" max="24" step="0.5"
                  value={profile[app.hoursField] || ''}
                  onChange={e => set(app.hoursField, e.target.value)}
                  placeholder="e.g. 4"
                  className="hours-input"
                />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="card tip-card">
        <strong>💡 Tip:</strong> Enter how many hours per day you typically use each appliance.
        For ACs with different sizes, add them one by one using the "+ Add AC" button.
        The system automatically calculates monthly usage (daily × 30).
      </div>
    </div>
  )
}
