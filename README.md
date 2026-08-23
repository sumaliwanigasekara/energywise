# EnergyWise

AI-powered electricity bill prediction web application for Sri Lankan households. EnergyWise predicts your monthly CEB electricity bill before it arrives, using machine learning trained on over 40,000 real household records, live weather data, and appliance usage patterns.

**Live App:** https://tinyurl.com/energywiseapp

---

## Features

- **Bill Prediction** — Predict your monthly electricity bill based on your appliances, usage habits, and district
- **Live Weather Integration** — Real-time weather conditions fetched and factored into every prediction
- **Tariff Breakdown** — CEB tariff schedule applied tier-by-tier with a full cost breakdown
- **Consumption Badge** — Instant Low / Moderate / High classification with money-saving tips
- **Prediction History** — Track predictions over time and monitor trends
- **Password Reset** — Secure email-based forgot password / reset flow
- **Admin Dashboard** — View all users, predictions, and accuracy metrics
- **Security** — Change password with current password verification

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, React Router, Vite |
| Backend | Python 3, Flask, Flask-JWT-Extended |
| Database | MySQL 8 (via Flask-SQLAlchemy + PyMySQL) |
| ML Model | Ensemble (VotingRegressor: Random Forest + XGBoost) |
| Weather API | Open-Meteo (free, no key required) |
| Email | Flask-Mail + Gmail SMTP |
| Deployment | Docker Compose, Oracle Cloud (Always Free) |

---

## ML Model

The prediction model is an ensemble of Random Forest and XGBoost regressors trained on CEB household electricity data.

| Model | R² | MAE |
|---|---|---|
| Default Random Forest | 0.8837 | 18.61 |
| Tuned Random Forest | 0.8837 | 18.61 |
| Default XGBoost | 0.8815 | 18.97 |
| Tuned XGBoost | 0.8838 | 18.37 |
| **Ensemble (RF + XGB)** | **0.8862** | **18.39** |

---

## Project Structure

```
energywise/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models (User, Prediction, Bill, …)
│   │   ├── routes/          # Flask blueprints (auth, predict, admin, …)
│   │   └── services/        # Business logic (tariff, ML, weather)
│   ├── ml/                  # model.pkl
│   ├── tests/               # pytest unit tests
│   └── requirements.txt
├── frontend/
│   ├── public/images/       # Landing page images
│   └── src/
│       ├── pages/           # React pages (Landing, Dashboard, Predict, …)
│       ├── components/      # Navbar, ProtectedRoute
│       └── services/        # Axios API client
├── docker-compose.yml
└── EnergyWise_Pipeline.ipynb
```

---

## Running Locally

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend dev)

### 1. Clone the repo
```bash
git clone https://github.com/sumaliwanigasekara/energywise.git
cd energywise
```

### 2. Create `.env` in the project root
```env
DB_HOST=db
DB_PORT=3306
DB_NAME=energywise
DB_USER=energywise
DB_PASSWORD=your_db_password
JWT_SECRET_KEY=your_jwt_secret
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=adminpassword
MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

### 3. Start with Docker Compose
```bash
docker compose up --build -d
```

App is available at `http://localhost:8080`

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Test Coverage

| Test ID | Description |
|---|---|
| TAR-01 | Consumption level badge matches predicted kWh (8 boundary cases) |
| TAR-02 | Bill calculated correctly across all CEB tariff schedules (7 cases) |
| TAR-03 | Negative unit inputs handled safely without crashing (3 cases) |
| TAR-04 | Tier label boundaries match PUCSL 2026 schedule exactly (8 cases) |

---

## Deployment

The app runs on an Oracle Cloud VM.Standard.E2.1.Micro (Always Free) instance using Docker Compose with a MySQL container and a Gunicorn-served Flask backend behind a React frontend served by Nginx.

To deploy updates:
```bash
cd energywise
git pull
docker compose up --build -d
```
