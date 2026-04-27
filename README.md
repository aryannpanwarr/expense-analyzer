# Expense Data Analyzer

A Django + Bootstrap + React project for analyzing personal expenses. Users can add expenses manually, upload CSV files, view spending charts, and ask Gemini for savings suggestions.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Update `.env` and replace `GEMINI_API_KEY` with your Gemini API key.

## CSV Format

Use these columns:

```csv
date,category,description,amount
2026-04-01,Food,Lunch,180
2026-04-02,Travel,Bus pass,450
```

Accepted date format is `YYYY-MM-DD`. Amount should be a number.

## Features

- Manual expense entry
- CSV upload
- Monthly spending chart
- Category-wise chart
- Recent expense table
- Gemini-powered spending explanation and savings advice
