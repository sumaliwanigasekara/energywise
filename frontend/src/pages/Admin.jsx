import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../services/api'

const RISK_COLORS = { Low: '#10b981', Medium: '#f59e0b', High: '#ef4444' }

export default function Admin() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)

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
    } catch {
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData(page) }, [page])

  const handleDelete = async userId => {
    if (!window.confirm('Delete this user and all their data?')) return
    setDeleting(userId)
    try {
      await api.delete(`/admin/users/${userId}`)
      setUsers(u => u.filter(x => x.id !== userId))
      setTotal(t => t - 1)
    } catch (err) {
      alert(err.response?.data?.error || 'Delete failed.')
    } finally {
      setDeleting(null)
    }
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

      {loading ? (
        <div className="loading-box">Loading...</div>
      ) : (
        <>
          {/* Stats Cards */}
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
            </div>
          )}

          {/* Risk Distribution Chart */}
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

          {/* Users Table */}
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
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td><strong>{u.name}</strong></td>
                      <td>{u.email}</td>
                      <td>{u.district}</td>
                      <td>{u.prediction_count}</td>
                      <td>{new Date(u.created_at).toLocaleDateString('en-GB')}</td>
                      <td>
                        <button
                          className="btn-danger-sm"
                          onClick={() => handleDelete(u.id)}
                          disabled={deleting === u.id}
                        >
                          {deleting === u.id ? '...' : 'Delete'}
                        </button>
                      </td>
                    </tr>
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
