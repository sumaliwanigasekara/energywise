import { Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function AdminLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <>
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="brand-icon">⚡</span>
          <span className="brand-name">EnergyWise</span>
          <span style={{ marginLeft: '0.75rem', fontSize: '0.75rem', background: '#2563eb', color: '#fff', padding: '2px 10px', borderRadius: '999px', fontWeight: 600 }}>
            Admin
          </span>
        </div>
        <div className="navbar-user">
          <span className="user-name">👤 {user?.name}</span>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </>
  )
}
