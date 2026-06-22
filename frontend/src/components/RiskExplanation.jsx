const TIERS = [
  {
    level: 'Low',
    range: '0 – 60 kWh',
    schedule: 'Schedule 1',
    color: '#10b981',
    bg: '#d1fae5',
    description: 'Cheapest CEB tariff. Unit rates are low and there is no high fixed charge.',
  },
  {
    level: 'Medium',
    range: '61 – 180 kWh',
    schedule: 'Schedule 2',
    color: '#f59e0b',
    bg: '#fef3c7',
    description: 'Mid-tier CEB tariff. Higher unit rates apply and a fixed charge is added at 90 and 120 kWh thresholds.',
  },
  {
    level: 'High',
    range: 'Above 180 kWh',
    schedule: 'Schedule 3',
    color: '#ef4444',
    bg: '#fee2e2',
    description: 'Most expensive CEB tariff. All 180+ units are billed at LKR 100/unit and a LKR 2,500 fixed charge is added. A single extra unit above 180 kWh significantly raises your entire bill.',
  },
]

export default function RiskExplanation({ currentLevel, predictedUnits }) {
  return (
    <div className="risk-explanation">
      <h4 className="risk-exp-title">📊 What does your risk level mean?</h4>
      <p className="risk-exp-sub">
        EnergyWise uses the PUCSL 2026 CEB tariff schedules to classify risk.
        Your predicted usage of <strong>{predictedUnits} kWh</strong> places you in the{' '}
        <strong>{currentLevel} Risk</strong> category.
      </p>
      <div className="risk-tier-list">
        {TIERS.map(t => {
          const active = t.level === currentLevel
          return (
            <div
              key={t.level}
              className={`risk-tier ${active ? 'risk-tier-active' : ''}`}
              style={active ? { borderColor: t.color, background: t.bg } : {}}
            >
              <div className="risk-tier-header">
                <span className={`badge badge-${t.level.toLowerCase()}`}>{t.level} Risk</span>
                <span className="risk-tier-range">{t.range}</span>
                <span className="risk-tier-schedule">{t.schedule}</span>
                {active && <span className="risk-tier-you">← You are here</span>}
              </div>
              <p className="risk-tier-desc">{t.description}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
