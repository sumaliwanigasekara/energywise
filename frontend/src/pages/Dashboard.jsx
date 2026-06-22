import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar,
  PieChart, Pie, Cell,
} from 'recharts'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import RiskExplanation from '../components/RiskExplanation'

const RISK_COLOR  = { Low: '#10b981', Medium: '#f59e0b', High: '#ef4444' }
const PIE_COLORS  = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16']
const APPL_LABELS = {
  air_conditioner: 'Air Conditioner', fans: 'Fans', refrigerator: 'Refrigerator',
  washing_machine: 'Washing Machine', water_heater: 'Water Heater',
  other: 'Other', base_load: 'Base Load',
}

function PredictionModal({ p, onClose }) {
  if (!p) return null

  const pieData = Object.entries(p.appliance_breakdown || {})
    .filter(([, v]) => v > 0)
    .map(([k, v]) => ({ name: APPL_LABELS[k] || k, value: v }))

  const billBar = [
    p.prev_bill_3 > 0 && { name: '3 months ago', bill: p.prev_bill_3 },
    p.prev_bill_2 > 0 && { name: '2 months ago', bill: p.prev_bill_2 },
    p.prev_bill_1 > 0 && { name: 'Last month',   bill: p.prev_bill_1 },
    { name: 'This month',  bill: p.predicted_units },
  ].filter(Boolean)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2>Prediction Details</h2>
            <p className="text-muted">{new Date(p.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' })}</p>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Result summary */}
          <div className="modal-result-row">
            <div className="result-main-card" style={{ flex: 1, minWidth: 0 }}>
              <div className="result-units">{p.predicted_units} <span>kWh</span></div>
              <div className="result-bill">LKR {p.predicted_bill?.toLocaleString()}</div>
              <span className={`badge badge-${p.risk_level?.toLowerCase()} badge-lg`}>{p.risk_level} Risk</span>
            </div>

            {(p.avg_temp || p.avg_humidity) && (
              <div className="weather-card" style={{ flex: 1, minWidth: 0 }}>
                <h4>🌤️ Weather at Prediction Time</h4>
                <div className="weather-grid">
                  {p.avg_temp    && <div className="weather-item"><span>🌡️</span><strong>{p.avg_temp}°C</strong><small>Avg Temp</small></div>}
                  {p.avg_humidity&& <div className="weather-item"><span>💧</span><strong>{p.avg_humidity}%</strong><small>Humidity</small></div>}
                  {p.total_precip!= null && <div className="weather-item"><span>🌧️</span><strong>{p.total_precip} mm</strong><small>Precipitation</small></div>}
                  {p.avg_wind    && <div className="weather-item"><span>💨</span><strong>{p.avg_wind} km/h</strong><small>Wind</small></div>}
                </div>
              </div>
            )}
          </div>

          {/* Charts */}
          {(pieData.length > 0 || billBar.length > 1) && (
            <div className="charts-row">
              {pieData.length > 0 && (
                <div className="chart-card">
                  <h3>Appliance Breakdown</h3>
                  <ResponsiveContainer width="100%" height={240}>
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" outerRadius={85}
                        dataKey="value" nameKey="name"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        labelLine={false}>
                        {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                      </Pie>
                      <Tooltip formatter={v => `${v} kWh`} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
              {billBar.length > 1 && (
                <div className="chart-card">
                  <h3>Bill Trend (kWh)</h3>
                  <ResponsiveContainer width="100%" height={240}>
                    <BarChart data={billBar}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip formatter={v => `${v} kWh`} />
                      <Bar dataKey="bill" radius={[4,4,0,0]} fill="#2563eb"
                        label={{ position: 'top', fontSize: 10 }} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          <RiskExplanation currentLevel={p.risk_level} predictedUnits={p.predicted_units} />

          {/* Recommendations */}
          {p.recommendations?.length > 0 && (
            <div>
              <h3 style={{ marginBottom: '.75rem' }}>💡 Recommendations</h3>
              <div className="recs-list">
                {p.recommendations.map((r, i) => (
                  <div key={i} className={`rec-card priority-${r.priority}`}>
                    <div className="rec-header">
                      <div>
                        <span className={`priority-badge ${r.priority}`}>{r.priority?.toUpperCase()}</span>
                        <span className="rec-category">{r.category}</span>
                      </div>
                      {r.saving_lkr > 0 && <div className="rec-saving">Save LKR {r.saving_lkr?.toLocaleString()}</div>}
                    </div>
                    <h4 className="rec-title">{r.title}</h4>
                    <p className="rec-desc">{r.description}</p>
                    {r.saving_kwh > 0 && <div className="rec-kwh">💡 {r.saving_kwh} kWh/month saving</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [actualInput, setActualInput] = useState({})   // {id: value}
  const [savingActual, setSavingActual] = useState(null)

  useEffect(() => {
    api.get('/predictions?per_page=10')
      .then(r => setPredictions(r.data.predictions))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const chartData = [...predictions].reverse().map((p, i) => ({
    name: `#${i + 1}`,
    units: p.predicted_units,
    bill:  p.predicted_bill,
    date:  new Date(p.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }),
  }))

  const latest = predictions[0]

  const handleSaveActual = async (id) => {
    const val = parseFloat(actualInput[id])
    if (!val || val <= 0) return
    setSavingActual(id)
    try {
      const r = await api.patch(`/predictions/${id}/actual`, { actual_units: val })
      setPredictions(prev => prev.map(p => p.id === id ? r.data : p))
      setActualInput(a => ({ ...a, [id]: '' }))
    } catch {
      alert('Failed to save. Please try again.')
    } finally {
      setSavingActual(null)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this prediction from your history?')) return
    setDeleting(id)
    try {
      await api.delete(`/predictions/${id}`)
      setPredictions(prev => prev.filter(p => p.id !== id))
      if (selected?.id === id) setSelected(null)
    } catch {
      alert('Failed to delete. Please try again.')
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.name?.split(' ')[0]} 👋</h1>
          <p className="text-muted">Here's your electricity usage overview</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/predict')}>+ New Prediction</button>
      </div>

      {/* Summary cards */}
      <div className="cards-row">
        <div className="stat-card stat-card-blue">
          <div className="stat-label">Latest Predicted Bill</div>
          <div className="stat-value">{latest ? `LKR ${latest.predicted_bill?.toLocaleString()}` : '—'}</div>
          {latest && <span className={`badge badge-${latest.risk_level?.toLowerCase()}`}>{latest.risk_level} Risk</span>}
        </div>
        <div className="stat-card stat-card-green">
          <div className="stat-label">Predicted Units</div>
          <div className="stat-value">{latest ? `${latest.predicted_units} kWh` : '—'}</div>
          <div className="stat-sub">This month estimate</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Predictions</div>
          <div className="stat-value">{predictions.length}</div>
          <div className="stat-sub">Lifetime</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">District</div>
          <div className="stat-value" style={{ fontSize: '1.4rem' }}>{user?.district}</div>
          <div className="stat-sub">Your location</div>
        </div>
      </div>

      {loading ? (
        <div className="loading-box">Loading prediction history...</div>
      ) : predictions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h3>No predictions yet</h3>
          <p>Make your first prediction to see your usage trends here.</p>
          <button className="btn-primary" onClick={() => navigate('/predict')}>Make First Prediction</button>
        </div>
      ) : (
        <>
          <div className="charts-row">
            <div className="chart-card">
              <h3>Predicted Units Over Time (kWh)</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="units" stroke="#2563eb" strokeWidth={2} dot={{ r: 4 }} name="kWh" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-card">
              <h3>Predicted Bill (LKR)</h3>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={v => `LKR ${v.toLocaleString()}`} />
                  <Bar dataKey="bill" fill="#10b981" name="Bill (LKR)" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginBottom: '1rem' }}>Prediction History</h3>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Predicted (kWh)</th>
                    <th>Predicted Bill</th>
                    <th>Actual (kWh)</th>
                    <th>Actual Bill</th>
                    <th>Accuracy</th>
                    <th>Risk</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.map(p => {
                    const accuracy = p.actual_units
                      ? Math.max(0, 100 - Math.abs((p.predicted_units - p.actual_units) / p.actual_units * 100))
                      : null
                    return (
                      <tr key={p.id}>
                        <td>{new Date(p.created_at).toLocaleDateString('en-GB')}</td>
                        <td><strong>{p.predicted_units}</strong></td>
                        <td>LKR {p.predicted_bill?.toLocaleString()}</td>
                        <td>
                          {p.actual_units ? (
                            <strong style={{ color: '#10b981' }}>{p.actual_units}</strong>
                          ) : (
                            <div className="actual-input-row">
                              <input
                                type="number" min="1" placeholder="Enter kWh"
                                className="actual-input"
                                value={actualInput[p.id] || ''}
                                onChange={e => setActualInput(a => ({ ...a, [p.id]: e.target.value }))}
                              />
                              <button className="btn-view"
                                disabled={savingActual === p.id || !actualInput[p.id]}
                                onClick={() => handleSaveActual(p.id)}>
                                {savingActual === p.id ? '...' : 'Save'}
                              </button>
                            </div>
                          )}
                        </td>
                        <td>{p.actual_bill ? `LKR ${p.actual_bill?.toLocaleString()}` : '—'}</td>
                        <td>
                          {accuracy != null ? (
                            <span style={{ color: accuracy >= 90 ? '#10b981' : accuracy >= 75 ? '#f59e0b' : '#ef4444', fontWeight: 600 }}>
                              {accuracy.toFixed(1)}%
                            </span>
                          ) : '—'}
                        </td>
                        <td>
                          <span className={`badge badge-${p.risk_level?.toLowerCase()}`}>{p.risk_level}</span>
                        </td>
                        <td style={{ display: 'flex', gap: '.5rem' }}>
                          <button className="btn-view" onClick={() => setSelected(p)}>View</button>
                          <button className="btn-danger-sm" disabled={deleting === p.id}
                            onClick={() => handleDelete(p.id)}>
                            {deleting === p.id ? '...' : 'Delete'}
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      <PredictionModal p={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
