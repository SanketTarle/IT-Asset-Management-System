# Enterprise Asset Management System (AMS)

A complete, production-grade web application built with Python Flask and modern responsive frontend technologies to manage, track, and audit physical and financial assets across an enterprise.

---

## 📌 1. Project Overview

The **Asset Management System (AMS)** centralizes the lifecycle of corporate assets—from procurement, custody assignment, maintenance scheduling, and warranty tracking, to financial valuation, depreciation, and decommissioning.

### Key Capabilities
- **Complete Asset Lifecycle**: Registration, tracking, check-out/assignment, return, servicing, and retirement.
- **Custody Management**: Real-time assignment to employees with full historical audit logs.
- **Maintenance Tracking**: Work orders, repair costs, vendor management, and next-service alerts.
- **Executive Analytics**: KPI metric tiles and dynamic interactive charts for category distributions, status ratios, condition states, and financial valuations.
- **7 Comprehensive Reports**: Filterable rosters with instantaneous CSV spreadsheet export and print-ready layouts.
- **Role-Based Access Control (RBAC)**: Distinct permissions for **Admin**, **Manager**, and **Employee**.
- **Zero-Configuration Local Database**: Automatically initializes `database.db` (SQLite) with schema, relations, indexes, and default administrator credentials on first run.

---

## 🚀 2. Quick Start Guide

No external database servers (MySQL, PostgreSQL, MongoDB, etc.) are needed. The application automatically generates `database.db` upon initial execution.

### Prerequisites
- Python 3.10+ installed
- `pip` package manager

### Step 1: Install Dependencies
Open your terminal / PowerShell in the project directory and run:

```bash
pip install -r requirements.txt
```

### Step 2: Launch Application
```bash
python app.py
```

### Step 3: Access Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 3. Default Credentials

The application seeds a default Administrator account upon initialization:

| Role | Email | Password |
|---|---|---|
| **System Administrator** | `admin@company.com` | `Admin@123` |
| **Operations Manager** | `manager@company.com` | `Manager@123` |
| **Employee** | `sarah.jenkins@company.com` | `Employee@123` |

> ⚠️ **IMPORTANT SECURITY NOTICE:**
> For production deployments, please sign in with the default Administrator account and immediately change the password via **My Profile** (`/profile`) or **System Settings** (`/settings`).

---

## 🛠️ 4. Technology Stack

- **Backend**:
  - Python 3.11
  - Flask (v3.0+)
  - Flask-SQLAlchemy (v3.1+)
  - Flask-Login (v0.6+)
  - Werkzeug (Secure password hashing using Scrypt / PBKDF2)
- **Database**:
  - SQLite (stored locally as `database.db` in project root)
- **Frontend**:
  - HTML5 & CSS3 (Modern SaaS design system)
  - Vanilla JavaScript (ES6+)
  - Bootstrap 5.3 (Responsive grid, modal dialogs, utility classes)
  - Chart.js 4.4 (Dynamic interactive charts)
  - Font Awesome 6 (Vector iconography)
  - Inter Google Font

---

## 📂 5. Project Architecture

```
Sarvesh Project/
│
├── app.py                     # Application factory, blueprints, template filters, auto-db init
├── config.py                  # Environment settings, SQLite URI, upload rules
├── requirements.txt           # Python package dependencies
├── database.db                # SQLite database (Auto-created on first run)
├── README.md                  # Comprehensive documentation and user manual
├── .gitignore                 # Version control exclusions
│
├── models/                    # SQLAlchemy database models
│   ├── __init__.py            # Model registry export
│   ├── user.py                # User credentials, roles (Admin/Manager/Employee)
│   ├── asset.py               # Assets, specifications, warranties, values
│   ├── category.py            # Asset taxonomies & categories
│   ├── location.py            # Physical sites, buildings, floors, rooms
│   ├── employee.py            # Staff members, codes, departments
│   ├── assignment.py          # Custody assignments & return records
│   ├── maintenance.py         # Service records, costs, providers
│   └── transaction.py         # Immutable audit log / transaction history
│
├── routes/                    # Modular Blueprint controllers
│   ├── __init__.py            # Blueprint registry
│   ├── auth.py                # Sign in, sign out, user registration
│   ├── dashboard.py           # Metrics computation & Chart.js API
│   ├── assets.py              # Asset CRUD, search, filter, custody actions
│   ├── employees.py           # Employee CRUD & custody history
│   ├── categories.py          # Category management
│   ├── locations.py           # Location & facility management
│   ├── assignments.py         # Equipment check-out / return workflow
│   ├── maintenance.py         # Service work orders & cost tracking
│   ├── reports.py             # 7 core operational reports & CSV export
│   └── settings.py            # User permissions, DB stats, live backup download
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Responsive master layout & sidebar navigation
│   ├── login.html             # Corporate sign-in portal
│   ├── register.html          # User account creation
│   ├── dashboard.html         # Executive overview & dynamic charts
│   ├── assets.html            # Asset directory with multi-column filtering
│   ├── asset_details.html     # Asset specification dossier & audit tabs
│   ├── asset_form.html        # Registration & modification form
│   ├── employees.html         # Staff directory
│   ├── employee_details.html  # Staff dossier with assigned equipment
│   ├── categories.html        # Category management
│   ├── locations.html         # Facility & room directory
│   ├── assignments.html       # Equipment custody ledger & return modal
│   ├── maintenance.html       # Service ledger & schedule modal
│   ├── reports.html           # 7 operational reports & CSV export
│   ├── profile.html           # User profile & password change
│   ├── settings.html          # Administrative user management & DB health
│   ├── 404.html               # Not Found error page
│   └── 500.html               # Internal Server Error page
│
├── static/                    # Frontend static assets
│   ├── css/
│   │   └── style.css          # Production design system stylesheet
│   ├── js/
│   │   ├── app.js             # Global UI interactions (sidebar, alerts, modals)
│   │   ├── dashboard.js       # Dynamic Chart.js visualizations
│   │   └── assets.js          # Image previews, auto-calculations
│   └── uploads/
│       └── assets/            # Secure directory for uploaded asset images
│           └── .gitkeep
│
└── utils/                     # Utility services
    ├── __init__.py
    ├── database.py            # SQLAlchemy instance & auto-initializer (init_db)
    ├── helpers.py             # Code generators, upload sanitizer, audit logger
    └── decorators.py          # Role-based access decorators (@admin_required, etc.)
```

---

## 🗄️ 6. Database Schema & Automatic Initialization

### How `database.db` is Created Automatically
When you execute `python app.py`:
1. The application checks for `database.db` in the project root.
2. If it does not exist, SQLite automatically creates the file.
3. `db.create_all()` executes all DDL statements to construct the tables:
   - `users`: Authentication, bcrypt/scrypt password hashes, role levels.
   - `categories`: Hardware categories (Laptops, Monitors, Furniture, etc.).
   - `locations`: Facility mapping (Buildings, Floors, Rooms).
   - `employees`: Staff roster, codes (`EMP-0001`), departments, contact info.
   - `assets`: Hardware catalog, unique `asset_code` (`AST-00001`), financial values, conditions, serial numbers.
   - `asset_assignments`: History of who held what equipment and when.
   - `maintenance_records`: Servicing events, costs, providers, next-service dates.
   - `asset_transactions`: Complete audit trail of every status transition.
4. An automated seeder checks whether the default administrator account exists. If not, it creates `admin@company.com` with `Admin@123` and populates seed categories, locations, sample employees, and demo assets so the dashboard displays live metrics right out of the box.
5. If `database.db` already exists, existing user data and assets are **never overwritten or cleared**.

---

## 💾 7. How to Backup & Restore `database.db`

### Backup via Web Interface
1. Sign in as an **Administrator**.
2. Navigate to **System Settings** in the sidebar.
3. Click **"Download database.db Backup"** to save an instant snapshot to your computer.

### Manual Backup (Terminal / CLI)
Run:
```powershell
# Windows PowerShell
Copy-Item database.db database_backup.db

# Or Command Prompt
copy database.db database_backup.db
```

### How to Restore
1. Stop the application server (`Ctrl + C`).
2. Replace `database.db` with your backup copy:
   ```powershell
   Copy-Item database_backup.db database.db
   ```
3. Restart the server:
   ```bash
   python app.py
   ```

---

## 📊 8. Reports Included

Navigate to **Reports** in the sidebar to view or download:
1. **Complete Asset Report**: Complete inventory of every physical & software asset.
2. **Assigned Asset Report**: Equipment currently in active staff possession.
3. **Available Asset Report**: Spare / ready-to-deploy inventory in storage.
4. **Maintenance Report**: Service history, repair costs, and vendor logs.
5. **Retired Asset Report**: Decommissioned, lost, or scrapped assets.
6. **Asset Value Report**: Financial summary comparing Purchase Price vs. Current Book Value and Total Depreciation.
7. **Employee Asset Report**: Staff custody breakdown showing how many items each employee currently holds.

All reports can be printed directly using the **Print Report** button or exported to a CSV spreadsheet with the **Export CSV** button.

---

## 🔒 9. Security & Validation Features

- **Password Security**: Passwords are never stored in plaintext; hashed via Werkzeug `generate_password_hash` using standard salt and hashing algorithms.
- **SQL Injection Prevention**: Completely mitigated via SQLAlchemy ORM parameterized queries.
- **Role-Based Authorization**: Route-level protection decorators (`@admin_required`, `@manager_or_admin_required`) prevent privilege escalation.
- **Safe File Uploads**: File uploads are strictly validated against allowed extensions (`.jpg`, `.jpeg`, `.png`, `.webp`), sanitized with `secure_filename`, assigned random UUID filenames, and bounded by a 16MB file size limit.
- **Session Management**: Secure session cookies via Flask-Login with configurable persistence.

---

## ❓ 10. Troubleshooting

### Port 5000 is already in use
If another application is using port 5000, specify a different port in `app.py`:
```python
app.run(host='127.0.0.1', port=5001, debug=True)
```
Then visit `http://127.0.0.1:5001`.

### Permission denied when saving database.db
Ensure your user account has write permissions in the project root directory.

### Resetting to fresh factory state
To reset the system to its initial state:
1. Delete `database.db`.
2. Delete any images in `static/uploads/assets/` (keep `.gitkeep`).
3. Run `python app.py`. The database will automatically recreate itself with the default admin account and initial categories.

