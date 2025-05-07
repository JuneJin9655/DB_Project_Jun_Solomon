# Medical Clinic Database Management System

## Quick Start Guide

```bash
# 1. Clone repository
git clone git@github.com:JuneJin9655/DB_Project_Jun_Solomon.git
cd DB_Project_Jun_Solomon

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (optional)
cp example.env .env
# Edit .env if needed

# 5. Initialize database
flask db upgrade

# 6. Load test data
python -m tests.setup_complete_database

# 7. Start application
flask run
```

Access the application at: http://127.0.0.1:5000/

## Troubleshooting

For nursing unit display issues:
```bash
python -m tests.update_nurse_nursing_units
python -m tests.update_inpatient_nursing_units
```

## Authors
- Jun Jin
- Solomon Okine