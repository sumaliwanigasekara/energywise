# EnergyWise

AI-powered electricity bill prediction web application for households in the Colombo District, Sri Lanka.

## Overview

EnergyWise helps consumers predict their monthly electricity bill before it arrives. Users enter their appliance usage and past bills, and the system uses a trained Random Forest model to estimate consumption (kWh) and cost (LKR) based on the PUCSL 2026 CEB tariff structure.

### Key Features

- Monthly electricity bill and kWh prediction
- Appliance-based usage profile (fans, ACs, washing machine, water heater, etc.)
- Multiple AC support with individual tonnage and daily hours
- Weather-adjusted predictions using Open-Meteo API (Colombo temperature data)
- Risk level classification based on CEB tariff schedules
- Bill history with actual vs predicted tracking
- Energy-saving recommendations
- Admin dashboard for user management
- JWT-based authentication

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite 5, React Router 6, Recharts |
| Backend | Flask, Flask-JWT-Extended, Flask-SQLAlchemy |
| Database | MySQL 8.0 |
| ML Model | Random Forest Regressor (R² = 0.886) |
| Deployment | Docker, Docker Compose, Nginx |

## CEB Tariff Structure (PUCSL 2026)

| Schedule | Consumption | Risk Level |
|----------|------------|------------|
| Schedule 1 | 0 – 60 kWh | Low |
| Schedule 2 | 61 – 180 kWh | Medium |
| Schedule 3 | Above 180 kWh | High |

## Project Structure

```
energywise_git/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── routes/          # Flask API routes
│   │   └── services/        # Weather, tariff, ML services
│   ├── ml/
│   │   └── model.pkl        # Trained Random Forest model (not in git)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # Dashboard, Appliances, Predict, Admin
│   │   └── components/      # Navbar, RiskExplanation
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml       # Local development
├── docker-compose.prod.yml  # Production (uses Docker Hub images)
└── .env                     # Environment variables (not in git)
```

## Running Locally

### Option 1 — Docker (Recommended)

**Requirements:** Docker Desktop

```bash
# Clone the repository
git clone https://github.com/sumaliwanigasekara/energywise.git
cd energywise

# Add the missing files (not in git):
# - backend/ml/model.pkl
# - .env (see Environment Variables section)

# Start all services
docker-compose up --build
```

Open `http://localhost:8080`

### Option 2 — Manual (Two Terminals)

**Requirements:** Python 3.11+, Node.js 20+, MySQL 8.0

**Terminal 1 — Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run.py
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=mysql+pymysql://root:root@localhost/energywise
JWT_SECRET_KEY=your-secret-key-here
ADMIN_EMAIL=admin@energywise.lk
ADMIN_PASSWORD=Admin@123
DB_ROOT_PASSWORD=root
```

## ML Model

The Random Forest model is trained on historical electricity consumption data for the Colombo District. It is not included in the repository due to file size (105 MB).

**Features used:**
- Appliance usage hours (fan, AC, washing machine, water heater)
- AC tonnage and count
- Number of household members
- Previous 3 months' bills
- Average monthly temperature (Colombo)

**To retrain the model**, run the notebook:
```
backend/ml/pipeline.ipynb
```

## Docker Hub Images

Pre-built images (with model included) are available on Docker Hub:

```
sumaliw/energywise-backend
sumaliw/energywise-frontend
```

### Deploy using pre-built images

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Open `http://localhost:8080`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login |
| GET/PUT | `/api/appliances` | Get/save appliance profile |
| POST | `/api/predict` | Run bill prediction |
| GET | `/api/predictions` | Get prediction history |
| PATCH | `/api/predictions/<id>/actual` | Save actual bill |
| DELETE | `/api/predictions/<id>` | Delete prediction |
| GET | `/api/predictions/autofill` | Auto-fill past bills |
| GET | `/api/admin/users` | List all users (admin only) |

## Default Admin Account

```
Email:    admin@energywise.lk
Password: Admin@123
```

---

Developed for ICBT Campus — Final Year Project
