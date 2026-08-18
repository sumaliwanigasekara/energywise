import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../services/api'

const RISK_COLORS = { Low: '#10b981', Moderate: '#f59e0b', High: '#ef4444' }

function PredictionModal({ prediction: p, onClose }) {
  if (!p) return null
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem',
    }} onClick={onClose}>
      <div style={{
        background: '#fff', borderRadius: '12px', padding: '1.5rem',
        maxWidth: '560px', width: '100%', maxHeight: '90vh', overflowY: 'auto',
      }} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0 }}>Prediction #{p.id} — {new Date(p.created_at).toLocaleDateString('en-GB')}</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '1.4rem', cursor: 'pointer', color: '#64748b' }}>×</button>
        </div>

        {/* Result */}
        <div style={{ background: '#1e3a5f', color: '#fff', borderRadius: '8px', padding: '1rem', marginBottom: '1rem', textAlign: 'center' }}>
          <div style={{ fontSize: '1.8rem', fontWeight: 700 }}>{p.predicted_units} kWh</div>
          <div style={{ fontSize: '1.1rem' }}>LKR {p.predicted_bill?.toLocaleString()}</div>
          <span className={`badge badge-${p.consumption_level?.toLowerCase()}`} style={{ marginTop: '.4rem', display: 'inline-block' }}>
            {p.consumption_level}
          </span>
        </div>

        {/* Previous Bills */}
        <div style={{ marginBottom: '1rem' }}>
          <h4 style={{ marginBottom: '.5rem', color: '#374151' }}>📋 Previous Bills Entered</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '.5rem' }}>
            {[['Last Month', p.prev_bill_1], ['2 Months Ago', p.prev_bill_2], ['3 Months Ago', p.prev_bill_3]].map(([label, val]) => (
              <div key={label} style={{ background: '#f8fafc', borderRadius: '6px', padding: '.6rem', textAlign: 'center' }}>
                <div style={{ fontSize: '.75rem', color: '#64748b' }}>{label}</div>
                <div style={{ fontWeight: 600 }}>{val > 0 ? `${val} kWh` : '—'}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Household */}
        <div style={{ marginBottom: '1rem' }}>
          <h4 style={{ marginBottom: '.5rem', color: '#374151' }}>👨‍👩‍👧 Household</h4>
          <div style={{ background: '#f8fafc', borderRadius: '6px', padding: '.6rem' }}>
            <span style={{ marginRight: '1.5rem' }}><strong>Members:</strong> {p.members}</span>
            <span><strong>District:</strong> {p.district}</span>
          </div>
        </div>

        {/* Appliances */}
        <div style={{ marginBottom: '1rem' }}>
          <h4 style={{ marginBottom: '.5rem', color: '#374151' }}>🔌 Appliance Profile Used</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '.3rem' }}>
            {p.ac_count > 0 && (
              <div style={{ background: '#f8fafc', borderRadius: '6px', padding: '.5rem .8rem', fontSize: '.88rem' }}>
                ❄️ <strong>AC:</strong> {p.ac_count} unit(s) · {p.ac_tons} ton · {+(p.ac_hours_per_month / 30).toFixed(1)} h/day
              </div>
            )}
            {p.fan_count > 0 && (
              <div style={{ background: '#f8fafc', borderRadius: '6px', padding: '.5rem .8rem', fontSize: '.88rem' }}>
                🌀 <strong>Fan:</strong> {p.fan_count} unit(s)
              </div>
            )}
            {p.fridge_count > 0 && (
              <div style={{ background: '#f8fafc', borderRadius: '6px', padding: '.5rem .8rem', fontSize: '.88rem' }}>
                🧊 <strong>Fridge:</strong> {p.fridge_count} unit(s) — 24/7
              </div>
            )}
            {p.washer_hours_per_month > 0 && (
              <div style={{ background: '#f8fafc', borderRadius: '6px', padding: '.5rem .8rem', fontSize: '.88rem' }}>
                🫧 <strong>Washing Machine:</strong> {+(p.washer_hours_per_month / 4).toFixed(1)} h/week
              </div>
            )}
            {p.heater_hours_per_month > 0 && (
              <div style={{ background: '#f8fafc', borderRadius: '6px', padding: '.5rem .8rem', fontSize: '.88rem' }}>
                🚿 <strong>Water Heater:</strong> {+(p.heater_hours_per_month / 4).toFixed(1)} h/week
              </div>
            )}
            {p.other_hours_per_month > 0 && (
              <div style={{ background: '#f8fafc', borderRadius: '6px', padding: '.5rem .8rem', fontSize: '.88rem' }}>
                🔌 <strong>Other:</strong> {+(p.other_hours_per_month / 30).toFixed(1)} h/day
              </div>
            )}
          </div>
        </div>

        {/* Weather */}
        <div style={{ marginBottom: '1rem' }}>
          <h4 style={{ marginBottom: '.5rem', color: '#374151' }}>🌤️ Weather Data (30-day avg)</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '.5rem' }}>
            {[
              ['🌡️ Avg Temp', `${p.avg_temp}°C`],
              ['💧 Humidity', `${p.avg_humidity}%`],
              ['🌧️ Precipitation', `${p.total_precip} mm`],
              ['💨 Wind', `${p.avg_wind} km/h`],
            ].map(([label, val]) => (
              <div key={label} style={{ background: '#f0f9ff', borderRadius: '6px', padding: '.6rem', fontSize: '.88rem' }}>
                <span style={{ color: '#64748b' }}>{label}</span>
                <div style={{ fontWeight: 600 }}>{val ?? '—'}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Actual bill if provided */}
        {p.actual_units != null && (
          <div style={{ background: '#f0fdf4', border: '1px solid #86efac', borderRadius: '6px', padding: '.75rem', marginBottom: '1rem' }}>
            <strong>✅ Actual Bill Recorded:</strong> {p.actual_units} kWh · LKR {p.actual_bill?.toLocaleString()}
            <div style={{ fontSize: '.82rem', color: '#16a34a', marginTop: '.3rem' }}>
              Accuracy: {Math.max(0, (1 - Math.abs(p.predicted_units - p.actual_units) / p.actual_units) * 100).toFixed(1)}%
            </div>
          </div>
        )}

        <button onClick={onClose} className="btn-primary btn-full" style={{ marginTop: '.5rem' }}>Close</button>
      </div>
    </div>
  )
}

function UserPredictions({ userId, onCountChange, onView }) {
  const [predictions, setPredictions] = useState(null)
  const [deleting, setDeleting] = useState(null)

  useEffect(() => {
    api.get(`/admin/users/${userId}/predictions`)
      .then(r => setPredictions(r.data.predictions))
      .catch(() => setPredictions([]))
  }, [userId])

  const handleDelete = async id => {
    if (!window.confirm('Delete this prediction?')) return
    setDeleting(id)
    try {
      await api.delete(`/admin/predictions/${id}`)
      setPredictions(p => p.filter(x => x.id !== id))
      onCountChange(c => c - 1)
    } catch (err) {
      alert(err.response?.data?.error || 'Delete failed.')
    } finally {
      setDeleting(null)
    }
  }

  if (!predictions) return (
    <tr><td colSpan={6} style={{ padding: '.75rem 1rem', color: '#94a3b8', fontSize: '.85rem' }}>Loading predictions...</td></tr>
  )

  if (predictions.length === 0) return (
    <tr><td colSpan={6} style={{ padding: '.75rem 1rem', color: '#94a3b8', fontSize: '.85rem' }}>No predictions yet.</td></tr>
  )

  return predictions.map(p => (
    <tr key={p.id} style={{ background: '#f8fafc' }}>
      <td style={{ paddingLeft: '2rem', color: '#64748b', fontSize: '.82rem' }}>
        #{p.id} · {new Date(p.created_at).toLocaleDateString('en-GB')}
      </td>
      <td style={{ fontSize: '.85rem' }}>{p.predicted_units} kWh</td>
      <td style={{ fontSize: '.85rem' }}>LKR {p.predicted_bill?.toLocaleString()}</td>
      <td>
        <span className={`badge badge-${p.consumption_level?.toLowerCase()}`} style={{ fontSize: '.75rem' }}>
          {p.consumption_level}
        </span>
      </td>
      <td style={{ fontSize: '.82rem', color: '#64748b' }}>{p.district}</td>
      <td style={{ display: 'flex', gap: '.3rem' }}>
        <button
          className="btn-outline"
          onClick={() => onView(p)}
          style={{ fontSize: '.75rem', padding: '.2rem .6rem' }}
        >
          View
        </button>
        <button
          className="btn-danger-sm"
          onClick={() => handleDelete(p.id)}
          disabled={deleting === p.id}
          style={{ fontSize: '.75rem', padding: '.2rem .6rem' }}
        >
          {deleting === p.id ? '...' : 'Delete'}
        </button>
      </td>
    </tr>
  ))
}

export default function Admin() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)
  const [expandedUser, setExpandedUser] = useState(null)
  const [predCounts, setPredCounts] = useState({})
  const [viewingPrediction, setViewingPrediction] = useState(null)

  const loadData = async p => {
    setLoading(true)
    try {
      const [statsRes, usersRes] = await Promise.all([
        api.get('/admin/stats'),
        api.get(`/admin/users?page=${p}`),
      ])
      setStats(statsRes.data)
      setUsers(usersRes.data.users)
      setTotal(usersRes.data.total)
      setPages(usersRes.data.pages)
      const counts = {}
      usersRes.data.users.forEach(u => { counts[u.id] = u.prediction_count })
      setPredCounts(counts)
    } catch {
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData(page) }, [page])

  const handleDeleteUser = async userId => {
    if (!window.confirm('Delete this user and all their data?')) return
    setDeleting(userId)
    try {
      await api.delete(`/admin/users/${userId}`)
      setUsers(u => u.filter(x => x.id !== userId))
      setTotal(t => t - 1)
      if (expandedUser === userId) setExpandedUser(null)
    } catch (err) {
      alert(err.response?.data?.error || 'Delete failed.')
    } finally {
      setDeleting(null)
    }
  }

  const toggleExpand = userId => {
    setExpandedUser(prev => prev === userId ? null : userId)
  }

  const riskPieData = stats
    ? Object.entries(stats.risk_distribution).map(([name, value]) => ({ name, value }))
    : []

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Admin Panel</h1>
          <p className="text-muted">Manage consumers and view system statistics</p>
        </div>
      </div>

      <PredictionModal prediction={viewingPrediction} onClose={() => setViewingPrediction(null)} />

      {loading ? (
        <div className="loading-box">Loading...</div>
      ) : (
        <>
          {stats && (
            <div className="cards-row">
              <div className="stat-card stat-card-blue">
                <div className="stat-label">Total Consumers</div>
                <div className="stat-value">{stats.total_users}</div>
              </div>
              <div className="stat-card stat-card-green">
                <div className="stat-label">Total Predictions</div>
                <div className="stat-value">{stats.total_predictions}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Avg Predicted Bill</div>
                <div className="stat-value" style={{ fontSize: '1.4rem' }}>
                  LKR {stats.avg_predicted_bill?.toLocaleString()}
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Avg Predicted Units</div>
                <div className="stat-value" style={{ fontSize: '1.4rem' }}>
                  {stats.avg_predicted_units} kWh
                </div>
              </div>
              <div className="stat-card stat-card-green">
                <div className="stat-label">Model Accuracy</div>
                <div className="stat-value">
                  {stats.avg_accuracy != null ? `${stats.avg_accuracy}%` : 'N/A'}
                </div>
                <div className="stat-sub">{stats.predictions_with_actual} verified predictions</div>
              </div>
            </div>
          )}

          {riskPieData.length > 0 && (
            <div className="card" style={{ maxWidth: '480px' }}>
              <h3>Risk Distribution</h3>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={riskPieData} cx="50%" cy="50%" outerRadius={90}
                    dataKey="value" nameKey="name"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                    {riskPieData.map((entry, i) => (
                      <Cell key={i} fill={RISK_COLORS[entry.name] || '#94a3b8'} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="card">
            <div className="table-header">
              <h3>Consumers ({total})</h3>
            </div>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>District</th>
                    <th>Predictions</th>
                    <th>Registered</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <>
                      <tr key={u.id}>
                        <td><strong>{u.name}</strong></td>
                        <td>{u.email}</td>
                        <td>{u.district}</td>
                        <td>{predCounts[u.id] ?? u.prediction_count}</td>
                        <td>{new Date(u.created_at).toLocaleDateString('en-GB')}</td>
                        <td style={{ display: 'flex', gap: '.4rem' }}>
                          <button
                            className="btn-outline"
                            style={{ fontSize: '.78rem', padding: '.25rem .6rem' }}
                            onClick={() => toggleExpand(u.id)}
                          >
                            {expandedUser === u.id ? '▲ Hide' : '▼ Predictions'}
                          </button>
                          <button
                            className="btn-danger-sm"
                            onClick={() => handleDeleteUser(u.id)}
                            disabled={deleting === u.id}
                          >
                            {deleting === u.id ? '...' : 'Delete'}
                          </button>
                        </td>
                      </tr>
                      {expandedUser === u.id && (
                        <UserPredictions
                          userId={u.id}
                          onCountChange={setter => setPredCounts(c => ({ ...c, [u.id]: setter(c[u.id] ?? 0) }))}
                          onView={setViewingPrediction}
                        />
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            </div>
            {pages > 1 && (
              <div className="pagination">
                <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="btn-outline">
                  ← Prev
                </button>
                <span>Page {page} of {pages}</span>
                <button disabled={page >= pages} onClick={() => setPage(p => p + 1)} className="btn-outline">
                  Next →
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
