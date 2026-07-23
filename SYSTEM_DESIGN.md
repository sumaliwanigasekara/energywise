# EnergyWise — System Design Document

> Paste any PlantUML block into [planttext.com](https://planttext.com) or the PlantUML VS Code extension to render the diagram.

---

## 1. System Overview

**EnergyWise** is a web-based household electricity forecasting application built for Sri Lankan consumers. Users register an account, enter their appliance profile and previous bills, and the system runs a trained machine learning model to predict the month's electricity consumption (kWh) and estimated CEB bill (LKR). The prediction engine accounts for appliance usage patterns, household size, district-level weather, and the PUCSL-approved CEB tariff structure. Personalised recommendations are generated to help users reduce their bill. An administrator role provides system-level monitoring of all users and predictions.

### Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Router, Axios |
| Backend | Python 3, Flask, Flask-JWT-Extended, SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy ORM |
| ML Engine | scikit-learn (trained model serialised as `model.pkl`) |
| Weather API | Open-Meteo Archive API (30-day historical averages) |
| Containerisation | Docker, Docker Compose |
| Production Serving | Nginx (frontend), Gunicorn (backend) |

---

## 2. Actors

| Actor | Description |
|---|---|
| **Consumer** | A registered household user. Manages appliances, bills, and runs predictions. |
| **Administrator** | A privileged user (`role = admin`). Monitors system statistics and manages users. |
| **ML Model** | Internal actor. The trained scikit-learn model that produces predicted kWh. |
| **Weather API** | External actor. Open-Meteo archive API that supplies 30-day weather averages. |
| **CEB Tariff Engine** | Internal actor. Calculates LKR bill from predicted kWh using PUCSL tariff schedules. |

---

## 3. Use Case Diagram

```plantuml
@startuml EnergyWise_UseCases

left to right direction
skinparam packageStyle rectangle

actor Consumer
actor Administrator
actor "Weather API" as WeatherAPI
actor "ML Model" as MLModel
actor "CEB Tariff Engine" as Tariff

rectangle "EnergyWise System" {

  ' ── Authentication ──────────────────────────────
  usecase "Register Account"         as UC_Register
  usecase "Login"                    as UC_Login
  usecase "View Profile"             as UC_Profile

  ' ── Appliance Management ────────────────────────
  usecase "View Appliance Profile"   as UC_AppView
  usecase "Create Appliance Profile" as UC_AppCreate
  usecase "Update Appliance Profile" as UC_AppUpdate

  ' ── Bill Management ─────────────────────────────
  usecase "Add Bill Record"          as UC_BillAdd
  usecase "View Bill History"        as UC_BillView
  usecase "Edit Bill Record"         as UC_BillEdit
  usecase "Delete Bill Record"       as UC_BillDel

  ' ── Prediction ──────────────────────────────────
  usecase "Run Energy Prediction"    as UC_Predict
  usecase "View Prediction Results"  as UC_PredResult
  usecase "View Prediction History"  as UC_PredHistory
  usecase "Enter Actual Units"       as UC_Actual
  usecase "Delete Prediction"        as UC_PredDel
  usecase "Auto-fill Previous Bills" as UC_Autofill

  ' ── Internal sub-flows ──────────────────────────
  usecase "Fetch Weather Data"       as UC_Weather
  usecase "Compute ML Prediction"    as UC_ML
  usecase "Calculate Tariff & Risk"  as UC_Tariff
  usecase "Generate Recommendations" as UC_Recs

  ' ── Admin ───────────────────────────────────────
  usecase "View System Statistics"   as UC_Stats
  usecase "View All Users"           as UC_Users
  usecase "Delete User"              as UC_DelUser
  usecase "View All Predictions"     as UC_AllPred
}

' Consumer associations
Consumer --> UC_Register
Consumer --> UC_Login
Consumer --> UC_Profile
Consumer --> UC_AppView
Consumer --> UC_AppCreate
Consumer --> UC_AppUpdate
Consumer --> UC_BillAdd
Consumer --> UC_BillView
Consumer --> UC_BillEdit
Consumer --> UC_BillDel
Consumer --> UC_Predict
Consumer --> UC_PredResult
Consumer --> UC_PredHistory
Consumer --> UC_Actual
Consumer --> UC_PredDel
Consumer --> UC_Autofill

' Admin associations
Administrator --> UC_Login
Administrator --> UC_Stats
Administrator --> UC_Users
Administrator --> UC_DelUser
Administrator --> UC_AllPred

' Prediction includes sub-flows
UC_Predict ..> UC_Weather    : <<include>>
UC_Predict ..> UC_ML         : <<include>>
UC_Predict ..> UC_Tariff     : <<include>>
UC_Predict ..> UC_Recs       : <<include>>

' External actor connections
UC_Weather --> WeatherAPI
UC_ML      --> MLModel
UC_Tariff  --> Tariff

@enduml
```

---

## 4. Use Case Descriptions

### UC-01 — Register Account
| Field | Detail |
|---|---|
| **Actor** | Consumer |
| **Precondition** | User does not have an account |
| **Main Flow** | User submits name, email, password, district → System validates → Creates User record → Returns JWT token |
| **Alternative** | Email already registered → System returns 409 Conflict |
| **Postcondition** | User is logged in with a JWT token |

### UC-02 — Login
| Field | Detail |
|---|---|
| **Actor** | Consumer, Administrator |
| **Precondition** | Account exists |
| **Main Flow** | User submits email and password → System verifies bcrypt hash → Returns JWT token and user object |
| **Alternative** | Wrong credentials → 401 Unauthorised |

### UC-03 — Create / Update Appliance Profile
| Field | Detail |
|---|---|
| **Actor** | Consumer |
| **Precondition** | Logged in |
| **Main Flow** | User enters fan count/hours, AC units (individual tons + hours/day), fridge count, washer/heater/other hours → System aggregates AC fields → Saves `UserAppliances` record |
| **Business Rule** | One profile per user (POST creates, PUT updates). AC aggregation: weighted average tons, average hours across individual AC units. |

### UC-04 — Add / Edit / Delete Bill Record
| Field | Detail |
|---|---|
| **Actor** | Consumer |
| **Precondition** | Logged in |
| **Main Flow** | User enters month, year, amount (LKR), optional units (kWh) and notes → Saved to `bills` table |
| **Purpose** | Historical reference; previous bill amounts are used as ML features in the prediction |

### UC-05 — Run Energy Prediction
| Field | Detail |
|---|---|
| **Actor** | Consumer |
| **Precondition** | Logged in; appliance profile preferred but not required |
| **Main Flow** | 1. User submits form (members, prev_bill_1/2/3, appliance overrides, district). 2. System fetches 30-day weather averages from Open-Meteo API for the district. 3. System builds the 21-feature ML input vector. 4. ML model returns predicted kWh. 5. TariffService converts kWh → LKR using PUCSL schedule (Low/Mid/High). 6. Risk level determined (Low ≤60 kWh, Medium ≤180 kWh, High >180 kWh). 7. Recommendations generated. 8. `Prediction` record saved to DB. 9. Response returned to client. |
| **Postcondition** | Prediction stored; user sees kWh, LKR, risk, appliance breakdown, and ranked recommendations |

### UC-06 — Enter Actual Units
| Field | Detail |
|---|---|
| **Actor** | Consumer |
| **Precondition** | Prediction exists; billing period has ended |
| **Main Flow** | User enters actual kWh from CEB bill → System stores `actual_units` and `actual_bill` on the Prediction record |
| **Purpose** | Enables prediction accuracy tracking in the admin dashboard |

### UC-07 — Auto-fill Previous Bills
| Field | Detail |
|---|---|
| **Actor** | Consumer |
| **Precondition** | At least one prior prediction exists |
| **Main Flow** | System reads the most recent prediction, populates prev_bill_1 (actual if entered, else predicted), prev_bill_2, prev_bill_3 from that prediction's inputs |

### UC-08 — View System Statistics (Admin)
| Field | Detail |
|---|---|
| **Actor** | Administrator |
| **Precondition** | Logged in as admin |
| **Main Flow** | Admin views: total consumers, total predictions, average predicted bill, average predicted units, risk level distribution, prediction accuracy % (only for predictions with actual_units entered) |

### UC-09 — View / Delete Users (Admin)
| Field | Detail |
|---|---|
| **Actor** | Administrator |
| **Main Flow** | Paginated list of consumers with prediction count per user; admin can permanently delete a user (cascades to their predictions, bills, appliance profile) |
| **Guard** | Admin accounts cannot be deleted |

---

## 5. Class Diagram

```plantuml
@startuml EnergyWise_ClassDiagram

skinparam classAttributeIconSize 0

' ── Domain Models ───────────────────────────────────────────────────────────

class User {
  +id : Integer <<PK>>
  +name : String(100)
  +email : String(150) <<unique>>
  +password_hash : String(255)
  +role : Enum["user","admin"]
  +district : String(100)
  +created_at : DateTime
  --
  +__init__(name, email, password, role, district)
  +check_password(password) : bool
  +to_dict() : dict
}

class UserAppliances {
  +id : Integer <<PK>>
  +user_id : Integer <<FK→users.id, unique>>
  +fan_count : Integer
  +fan_hours_per_month : Float
  +ac_count : Integer
  +ac_hours_per_month : Float
  +ac_tons : Float
  +ac_units : JSON
  +fridge_count : Integer
  +washer_hours_per_month : Float
  +heater_hours_per_month : Float
  +other_hours_per_month : Float
  +updated_at : DateTime
  --
  +to_dict() : dict
}

class Bill {
  +id : Integer <<PK>>
  +user_id : Integer <<FK→users.id>>
  +month : Integer
  +year : Integer
  +units : Float
  +amount : Float
  +notes : Text
  +created_at : DateTime
  --
  +to_dict() : dict
}

class Prediction {
  +id : Integer <<PK>>
  +user_id : Integer <<FK→users.id>>
  +members : Integer
  +district : String(100)
  +prev_bill_1 : Float
  +prev_bill_2 : Float
  +prev_bill_3 : Float
  +fan_count : Integer
  +ac_count : Integer
  +ac_hours_per_month : Float
  +ac_tons : Float
  +fridge_count : Integer
  +washer_hours_per_month : Float
  +heater_hours_per_month : Float
  +other_hours_per_month : Float
  +avg_temp : Float
  +avg_humidity : Float
  +total_precip : Float
  +avg_wind : Float
  +start_date : DateTime
  +end_date : DateTime
  +predicted_units : Float
  +predicted_bill : Float
  +risk_level : String(20)
  +recommendations : JSON
  +appliance_breakdown : JSON
  +actual_units : Float
  +actual_bill : Float
  +created_at : DateTime
  --
  +to_dict() : dict
}

' ── Service Classes ─────────────────────────────────────────────────────────

class MLService {
  -_model : sklearn.Estimator
  -_FEATURE_COLS : List[str]
  --
  +predict(payload: dict) : dict
  -_appliance_breakdown(data, total_units) : dict
  -_generate_recommendations(data, units, bill) : List[dict]
}

class TariffService {
  +TIERS_LOW : List[dict]
  +TIERS_MID : List[dict]
  +TIERS_HIGH : List[dict]
  --
  +calculate_bill(units: float) : float
  +get_risk_level(units: float) : str
  +get_tier_label(units: float) : str
  -{static}_apply_tiers(units, tiers) : float
}

class WeatherService {
  +DISTRICT_COORDS : dict
  +FALLBACK : dict
  --
  +get_weather(district: str) : dict
}

' ── Route Controllers ────────────────────────────────────────────────────────

class AuthController <<Blueprint>> {
  +register() : Response
  +login() : Response
  +me() : Response
}

class AppliancesController <<Blueprint>> {
  +appliances() : Response  [GET/POST/PUT]
  -{static}_aggregate_ac(ac_units) : dict
}

class BillsController <<Blueprint>> {
  +get_bills() : Response
  +add_bill() : Response
  +update_bill(bill_id) : Response
  +delete_bill(bill_id) : Response
}

class PredictController <<Blueprint>> {
  +predict() : Response
}

class HistoryController <<Blueprint>> {
  +get_predictions() : Response
  +get_prediction(prediction_id) : Response
  +delete_prediction(prediction_id) : Response
  +update_actual(prediction_id) : Response
  +autofill() : Response
}

class AdminController <<Blueprint>> {
  +stats() : Response
  +get_users() : Response
  +delete_user(user_id) : Response
  +get_all_predictions() : Response
  -{static}admin_required(fn) : decorator
}

' ── Relationships ────────────────────────────────────────────────────────────

User "1" --o "0..1" UserAppliances : has profile >
User "1" --o "0..*" Bill            : has bills >
User "1" --o "0..*" Prediction      : has predictions >

PredictController ..> MLService      : calls predict()
PredictController ..> WeatherService : calls get_weather()
MLService          ..> TariffService : calls calculate_bill()\ncalls get_risk_level()

AuthController     ..> User
AppliancesController ..> UserAppliances
BillsController    ..> Bill
HistoryController  ..> Prediction
AdminController    ..> User
AdminController    ..> Prediction

@enduml
```

---

## 6. Sequence Diagrams

### SD-01 — User Registration

```plantuml
@startuml SD_Register
title User Registration

actor Consumer
participant "React Frontend" as UI
participant "AuthController\n/api/auth/register" as Auth
participant "User Model" as UserModel
database "Database" as DB

Consumer -> UI : Fill name, email,\npassword, district
UI -> Auth : POST /api/auth/register\n{name, email, password, district}

Auth -> DB : SELECT * FROM users\nWHERE email = ?
DB --> Auth : result

alt Email already exists
  Auth --> UI : 409 Conflict\n{"error": "Email already registered"}
  UI --> Consumer : Show error message
else Email available
  Auth -> UserModel : new User(name, email, password, district)
  UserModel -> UserModel : bcrypt.hash(password)
  Auth -> DB : INSERT INTO users
  DB --> Auth : user record
  Auth -> Auth : create_access_token(user.id)
  Auth --> UI : 201 Created\n{"token": "...", "user": {...}}
  UI -> UI : Store token in AuthContext
  UI --> Consumer : Redirect to Dashboard
end

@enduml
```

---

### SD-02 — User Login

```plantuml
@startuml SD_Login
title User Login

actor Consumer
participant "React Frontend" as UI
participant "AuthController\n/api/auth/login" as Auth
participant "User Model" as UserModel
database "Database" as DB

Consumer -> UI : Enter email and password
UI -> Auth : POST /api/auth/login\n{email, password}

Auth -> DB : SELECT * FROM users WHERE email = ?
DB --> Auth : user record (or null)

alt User not found
  Auth --> UI : 401 Unauthorised\n{"error": "Invalid email or password"}
  UI --> Consumer : Show error
else User found
  Auth -> UserModel : check_password(password)
  UserModel -> UserModel : bcrypt.checkpw(password, hash)
  UserModel --> Auth : True / False

  alt Password incorrect
    Auth --> UI : 401 Unauthorised
    UI --> Consumer : Show error
  else Password correct
    Auth -> Auth : create_access_token(user.id)
    Auth --> UI : 200 OK\n{"token": "...", "user": {...}}
    UI -> UI : Store token + user in AuthContext
    UI --> Consumer : Redirect to Dashboard\n(or /admin if role=admin)
  end
end

@enduml
```

---

### SD-03 — Run Energy Prediction

```plantuml
@startuml SD_Predict
title Run Energy Prediction

actor Consumer
participant "React Frontend\nPredict.jsx" as UI
participant "PredictController\n/api/predict" as PredCtrl
participant "UserAppliances\nModel" as AppModel
participant "WeatherService" as WS
participant "Open-Meteo\nArchive API" as API
participant "MLService" as ML
participant "TariffService" as Tariff
database "Database" as DB

Consumer -> UI : Fill members, prev bills,\nappliance overrides, district
UI -> PredCtrl : POST /api/predict\n{members, prev_bill_1/2/3,\nappliance fields, district}\n[JWT in header]

PredCtrl -> PredCtrl : Verify JWT → get user_id

PredCtrl -> DB : SELECT appliance profile\nWHERE user_id = ?
DB --> PredCtrl : UserAppliances (fallback values)

PredCtrl -> WS : get_weather(district)
WS -> API : GET archive-api.open-meteo.com\n?lat=&lon=&start=&end=&daily=...
API --> WS : {temperature, humidity,\nprecipitation, wind}
WS -> WS : Compute 30-day averages
WS --> PredCtrl : {avg_temp, avg_humidity,\ntotal_precip, avg_wind,\nperiod_start, period_end}

PredCtrl -> PredCtrl : Build payload dict\n(merge request + profile + weather)

PredCtrl -> ML : predict(payload)
ML -> ML : Compute derived features:\navg_prev_bill, std, trend,\nac_kwh_est, total_load_est
ML -> ML : Build 21-feature DataFrame
ML -> ML : model.predict(features)
ML -> Tariff : calculate_bill(predicted_units)
Tariff -> Tariff : Select schedule (Low/Mid/High)\nApply progressive tier rates\n+ fixed charge
Tariff --> ML : predicted_bill (LKR)
ML -> Tariff : get_risk_level(predicted_units)
Tariff --> ML : "Low" / "Medium" / "High"
ML -> ML : _appliance_breakdown(payload, units)
ML -> ML : _generate_recommendations(payload, units, bill)
ML --> PredCtrl : {predicted_units, predicted_bill,\nrisk_level, recommendations,\nappliance_breakdown}

PredCtrl -> DB : INSERT INTO predictions\n(all inputs + weather + ML outputs)
DB --> PredCtrl : prediction.id

PredCtrl --> UI : 200 OK\n{prediction_id, predicted_units,\npredicted_bill, risk_level,\nrecommendations, appliance_breakdown, weather}

UI --> Consumer : Display result:\nkWh, LKR bill, risk badge,\nappliance pie chart,\nranked recommendations

@enduml
```

---

### SD-04 — Manage Appliance Profile (Create & Update)

```plantuml
@startuml SD_Appliances
title Manage Appliance Profile

actor Consumer
participant "React Frontend\nAppliances.jsx" as UI
participant "AppliancesController\n/api/appliances" as AppCtrl
database "Database" as DB

Consumer -> UI : Open Appliances page
UI -> AppCtrl : GET /api/appliances [JWT]
AppCtrl -> DB : SELECT * FROM user_appliances\nWHERE user_id = ?
DB --> AppCtrl : profile (or 404)
AppCtrl --> UI : profile data / 404
UI --> Consumer : Show form pre-filled\nwith saved values

Consumer -> UI : Edit values\n(fans, AC units, fridge, washer, heater)
UI -> AppCtrl : POST /api/appliances (first time)\nor PUT /api/appliances (update)\n{fan_count, ac_units:[{tons, hrs}...], ...}

AppCtrl -> AppCtrl : if ac_units list present:\n_aggregate_ac(ac_units)\n→ compute ac_count,\n  ac_hours_per_month,\n  ac_tons (weighted)

alt POST — create new profile
  AppCtrl -> DB : INSERT INTO user_appliances
  DB --> AppCtrl : saved profile
  AppCtrl --> UI : 201 Created {profile}
else PUT — update existing
  AppCtrl -> DB : UPDATE user_appliances\nSET ... WHERE user_id = ?
  DB --> AppCtrl : updated profile
  AppCtrl --> UI : 200 OK {profile}
end

UI --> Consumer : Show success toast

@enduml
```

---

### SD-05 — Bill Record Management

```plantuml
@startuml SD_Bills
title Bill Record Management

actor Consumer
participant "React Frontend\nDashboard.jsx" as UI
participant "BillsController\n/api/bills" as BillCtrl
database "Database" as DB

Consumer -> UI : Navigate to Bill History

UI -> BillCtrl : GET /api/bills [JWT]
BillCtrl -> DB : SELECT * FROM bills\nWHERE user_id = ?\nORDER BY year DESC, month DESC
DB --> BillCtrl : list of bills
BillCtrl --> UI : 200 OK {bills: [...]}
UI --> Consumer : Display bill list

Consumer -> UI : Click "Add Bill"
Consumer -> UI : Enter month, year, amount, units, notes
UI -> BillCtrl : POST /api/bills\n{month, year, amount, units, notes}
BillCtrl -> DB : INSERT INTO bills
DB --> BillCtrl : new bill record
BillCtrl --> UI : 201 Created {bill}
UI --> Consumer : Bill added to list

Consumer -> UI : Click Edit on a bill
Consumer -> UI : Change amount / units
UI -> BillCtrl : PUT /api/bills/{id}\n{month, year, amount, units, notes}
BillCtrl -> DB : UPDATE bills WHERE id=? AND user_id=?
DB --> BillCtrl : updated bill
BillCtrl --> UI : 200 OK {bill}

Consumer -> UI : Click Delete on a bill
UI -> BillCtrl : DELETE /api/bills/{id}
BillCtrl -> DB : DELETE FROM bills\nWHERE id=? AND user_id=?
DB --> BillCtrl : success
BillCtrl --> UI : 200 OK {message: "Bill deleted"}
UI --> Consumer : Bill removed from list

@enduml
```

---

### SD-06 — Enter Actual Units After Billing Period

```plantuml
@startuml SD_Actual
title Enter Actual Units (Post-billing Feedback)

actor Consumer
participant "React Frontend\nDashboard / History" as UI
participant "HistoryController\n/api/predictions/{id}/actual" as HistCtrl
participant "TariffService" as Tariff
database "Database" as DB

Consumer -> UI : View prediction history
UI -> HistCtrl : GET /api/predictions [JWT]
HistCtrl -> DB : SELECT predictions\nWHERE user_id = ?
DB --> HistCtrl : prediction list
HistCtrl --> UI : 200 OK {predictions}
UI --> Consumer : List of past predictions

Consumer -> UI : Find prediction for last month\nClick "Enter actual units"
Consumer -> UI : Type actual kWh from CEB bill
UI -> HistCtrl : PATCH /api/predictions/{id}/actual\n{actual_units: 145.5}

HistCtrl -> DB : SELECT prediction WHERE id=? AND user_id=?
DB --> HistCtrl : prediction record

HistCtrl -> Tariff : calculate_bill(actual_units)
Tariff --> HistCtrl : actual_bill (LKR)

HistCtrl -> DB : UPDATE predictions SET\nactual_units=?, actual_bill=?\nWHERE id=?
DB --> HistCtrl : updated record
HistCtrl --> UI : 200 OK {updated prediction}
UI --> Consumer : Show actual vs predicted comparison

@enduml
```

---

### SD-07 — Admin Views System Statistics

```plantuml
@startuml SD_AdminStats
title Admin Views System Statistics

actor Administrator
participant "React Frontend\nAdmin.jsx" as UI
participant "AdminController\n/api/admin" as AdminCtrl
database "Database" as DB

Administrator -> UI : Navigate to Admin Dashboard
UI -> AdminCtrl : GET /api/admin/stats [JWT]

AdminCtrl -> AdminCtrl : admin_required decorator:\n  verify JWT → get user_id\n  check user.role == "admin"

alt Not admin
  AdminCtrl --> UI : 403 Forbidden
  UI --> Administrator : Access denied
else Is admin
  AdminCtrl -> DB : COUNT users WHERE role='user'
  DB --> AdminCtrl : total_users
  AdminCtrl -> DB : COUNT predictions
  DB --> AdminCtrl : total_predictions
  AdminCtrl -> DB : AVG(predicted_bill), AVG(predicted_units)
  DB --> AdminCtrl : avg_bill, avg_units
  AdminCtrl -> DB : GROUP BY risk_level COUNT(id)
  DB --> AdminCtrl : risk_distribution
  AdminCtrl -> DB : SELECT predictions\nWHERE actual_units IS NOT NULL
  DB --> AdminCtrl : actuals list
  AdminCtrl -> AdminCtrl : Compute accuracy:\n  accuracy_i = max(0, 1 - |pred - actual| / actual) * 100\n  avg_accuracy = mean(accuracies)
  AdminCtrl --> UI : 200 OK\n{total_users, total_predictions,\navg_predicted_bill, avg_predicted_units,\nrisk_distribution, avg_accuracy,\npredictions_with_actual}
  UI --> Administrator : Display stat cards and charts
end

@enduml
```

---

### SD-08 — Admin Deletes a User

```plantuml
@startuml SD_AdminDeleteUser
title Admin Deletes a User

actor Administrator
participant "React Frontend\nAdmin.jsx" as UI
participant "AdminController\n/api/admin/users/{id}" as AdminCtrl
database "Database" as DB

Administrator -> UI : View user list
UI -> AdminCtrl : GET /api/admin/users [JWT]
AdminCtrl -> DB : SELECT users WHERE role='user'\nORDER BY created_at DESC
DB --> AdminCtrl : paginated user list
AdminCtrl --> UI : 200 OK {users, total, pages}
UI --> Administrator : Display user table

Administrator -> UI : Click "Delete" on a user row
UI -> UI : Show confirmation dialog
Administrator -> UI : Confirm deletion

UI -> AdminCtrl : DELETE /api/admin/users/{user_id} [JWT]
AdminCtrl -> AdminCtrl : admin_required check

AdminCtrl -> DB : SELECT user WHERE id=?
DB --> AdminCtrl : user record

alt user.role == "admin"
  AdminCtrl --> UI : 400 Bad Request\n{"error": "Cannot delete admin accounts"}
  UI --> Administrator : Show error
else role == "user"
  AdminCtrl -> DB : DELETE FROM users WHERE id=?\n(cascades to predictions, bills, appliances)
  DB --> AdminCtrl : success
  AdminCtrl --> UI : 200 OK {message: "User deleted"}
  UI --> Administrator : User removed from table
end

@enduml
```

---

## 7. Database Entity Relationship Diagram

```plantuml
@startuml EnergyWise_ERD
title EnergyWise — Entity Relationship Diagram

entity "users" as User {
  *id : INTEGER <<PK>>
  --
  name : VARCHAR(100)
  email : VARCHAR(150) <<unique>>
  password_hash : VARCHAR(255)
  role : ENUM('user','admin')
  district : VARCHAR(100)
  created_at : DATETIME
}

entity "user_appliances" as UA {
  *id : INTEGER <<PK>>
  --
  *user_id : INTEGER <<FK>>
  fan_count : INTEGER
  fan_hours_per_month : FLOAT
  ac_count : INTEGER
  ac_hours_per_month : FLOAT
  ac_tons : FLOAT
  ac_units : JSON
  fridge_count : INTEGER
  washer_hours_per_month : FLOAT
  heater_hours_per_month : FLOAT
  other_hours_per_month : FLOAT
  updated_at : DATETIME
}

entity "bills" as Bill {
  *id : INTEGER <<PK>>
  --
  *user_id : INTEGER <<FK>>
  month : INTEGER
  year : INTEGER
  units : FLOAT
  amount : FLOAT
  notes : TEXT
  created_at : DATETIME
}

entity "predictions" as Pred {
  *id : INTEGER <<PK>>
  --
  *user_id : INTEGER <<FK>>
  members : INTEGER
  district : VARCHAR(100)
  prev_bill_1 : FLOAT
  prev_bill_2 : FLOAT
  prev_bill_3 : FLOAT
  fan_count : INTEGER
  ac_count : INTEGER
  ac_hours_per_month : FLOAT
  ac_tons : FLOAT
  fridge_count : INTEGER
  washer_hours_per_month : FLOAT
  heater_hours_per_month : FLOAT
  other_hours_per_month : FLOAT
  avg_temp : FLOAT
  avg_humidity : FLOAT
  total_precip : FLOAT
  avg_wind : FLOAT
  start_date : DATETIME
  end_date : DATETIME
  predicted_units : FLOAT
  predicted_bill : FLOAT
  risk_level : VARCHAR(20)
  recommendations : JSON
  appliance_breakdown : JSON
  actual_units : FLOAT
  actual_bill : FLOAT
  created_at : DATETIME
}

User ||--o| UA   : "has profile"
User ||--o{ Bill : "has bills"
User ||--o{ Pred : "has predictions"

@enduml
```

---

## 8. ML Feature Vector Summary

The trained model receives the following 21 features per prediction:

| # | Feature | Source | Description |
|---|---|---|---|
| 1 | `members` | User input | Number of people in household |
| 2 | `avg_prev_bill` | Derived | Mean of 3 previous bills (kWh) |
| 3 | `prev_month_consumption` | Derived | Most recent month's bill |
| 4 | `std_prev_3months` | Derived | Std deviation of 3 previous bills |
| 5 | `consumption_trend` | Derived | prev_bill_1 − prev_bill_2 |
| 6 | `fan_count` | Appliance profile | Number of fans |
| 7 | `fan_hours_per_month` | Appliance profile | Total fan run hours/month |
| 8 | `ac_count` | Appliance profile | Number of AC units |
| 9 | `ac_hours_per_month` | Appliance profile | Avg AC run hours/month |
| 10 | `ac_tons` | Appliance profile | Weighted avg AC capacity (tons) |
| 11 | `fridge_count` | Appliance profile | Number of refrigerators |
| 12 | `washer_hours_per_month` | Appliance profile | Washing machine hours/month |
| 13 | `heater_hours_per_month` | Appliance profile | Water heater hours/month |
| 14 | `other_hours_per_month` | Appliance profile | Other appliances hours/month |
| 15 | `avg_temp` | Open-Meteo API | 30-day average temperature (°C) |
| 16 | `avg_humidity` | Open-Meteo API | 30-day average relative humidity (%) |
| 17 | `total_precip` | Open-Meteo API | 30-day total precipitation (mm) |
| 18 | `avg_wind` | Open-Meteo API | 30-day average wind speed (km/h) |
| 19 | `month` | System clock | Current calendar month (1–12) |
| 20 | `ac_kwh_est` | Derived | `ac_count × ac_hrs × ac_tons × 0.7` |
| 21 | `total_load_est` | Derived | Sum of all appliance estimated kWh |

---

## 9. CEB Tariff Logic Summary

The `TariffService` implements the PUCSL-approved tariff (effective 11 May 2026).

| Schedule | Consumption | Fixed Charge | Progressive Rates |
|---|---|---|---|
| **Schedule 1 (Low)** | 0 – 60 kWh | LKR 80 (≤30) / LKR 210 (31–60) | LKR 5.00/unit (0–30), LKR 9.00/unit (31–60) |
| **Schedule 2 (Mid)** | 61 – 180 kWh | LKR 400 (≤90) / LKR 1,000 (≤120) / LKR 1,500 (≤180) | LKR 14–44/unit (progressive) |
| **Schedule 3 (High)** | > 180 kWh | LKR 2,500 | LKR 32.50/unit (≤180), LKR 100.00/unit (>180) |

Crossing a schedule boundary recalculates the **entire bill** at the new schedule's rates — not just the excess units. The recommendation engine explicitly checks proximity to these boundaries.

---

## 10. API Endpoint Summary

| Method | Endpoint | Auth | Actor | Purpose |
|---|---|---|---|---|
| POST | `/api/auth/register` | None | Consumer | Create account |
| POST | `/api/auth/login` | None | Consumer / Admin | Authenticate |
| GET | `/api/auth/me` | JWT | Any | Get current user |
| GET | `/api/appliances` | JWT | Consumer | Get appliance profile |
| POST | `/api/appliances` | JWT | Consumer | Create appliance profile |
| PUT | `/api/appliances` | JWT | Consumer | Update appliance profile |
| POST | `/api/predict` | JWT | Consumer | Run energy prediction |
| GET | `/api/bills` | JWT | Consumer | List bill records |
| POST | `/api/bills` | JWT | Consumer | Add bill record |
| PUT | `/api/bills/{id}` | JWT | Consumer | Edit bill record |
| DELETE | `/api/bills/{id}` | JWT | Consumer | Delete bill record |
| GET | `/api/predictions` | JWT | Consumer | Prediction history |
| GET | `/api/predictions/{id}` | JWT | Consumer | Single prediction detail |
| DELETE | `/api/predictions/{id}` | JWT | Consumer | Delete prediction |
| PATCH | `/api/predictions/{id}/actual` | JWT | Consumer | Enter actual units |
| GET | `/api/predictions/autofill` | JWT | Consumer | Auto-fill previous bills |
| GET | `/api/admin/stats` | JWT (admin) | Administrator | System statistics |
| GET | `/api/admin/users` | JWT (admin) | Administrator | All users (paginated) |
| DELETE | `/api/admin/users/{id}` | JWT (admin) | Administrator | Delete user |
| GET | `/api/admin/predictions` | JWT (admin) | Administrator | All predictions (paginated) |
| GET | `/api/weather` | JWT | Consumer | Weather for a district |
