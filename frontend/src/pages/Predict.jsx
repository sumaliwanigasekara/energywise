import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  PieChart, Pie, Cell, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
} from 'recharts'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import RiskExplanation from '../components/RiskExplanation'

const PIE_COLORS = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16']

const APPLIANCE_LABELS = {
  air_conditioner: 'Air Conditioner',
  fans: 'Fans',
  refrigerator: 'Refrigerator',
  washing_machine: 'Washing Machine',
  water_heater: 'Water Heater',
  other: 'Other',
  base_load: 'Base Load',
}

function ProfileSummary({ profile }) {
  const acUnits = profile.ac_units || []
  return (
    <div className="profile-summary">
      {acUnits.length > 0 && (
        <div className="profile-summary-group">
          <span className="ps-icon">❄️</span>
          <span className="ps-label">Air Conditioners</span>
          <span className="ps-value">
            {acUnits.map((u, i) => `AC${i + 1}: ${u.tons}t × ${u.hours_per_day}h/day`).join('  |  ')}
          </span>
        </div>
      )}
      {profile.fan_count > 0 && (
        <div className="profile-summary-group">
          <span className="ps-icon">🌀</span>
          <span className="ps-label">Fans</span>
          <span className="ps-value">
            {profile.fan_count} fan{profile.fan_count > 1 ? 's' : ''} · {+(profile.fan_hours_per_month / 30).toFixed(1)} h/day
          </span>
        </div>
      )}
      {profile.fridge_count > 0 && (
        <div className="profile-summary-group">
          <span className="ps-icon">🧊</span>
          <span className="ps-label">Refrigerator</span>
          <span className="ps-value">{profile.fridge_count} unit{profile.fridge_count > 1 ? 's' : ''} (24/7)</span>
        </div>
      )}
      {profile.washer_hours_per_month > 0 && (
        <div className="profile-summary-group">
          <span className="ps-icon">🫧</span>
          <span className="ps-label">Washing Machine</span>
          <span className="ps-value">{+(profile.washer_hours_per_month / 30).toFixed(1)} h/day</span>
        </div>
      )}
      {profile.heater_hours_per_month > 0 && (
        <div className="profile-summary-group">
          <span className="ps-icon">🚿</span>
          <span className="ps-label">Water Heater</span>
          <span className="ps-value">{+(profile.heater_hours_per_month / 30).toFixed(1)} h/day</span>
        </div>
      )}
      {profile.other_hours_per_month > 0 && (
        <div className="profile-summary-group">
          <span className="ps-icon">🔌</span>
          <span className="ps-label">Other Appliances</span>
          <span className="ps-value">{+(profile.other_hours_per_month / 30).toFixed(1)} h/day</span>
        </div>
      )}
    </div>
  )
}

export default function Predict() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [profileLoading, setProfileLoading] = useState(true)
  const [form, setForm] = useState({ prev_bill_1: '', prev_bill_2: '', prev_bill_3: '', members: 4 })
  const [autofillSource, setAutofillSource] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [weather, setWeather] = useState(null)

  useEffect(() => {
    api.get('/appliances')
      .then(r => setProfile(r.data))
      .catch(() => {})
      .finally(() => setProfileLoading(false))

    api.get(`/weather?district=${user?.district || 'Colombo'}`)
      .then(r => setWeather(r.data))
      .catch(() => {})

    // Auto-fill past bills from prediction history
    api.get('/predictions/autofill')
      .then(r => {
        const d = r.data
        setForm(f => ({
          ...f,
          ...(d.prev_bill_1 != null && { prev_bill_1: d.prev_bill_1 }),
          ...(d.prev_bill_2 != null && { prev_bill_2: d.prev_bill_2 }),
          ...(d.prev_bill_3 != null && { prev_bill_3: d.prev_bill_3 }),
        }))
        if (d.source?.length > 0) setAutofillSource(d.source)
      })
      .catch(() => {})
  }, [user])

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }))

  const handleSubmit = async e => {
    e.preventDefault()
    if (!profile) {
      navigate('/appliances')
      return
    }
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const payload = {
        prev_bill_1: parseFloat(form.prev_bill_1) || 0,
        prev_bill_2: parseFloat(form.prev_bill_2) || 0,
        prev_bill_3: parseFloat(form.prev_bill_3) || 0,
        members:     parseInt(form.members)        || 4,
        district:    user?.district || 'Colombo',
        // Appliance data from saved profile
        fan_count:              profile.fan_count    || 0,
        fridge_count:           profile.fridge_count || 1,
        ac_count:               profile.ac_count     || 0,
        ac_tons:                profile.ac_tons       || 1.5,
        ac_hours_per_month:     profile.ac_hours_per_month    || 0,
        fan_hours_per_month:    profile.fan_hours_per_month   || 0,
        washer_hours_per_month: profile.washer_hours_per_month|| 0,
        heater_hours_per_month: profile.heater_hours_per_month|| 0,
        other_hours_per_month:  profile.other_hours_per_month || 0,
      }
      const r = await api.post('/predict', payload)
      setResult(r.data)
      setTimeout(() => {
        const el = document.getElementById('results')
        if (el) window.scrollTo({ top: el.offsetTop - 80, behavior: 'smooth' })
      }, 50)
    } catch (err) {
      setError(err.response?.data?.error || 'Prediction failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const pieData = result
    ? Object.entries(result.appliance_breakdown)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => ({ name: APPLIANCE_LABELS[k] || k, value: v }))
    : []

  const billCompareData = result
    ? [
        parseFloat(form.prev_bill_3) > 0 && { name: '3 months ago', bill: parseFloat(form.prev_bill_3) },
        parseFloat(form.prev_bill_2) > 0 && { name: '2 months ago', bill: parseFloat(form.prev_bill_2) },
        parseFloat(form.prev_bill_1) > 0 && { name: 'Last month',   bill: parseFloat(form.prev_bill_1) },
        { name: 'This month (predicted)', bill: result.predicted_units },
      ].filter(Boolean)
    : []

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Predict My Bill</h1>
          <p className="text-muted">Enter your past bills — appliance data is loaded from your saved profile</p>
        </div>
        {weather && (
          <div className="weather-badge">
            <span>🌡️ {weather.avg_temp}°C</span>
            <span>💧 {weather.avg_humidity}%</span>
            <span>💨 {weather.avg_wind} km/h</span>
            <span className="weather-loc">📍 {user?.district}</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit}>
        {/* Past Bills */}
        <div className="card form-section">
          <h3>📋 Past Electricity Bills</h3>
          <p className="text-muted">Enter your actual CEB bill amounts in kWh (units consumed)</p>
          {autofillSource && (
            <div className="alert alert-success" style={{ fontSize: '.85rem', padding: '.6rem .9rem' }}>
              ✓ Auto-filled from your last prediction — edit any value if your actual bill was different.
            </div>
          )}
          <div className="bills-row">
            <div className="form-group">
              <label>Last Month (kWh)</label>
              <input type="number" min="0" step="1" value={form.prev_bill_1}
                onChange={e => set('prev_bill_1', e.target.value)} placeholder="e.g. 120" />
            </div>
            <div className="form-group">
              <label>2 Months Ago (kWh)</label>
              <input type="number" min="0" step="1" value={form.prev_bill_2}
                onChange={e => set('prev_bill_2', e.target.value)} placeholder="e.g. 135" />
            </div>
            <div className="form-group">
              <label>3 Months Ago (kWh)</label>
              <input type="number" min="0" step="1" value={form.prev_bill_3}
                onChange={e => set('prev_bill_3', e.target.value)} placeholder="e.g. 110" />
            </div>
          </div>
        </div>

        {/* Household */}
        <div className="card form-section">
          <h3>👨‍👩‍👧 Household</h3>
          <div className="form-group" style={{ maxWidth: '200px' }}>
            <label>Number of Members</label>
            <input type="number" min="1" max="20" value={form.members}
              onChange={e => set('members', e.target.value)} />
          </div>
        </div>

        {/* Appliance Profile Summary */}
        <div className="card form-section">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '.75rem' }}>
            <h3>🔌 Appliance Profile</h3>
            <button type="button" className="btn-outline" onClick={() => navigate('/appliances')}>
              Edit Profile
            </button>
          </div>

          {profileLoading ? (
            <p className="text-muted">Loading your appliance profile...</p>
          ) : profile ? (
            <ProfileSummary profile={profile} />
          ) : (
            <div className="alert alert-warning" style={{ marginBottom: 0 }}>
              No appliance profile saved yet.{' '}
              <span style={{ color: '#b45309', fontWeight: 500, cursor: 'pointer' }}
                onClick={() => navigate('/appliances')}>
                Set up your appliances first →
              </span>
            </div>
          )}
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <button type="submit" className="btn-primary btn-full btn-predict"
          disabled={loading || !profile || profileLoading}>
          {loading ? '⏳ Calculating...' : '⚡ Predict My Bill'}
        </button>
      </form>

      {/* Results */}
      {result && (
        <div id="results" className="results-section">
          <h2>Prediction Results</h2>

          <div className="result-top">
            <div className="result-main-card">
              <div className="result-units">{result.predicted_units} <span>kWh</span></div>
              <div className="result-bill">LKR {result.predicted_bill?.toLocaleString()}</div>
              <span className={`badge badge-${result.risk_level?.toLowerCase()} badge-lg`}>
                {result.risk_level} Risk
              </span>
            </div>

            {result.weather && (
              <div className="weather-card">
                <h4>🌤️ Weather — {user?.district}</h4>
                <div className="weather-grid">
                  <div className="weather-item"><span>🌡️</span><strong>{result.weather.avg_temp}°C</strong><small>Avg Temp</small></div>
                  <div className="weather-item"><span>💧</span><strong>{result.weather.avg_humidity}%</strong><small>Humidity</small></div>
                  <div className="weather-item"><span>🌧️</span><strong>{result.weather.total_precip} mm</strong><small>Precipitation</small></div>
                  <div className="weather-item"><span>💨</span><strong>{result.weather.avg_wind} km/h</strong><small>Wind</small></div>
                </div>
              </div>
            )}
          </div>

          <RiskExplanation currentLevel={result.risk_level} predictedUnits={result.predicted_units} />

          <div className="charts-row">
            <div className="chart-card">
              <h3>Appliance Breakdown</h3>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" outerRadius={100}
                    dataKey="value" nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}>
                    {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                  </Pie>
                  <Tooltip formatter={v => `${v} kWh`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-card">
              <h3>Bill Trend Comparison (kWh)</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={billCompareData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={v => `${v} kWh`} />
                  <Bar dataKey="bill" radius={[4, 4, 0, 0]} fill="#2563eb"
                    label={{ position: 'top', fontSize: 11 }} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {result.recommendations?.length > 0 && (
            <div className="card">
              <h3>💡 Recommendations to Reduce Your Bill</h3>
              <div className="recs-list">
                {result.recommendations.map((r, i) => (
                  <div key={i} className={`rec-card priority-${r.priority}`}>
                    <div className="rec-header">
                      <div>
                        <span className={`priority-badge ${r.priority}`}>{r.priority.toUpperCase()}</span>
                        <span className="rec-category">{r.category}</span>
                      </div>
                      {r.saving_lkr > 0 && (
                        <div className="rec-saving">Save LKR {r.saving_lkr?.toLocaleString()}</div>
                      )}
                    </div>
                    <h4 className="rec-title">{r.title}</h4>
                    <p className="rec-desc">{r.description}</p>
                    {r.saving_kwh > 0 && (
                      <div className="rec-kwh">💡 Potential saving: {r.saving_kwh} kWh/month</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
