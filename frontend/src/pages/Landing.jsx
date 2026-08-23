import { Link } from 'react-router-dom'

const FEATURES = [
  { icon: '🔮', title: 'AI-Powered Predictions', desc: 'Our ensemble ML model predicts your monthly electricity bill before it arrives, trained on 40,000+ real household records.' },
  { icon: '🌤️', title: 'Weather-Aware', desc: 'Integrates live weather data — temperature, humidity, precipitation — because Sri Lanka\'s climate directly drives your electricity usage.' },
  { icon: '💡', title: 'Smart Recommendations', desc: 'Get personalised tips on which appliances to reduce and how much you could save in LKR on your next bill.' },
  { icon: '📊', title: 'Track Your History', desc: 'Log actual bills against predictions, see accuracy over time, and spot trends in your household energy usage.' },
]

const STATS = [
  { value: 'AI', label: 'Powered Predictions', sub: 'Built on real machine learning — not just a formula' },
  { value: '40K+', label: 'Real Households', sub: 'Trained on actual CEB electricity records' },
  { value: 'Live', label: 'Weather Integration', sub: 'Real-time conditions factored into every prediction' },
  { value: '8+', label: 'Districts Covered', sub: 'Colombo areas now — expanding island-wide' },
]

const WHY = [
  { icon: '⚡', title: 'Rising Tariffs', desc: 'Sri Lanka\'s CEB electricity tariffs have multiple progressive slabs — a small increase in usage can push you into a much higher billing tier.' },
  { icon: '🏠', title: 'Hidden Usage', desc: 'Most households don\'t realise how much air conditioners, water heaters, and fridges contribute to their bill until it\'s too late.' },
  { icon: '🌿', title: 'Environmental Impact', desc: 'Reducing household consumption directly lowers demand on the national grid, cutting carbon emissions and supporting a greener Sri Lanka.' },
]

// Replace these YouTube video IDs with actual energy-saving videos of your choice
const VIDEOS = [
  { id: 'mnZ_uG57xYI', title: 'How to Reduce Your Electricity Bill at Home' },
  { id: 'E-etG2PcUHA', title: 'Understanding Your Electricity Tariff' },
]

export default function Landing() {
  return (
    <div style={{ fontFamily: "'Inter', sans-serif", color: '#1e293b', overflowX: 'hidden' }}>

      {/* ── NAV ─────────────────────────────────────── */}
      <nav style={{
        position: 'sticky', top: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 2rem', height: '64px',
        background: 'rgba(15,30,55,0.92)', backdropFilter: 'blur(10px)',
        boxShadow: '0 2px 20px rgba(0,0,0,0.3)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '.6rem' }}>
          <span style={{ fontSize: '1.6rem' }}>⚡</span>
          <span style={{ color: '#fff', fontWeight: 800, fontSize: '1.25rem', letterSpacing: '-.5px' }}>EnergyWise</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <Link to="/register" style={{
            color: 'rgba(255,255,255,0.8)', textDecoration: 'none',
            fontSize: '.9rem', padding: '.4rem .9rem', borderRadius: '6px',
            transition: 'color .15s',
          }}>Create Account</Link>
          <Link to="/login" style={{
            background: '#2563eb', color: '#fff', textDecoration: 'none',
            padding: '.45rem 1.2rem', borderRadius: '8px', fontWeight: 600,
            fontSize: '.9rem', boxShadow: '0 2px 8px rgba(37,99,235,0.4)',
          }}>Sign In</Link>
        </div>
      </nav>

      {/* ── HERO ─────────────────────────────────────── */}
      <section style={{
        minHeight: '92vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'linear-gradient(135deg, #0f1e37 0%, #0f766e 60%, #1e3a5f 100%)',
        padding: '4rem 2rem', textAlign: 'center', position: 'relative', overflow: 'hidden',
      }}>
        {/* decorative circles */}
        {[
          { size: 500, top: '-150px', right: '-150px', opacity: 0.06 },
          { size: 300, bottom: '-80px', left: '-80px', opacity: 0.08 },
        ].map((c, i) => (
          <div key={i} style={{
            position: 'absolute', width: c.size, height: c.size, borderRadius: '50%',
            background: '#fff', opacity: c.opacity,
            top: c.top, right: c.right, bottom: c.bottom, left: c.left,
            pointerEvents: 'none',
          }} />
        ))}

        <div style={{ maxWidth: '780px', position: 'relative' }}>
          <div style={{
            display: 'inline-block', background: 'rgba(16,185,129,0.18)',
            color: '#34d399', border: '1px solid rgba(52,211,153,0.3)',
            padding: '.35rem 1rem', borderRadius: '999px', fontSize: '.82rem',
            fontWeight: 600, letterSpacing: '.5px', marginBottom: '1.75rem',
          }}>
            AI-POWERED ELECTRICITY BILL PREDICTOR — COLOMBO
          </div>

          <h1 style={{
            color: '#fff', fontSize: 'clamp(2.4rem, 6vw, 3.8rem)',
            fontWeight: 800, lineHeight: 1.1, marginBottom: '1.25rem', letterSpacing: '-1px',
          }}>
            Know Your Bill<br />
            <span style={{ color: '#34d399' }}>Before It Arrives</span>
          </h1>

          <p style={{
            color: 'rgba(255,255,255,0.72)', fontSize: 'clamp(1rem, 2.5vw, 1.2rem)',
            lineHeight: 1.7, marginBottom: '2.5rem', maxWidth: '600px', margin: '0 auto 2.5rem',
          }}>
            EnergyWise uses machine learning trained on real CEB household data to predict your
            monthly electricity bill — and tell you exactly how to reduce it.
          </p>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/register" style={{
              background: '#2563eb', color: '#fff', textDecoration: 'none',
              padding: '.9rem 2.2rem', borderRadius: '10px', fontWeight: 700,
              fontSize: '1.05rem', boxShadow: '0 4px 20px rgba(37,99,235,0.5)',
              transition: 'transform .15s',
            }}>Get Started Free →</Link>
            <Link to="/login" style={{
              background: 'rgba(255,255,255,0.1)', color: '#fff', textDecoration: 'none',
              padding: '.9rem 2.2rem', borderRadius: '10px', fontWeight: 600,
              fontSize: '1.05rem', border: '1px solid rgba(255,255,255,0.25)',
            }}>Sign In</Link>
          </div>

          {/* hero feature pills */}
          <div style={{ marginTop: '3rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            {[
              { icon: '🤖', text: 'AI-Powered' },
              { icon: '🌤️', text: 'Live Weather Data' },
              { icon: '💡', text: 'Personalised Tips' },
              { icon: '📊', text: 'Track Your Bills' },
            ].map((p, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '.5rem',
                background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.18)',
                borderRadius: '999px', padding: '.45rem 1.1rem', color: '#fff',
                fontSize: '.9rem', fontWeight: 500,
              }}>
                <span>{p.icon}</span> {p.text}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── STATS ─────────────────────────────────────── */}
      <section style={{ background: '#1e3a5f', padding: '3.5rem 2rem' }}>
        <div style={{
          maxWidth: '1100px', margin: '0 auto',
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px,1fr))', gap: '2rem',
        }}>
          {STATS.map((s, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{ color: '#34d399', fontSize: '2.4rem', fontWeight: 800, letterSpacing: '-1px' }}>{s.value}</div>
              <div style={{ color: '#fff', fontWeight: 600, marginTop: '.3rem', fontSize: '1rem' }}>{s.label}</div>
              <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '.82rem', marginTop: '.2rem' }}>{s.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── IMAGE GALLERY ────────────────────────────── */}
      <section style={{ padding: '5rem 2rem', background: '#fff' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ fontSize: 'clamp(1.8rem,4vw,2.6rem)', fontWeight: 800, letterSpacing: '-0.5px' }}>
              The Reality of Rising Energy Costs
            </h2>
            <p style={{ color: '#64748b', marginTop: '.75rem', fontSize: '1.05rem', maxWidth: '560px', margin: '.75rem auto 0' }}>
              Millions of households across Sri Lanka struggle with unpredictable electricity bills every month.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: 'auto auto', gap: '1rem' }}>
            <div style={{ gridRow: '1 / 3', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
              <img src="/images/img3.jpg" alt="Power transmission towers at sunset"
                style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
            </div>
            <div style={{ borderRadius: '16px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
              <img src="/images/img1.jpg" alt="Stressed household over rising electricity bill"
                style={{ width: '100%', height: '260px', objectFit: 'cover', display: 'block' }} />
            </div>
            <div style={{ borderRadius: '16px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
              <img src="/images/img2.jpg" alt="Reading an electricity meter"
                style={{ width: '100%', height: '260px', objectFit: 'cover', display: 'block' }} />
            </div>
          </div>
        </div>
      </section>

      {/* ── WHY IT MATTERS ──────────────────────────── */}
      <section style={{ padding: '5rem 2rem', background: '#f8fafc' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ fontSize: 'clamp(1.8rem,4vw,2.6rem)', fontWeight: 800, letterSpacing: '-0.5px' }}>
              Why Energy Awareness Matters
            </h2>
            <p style={{ color: '#64748b', marginTop: '.75rem', fontSize: '1.05rem', maxWidth: '560px', margin: '.75rem auto 0' }}>
              Electricity bills in Sri Lanka can be unpredictable. Understanding your usage is the first step to controlling it.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px,1fr))', gap: '1.5rem' }}>
            {WHY.map((w, i) => (
              <div key={i} style={{
                background: '#fff', borderRadius: '14px', padding: '2rem',
                boxShadow: '0 2px 16px rgba(0,0,0,0.07)',
                borderTop: '4px solid #2563eb',
              }}>
                <div style={{ fontSize: '2.2rem', marginBottom: '1rem' }}>{w.icon}</div>
                <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '.6rem' }}>{w.title}</h3>
                <p style={{ color: '#64748b', lineHeight: 1.7, fontSize: '.92rem' }}>{w.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES ─────────────────────────────────── */}
      <section style={{ padding: '5rem 2rem', background: '#fff' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ fontSize: 'clamp(1.8rem,4vw,2.6rem)', fontWeight: 800, letterSpacing: '-0.5px' }}>
              What EnergyWise Does
            </h2>
            <p style={{ color: '#64748b', marginTop: '.75rem', fontSize: '1.05rem' }}>
              More than a calculator — a complete household energy intelligence tool.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px,1fr))', gap: '1.5rem' }}>
            {FEATURES.map((f, i) => (
              <div key={i} style={{
                background: '#f8fafc', borderRadius: '14px', padding: '2rem',
                border: '1px solid #e2e8f0', transition: 'transform .2s, box-shadow .2s',
              }}>
                <div style={{
                  width: '52px', height: '52px', borderRadius: '12px',
                  background: 'linear-gradient(135deg,#2563eb,#0f766e)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1.5rem', marginBottom: '1.2rem',
                }}>{f.icon}</div>
                <h3 style={{ fontWeight: 700, fontSize: '1.05rem', marginBottom: '.6rem' }}>{f.title}</h3>
                <p style={{ color: '#64748b', lineHeight: 1.7, fontSize: '.9rem' }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── VIDEOS ───────────────────────────────────── */}
      <section style={{ padding: '5rem 2rem', background: '#f0f4f8' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2 style={{ fontSize: 'clamp(1.8rem,4vw,2.6rem)', fontWeight: 800, letterSpacing: '-0.5px' }}>
              Learn to Save Energy
            </h2>
            <p style={{ color: '#64748b', marginTop: '.75rem', fontSize: '1.05rem' }}>
              Small changes at home make a big difference on your bill and the environment.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px,1fr))', gap: '2rem' }}>
            {VIDEOS.map((v, i) => (
              <div key={i} style={{ borderRadius: '14px', overflow: 'hidden', boxShadow: '0 4px 20px rgba(0,0,0,0.12)' }}>
                <div style={{ position: 'relative', paddingBottom: '56.25%', background: '#000' }}>
                  <iframe
                    src={`https://www.youtube.com/embed/${v.id}`}
                    title={v.title}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                  />
                </div>
                <div style={{ background: '#fff', padding: '1rem 1.25rem' }}>
                  <p style={{ fontWeight: 600, fontSize: '.95rem' }}>{v.title}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────── */}
      <section style={{
        padding: '5rem 2rem', textAlign: 'center',
        background: 'linear-gradient(135deg, #1e3a5f 0%, #0f766e 100%)',
      }}>
        <h2 style={{ color: '#fff', fontSize: 'clamp(1.8rem,4vw,2.8rem)', fontWeight: 800, letterSpacing: '-0.5px', marginBottom: '1rem' }}>
          Take Control of Your Energy Bill
        </h2>
        <p style={{ color: 'rgba(255,255,255,0.72)', fontSize: '1.1rem', marginBottom: '2.5rem', maxWidth: '520px', margin: '0 auto 2.5rem' }}>
          Join households across Colombo who are already predicting and reducing their electricity costs.
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/register" style={{
            background: '#fff', color: '#1e3a5f', textDecoration: 'none',
            padding: '.9rem 2.4rem', borderRadius: '10px', fontWeight: 700, fontSize: '1.05rem',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
          }}>Create Free Account</Link>
          <Link to="/login" style={{
            background: 'transparent', color: '#fff', textDecoration: 'none',
            padding: '.9rem 2.4rem', borderRadius: '10px', fontWeight: 600, fontSize: '1.05rem',
            border: '2px solid rgba(255,255,255,0.4)',
          }}>Sign In</Link>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────── */}
      <footer style={{
        background: '#0f1e37', color: 'rgba(255,255,255,0.45)',
        textAlign: 'center', padding: '1.75rem 2rem', fontSize: '.85rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '.5rem', marginBottom: '.5rem' }}>
          <span>⚡</span>
          <span style={{ color: '#fff', fontWeight: 700 }}>EnergyWise</span>
        </div>
        © {new Date().getFullYear()} EnergyWise · Cardiff Metropolitan University Final Project
      </footer>

    </div>
  )
}
