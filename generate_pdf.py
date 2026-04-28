from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "Expense_Analyzer_Project_Overview.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=20*mm, rightMargin=20*mm,
    topMargin=22*mm, bottomMargin=22*mm,
)

styles = getSampleStyleSheet()

# Custom styles
TEAL = colors.HexColor("#0f766e")
DARK = colors.HexColor("#17202a")
MUTED = colors.HexColor("#667085")
LIGHT_BG = colors.HexColor("#f5f8fb")
BORDER = colors.HexColor("#d9e2ec")
CODE_BG = colors.HexColor("#f0f4f8")

title_style = ParagraphStyle("Title", parent=styles["Title"],
    fontSize=22, textColor=TEAL, spaceAfter=4, alignment=TA_CENTER)

subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
    fontSize=11, textColor=MUTED, spaceAfter=16, alignment=TA_CENTER)

h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
    fontSize=14, textColor=TEAL, spaceBefore=14, spaceAfter=6,
    borderPad=0)

h3_style = ParagraphStyle("H3", parent=styles["Heading3"],
    fontSize=11, textColor=DARK, spaceBefore=10, spaceAfter=4,
    fontName="Helvetica-Bold")

body_style = ParagraphStyle("Body", parent=styles["Normal"],
    fontSize=9.5, leading=15, textColor=DARK, spaceAfter=6)

bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"],
    fontSize=9.5, leading=14, textColor=DARK, leftIndent=14,
    spaceAfter=3, bulletIndent=4)

code_style = ParagraphStyle("Code", parent=styles["Code"],
    fontSize=8.5, leading=13, leftIndent=12, backColor=CODE_BG,
    borderColor=BORDER, borderWidth=1, borderPad=6,
    fontName="Courier", spaceAfter=8, spaceBefore=4)

file_ref_style = ParagraphStyle("FileRef", parent=styles["Normal"],
    fontSize=8.5, textColor=MUTED, fontName="Courier", spaceAfter=6)

def H(text, level=2):
    return Paragraph(text, h2_style if level == 2 else h3_style)

def P(text):
    return Paragraph(text, body_style)

def B(text):
    return Paragraph(f"• {text}", bullet_style)

def Code(text):
    return Paragraph(text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)

def FileRef(text):
    return Paragraph(text, file_ref_style)

def HR():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8, spaceBefore=4)

story = []

# ── Title ──────────────────────────────────────────────────────────────────────
story += [
    Spacer(1, 6*mm),
    Paragraph("Expense Data Analyzer", title_style),
    Paragraph("Project Overview — Architecture, Tech Stack &amp; How It Works", subtitle_style),
    HR(),
    Spacer(1, 2*mm),
]

# ── What the project does ──────────────────────────────────────────────────────
story += [
    H("What This Project Does"),
    P("A personal finance web app for students to <b>track, visualize, and get AI-powered suggestions</b> on their spending. Users can:"),
    B("Add expenses manually or bulk-import via CSV"),
    B("View spending charts — category breakdown (doughnut) and monthly trends (bar)"),
    B("Ask Google Gemini AI personalized questions about their spending"),
    B("Fallback local analysis when no API key is configured"),
    Spacer(1, 4*mm),
]

# ── Architecture ───────────────────────────────────────────────────────────────
story += [
    H("Architecture Overview"),
    P("The app follows a classic <b>backend API + single-page frontend</b> pattern:"),
    Code(
        "Browser (React + Chart.js)\n"
        "        |\n"
        "        |  HTTP / JSON API calls\n"
        "        v\n"
        "Django Backend (Python)\n"
        "        |\n"
        "        |-- reads/writes --> SQLite database\n"
        "        |-- calls        --> Google Gemini API (AI insights)\n"
        "        |-- parses CSV   --> pandas\n"
        "        |\n"
        "Static files served by WhiteNoise\n"
        "Deployed on Vercel"
    ),
    Spacer(1, 2*mm),
]

# ── Tech Stack Table ────────────────────────────────────────────────────────────
story += [
    H("Tech Stack at a Glance"),
]

table_data = [
    [Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Role</b>", body_style)],
    [Paragraph("Django 5.2", body_style), Paragraph("Web framework, ORM, URL routing, CSRF, migrations", body_style)],
    [Paragraph("SQLite", body_style), Paragraph("File-based database — zero config, single user", body_style)],
    [Paragraph("pandas 2.2", body_style), Paragraph("CSV parsing and row validation for bulk import", body_style)],
    [Paragraph("google-genai 1.73", body_style), Paragraph("Google Gemini AI SDK — spending insights", body_style)],
    [Paragraph("React 18 (CDN)", body_style), Paragraph("Single-page frontend, state management, DOM rendering", body_style)],
    [Paragraph("Chart.js 4.4", body_style), Paragraph("Doughnut and bar charts for expense visualization", body_style)],
    [Paragraph("Bootstrap 5.3", body_style), Paragraph("Responsive grid, form controls, table, buttons", body_style)],
    [Paragraph("WhiteNoise 6.9", body_style), Paragraph("Serves compressed static files directly from Django", body_style)],
    [Paragraph("Gunicorn 23", body_style), Paragraph("Production WSGI server for concurrent request handling", body_style)],
    [Paragraph("python-dotenv", body_style), Paragraph("Loads SECRET_KEY and GEMINI_API_KEY from .env file", body_style)],
    [Paragraph("Vercel", body_style), Paragraph("Serverless deployment via vercel.json + @vercel/python", body_style)],
]

col_widths = [45*mm, 120*mm]
tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), TEAL),
    ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("GRID",       (0, 0), (-1, -1), 0.4, BORDER),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 7),
]))
story += [tbl, Spacer(1, 6*mm)]

# ── Detailed breakdown ─────────────────────────────────────────────────────────
story += [H("Detailed Tech Breakdown")]

# 1 Django
story += [
    H("1. Django — Web Framework", level=3),
    FileRef("Files: expense_analyzer/settings.py · expense_analyzer/urls.py · expenses/views.py"),
    P("Django is the backbone of the entire backend. It handles:"),
    B("<b>URL routing</b> — /admin/ goes to Django admin; all other paths route to the expenses app, which maps 6 JSON API endpoints."),
    B("<b>ORM</b> — Database queries are written in Python, not SQL. Example: <font name='Courier' size='8.5'>expenses.values(\"category\").annotate(total=Sum(\"amount\"))</font> compiles to SQL GROUP BY + SUM automatically."),
    B("<b>CSRF protection</b> — @ensure_csrf_cookie sets a secure cookie; every POST must echo it back, blocking cross-site attacks."),
    B("<b>Migrations</b> — Schema changes are versioned in expenses/migrations/ and applied with manage.py migrate."),
    P("<i>Why Django?</i> Batteries-included: admin panel, ORM, migrations, security middleware, and static file management come built in."),
    Spacer(1, 2*mm),
]

# 2 SQLite
story += [
    H("2. SQLite — Database", level=3),
    FileRef("File: expense_analyzer/settings.py:55-60"),
    P("Stores all Expense records in a single file (<font name='Courier' size='8.5'>db.sqlite3</font>). On Vercel (serverless), the path is <font name='Courier' size='8.5'>/tmp/db.sqlite3</font> — the only writable directory in a serverless environment. This means data resets on cold starts, which is an accepted trade-off for a student project."),
    P("<i>Why SQLite?</i> Zero-config, file-based, perfect for a single-user app. No separate database server needed."),
    Spacer(1, 2*mm),
]

# 3 Expense model
story += [
    H("3. The Expense Model", level=3),
    FileRef("File: expenses/models.py"),
    P("The single database table has five columns:"),
    Code(
        "date        — DateField\n"
        "category    — Choice field (Food/Travel/Shopping/Bills/Education/Health/Entertainment/Other)\n"
        "description — CharField (max 160 chars)\n"
        "amount      — DecimalField (10 digits, 2 decimal places)\n"
        "created_at  — DateTimeField (auto-set on creation)"
    ),
    P("Default ordering is newest-first (<font name='Courier' size='8.5'>-date, -created_at</font>)."),
    Spacer(1, 2*mm),
]

# 4 API
story += [
    H("4. REST-style JSON API", level=3),
    FileRef("File: expenses/views.py · expenses/urls.py"),
    P("The backend exposes 5 API endpoints, all returning JSON:"),
]

api_data = [
    [Paragraph("<b>Endpoint</b>", body_style), Paragraph("<b>Method</b>", body_style), Paragraph("<b>What it does</b>", body_style)],
    [Paragraph("/api/expenses/", body_style), Paragraph("GET", body_style), Paragraph("Full summary: total, count, top category, chart data, recent 12 expenses", body_style)],
    [Paragraph("/api/expenses/add/", body_style), Paragraph("POST", body_style), Paragraph("Validates JSON body and creates one expense", body_style)],
    [Paragraph("/api/expenses/upload/", body_style), Paragraph("POST", body_style), Paragraph("Accepts a CSV file, bulk-creates rows row-by-row", body_style)],
    [Paragraph("/api/expenses/<id>/delete/", body_style), Paragraph("POST", body_style), Paragraph("Deletes one expense by ID", body_style)],
    [Paragraph("/api/expenses/insights/", body_style), Paragraph("POST", body_style), Paragraph("Calls Gemini AI with current spending data + user question", body_style)],
]
api_tbl = Table(api_data, colWidths=[50*mm, 20*mm, 95*mm], repeatRows=1)
api_tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), TEAL),
    ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ("GRID",       (0, 0), (-1, -1), 0.4, BORDER),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 7),
]))
story += [api_tbl, Spacer(1, 4*mm)]

story += [
    P("The key helper <font name='Courier' size='8.5'>_summary_payload()</font> (views.py:32) runs all aggregation queries and returns the data structure the frontend needs. Every mutating endpoint returns a fresh summary so the UI always reflects the latest state."),
    Spacer(1, 2*mm),
]

# 5 pandas
story += [
    H("5. pandas — Data Processing", level=3),
    FileRef("File: expenses/views.py:131"),
    P("Used exclusively in the CSV upload flow. pandas reads the uploaded file into a DataFrame, normalizes column names to lowercase, then iterates rows — each row goes through the same <font name='Courier' size='8.5'>_validate_expense()</font> function used for manual entries."),
    Code(
        "frame = pd.read_csv(csv_file)\n"
        "frame.columns = [col.lower() for col in frame.columns]\n"
        "for index, row in frame.iterrows():\n"
        "    errors, cleaned = _validate_expense(row.to_dict())\n"
        "    if errors: skipped.append(...); continue\n"
        "    Expense.objects.create(**cleaned)"
    ),
    P("<i>Why pandas?</i> Handles CSV edge cases (encoding, quoting, whitespace) far more robustly than Python's built-in csv module. The .to_dict() trick makes each CSV row look identical to a JSON form submission."),
    Spacer(1, 2*mm),
]

# 6 Gemini
story += [
    H("6. Google Gemini AI (google-genai)", level=3),
    FileRef("File: expenses/views.py:171-232"),
    P("The AI insights flow works like this:"),
    B("Collect current _summary_payload() (totals, categories, monthly trends, recent expenses)"),
    B("Build a structured prompt asking Gemini for: where the user spends most, two likely reasons, three savings suggestions"),
    B("Call gemini-2.5-flash-lite — a fast, lightweight Gemini model"),
    B("Graceful fallback — if no API key is set or Gemini fails, _local_insight() generates a math-based local answer showing the top category percentage"),
    P("The frontend shows the source label: <i>Gemini API</i>, <i>Gemini error fallback</i>, or <i>Local fallback</i> so users always know where the answer came from."),
    Spacer(1, 2*mm),
]

# 7 React
story += [
    H("7. React 18 — Frontend UI", level=3),
    FileRef("Files: static/js/app.js · templates/dashboard.html"),
    P("The entire frontend is a <b>single React component</b> (App) loaded as CDN scripts — no npm, no build step. Babel Standalone transpiles JSX directly in the browser at runtime."),
    P("React manages four pieces of state:"),
    B("<b>summary</b> — all chart/table data fetched from the API"),
    B("<b>form</b> — the add-expense form inputs (date, category, description, amount)"),
    B("<b>insight</b> — the AI response text"),
    B("<b>message</b> — status alerts (success/error)"),
    P("<font name='Courier' size='8.5'>useMemo</font> derives <font name='Courier' size='8.5'>categoryChart</font> and <font name='Courier' size='8.5'>monthlyChart</font> from summary without re-running on unrelated state changes. A central <font name='Courier' size='8.5'>apiFetch()</font> helper attaches the CSRF token from the cookie to every request."),
    P("<i>Why React without a build tool?</i> Keeps the project simple — no Node.js or bundler config. Babel in-browser transpilation is slower than pre-built but acceptable for a student project."),
    Spacer(1, 2*mm),
]

# 8 Chart.js
story += [
    H("8. Chart.js — Data Visualization", level=3),
    FileRef("File: static/js/app.js:45-93"),
    P("The <font name='Courier' size='8.5'>ChartCanvas</font> component wraps Chart.js. It creates a new chart on mount, destroys and recreates it when data changes (useEffect cleanup), and renders:"),
    B("<b>Doughnut chart</b> — category-wise expense breakdown"),
    B("<b>Bar chart</b> — monthly spending trends"),
    P("The dependency trick <font name='Courier' size='8.5'>[labels.join(\"|\"), values.join(\"|\")]</font> converts arrays to strings so React can detect actual data changes (arrays are reference-compared by default in JS)."),
    Spacer(1, 2*mm),
]

# 9 Bootstrap
story += [
    H("9. Bootstrap 5 — CSS Framework", level=3),
    FileRef("Files: templates/dashboard.html:8 · static/css/styles.css"),
    P("Bootstrap provides the responsive grid (row/col-lg-6), form controls, buttons, and table styles. Custom CSS in styles.css overrides Bootstrap's primary color to teal (#0f766e) and adds project-specific components: .metric, .panel, .chart-box, .insight-box."),
    Spacer(1, 2*mm),
]

# 10 WhiteNoise
story += [
    H("10. WhiteNoise — Static File Serving", level=3),
    FileRef("File: expense_analyzer/settings.py:27,77"),
    P("Normally, a separate nginx server serves static files. WhiteNoise middleware makes Django serve them directly — essential for Vercel. <font name='Courier' size='8.5'>CompressedManifestStaticFilesStorage</font> adds content-hash fingerprinting to filenames (e.g., <font name='Courier' size='8.5'>styles.abc123.css</font>) for automatic cache-busting."),
    Spacer(1, 2*mm),
]

# 11 Gunicorn
story += [
    H("11. Gunicorn — Production WSGI Server", level=3),
    FileRef("File: requirements.txt:6"),
    P("Django's built-in dev server is single-threaded and not safe for production. Gunicorn runs multiple worker processes to handle concurrent requests. Vercel invokes the app through <font name='Courier' size='8.5'>expense_analyzer/wsgi.py</font>."),
    Spacer(1, 2*mm),
]

# 12 python-dotenv
story += [
    H("12. python-dotenv — Environment Variables", level=3),
    FileRef("File: expense_analyzer/settings.py:8 · .env.example"),
    P("Loads <font name='Courier' size='8.5'>SECRET_KEY</font> and <font name='Courier' size='8.5'>GEMINI_API_KEY</font> from a local <font name='Courier' size='8.5'>.env</font> file so secrets are never hardcoded in source. The <font name='Courier' size='8.5'>.env.example</font> file shows which variables are needed without exposing real values."),
    Spacer(1, 2*mm),
]

# 13 Vercel
story += [
    H("13. Vercel — Deployment", level=3),
    FileRef("File: vercel.json"),
    P("Vercel deploys the app as a serverless Python function. Every HTTP request is routed to the WSGI app:"),
    Code(
        '{\n'
        '  "builds": [{ "src": "expense_analyzer/wsgi.py", "use": "@vercel/python" }],\n'
        '  "routes": [{ "src": "/(.*)", "dest": "expense_analyzer/wsgi.py" }]\n'
        '}'
    ),
    P("Database is at /tmp/db.sqlite3 (the only writable path in serverless). This means data resets on cold starts — a known trade-off for a student project."),
    Spacer(1, 2*mm),
]

# ── Data flow ──────────────────────────────────────────────────────────────────
story += [
    HR(),
    H("Data Flow: Adding an Expense (End-to-End)"),
    Code(
        "1. User fills form → clicks 'Add Expense'\n"
        "2. React calls apiFetch('POST /api/expenses/add/', { date, category, description, amount })\n"
        "   → attaches CSRF token from cookie to request headers\n"
        "3. Django CsrfViewMiddleware validates the token\n"
        "4. add_expense() view calls _validate_expense() — checks date format, non-empty\n"
        "   description, positive amount, valid category\n"
        "5. Expense.objects.create(**cleaned) → SQL INSERT into SQLite\n"
        "6. Returns { expense, summary } JSON — summary has fresh aggregated totals\n"
        "7. React sets summary state → metrics, charts, and table all re-render"
    ),
    Spacer(1, 4*mm),
]

# ── Data flow AI ───────────────────────────────────────────────────────────────
story += [
    H("Data Flow: Asking Gemini for Insights"),
    Code(
        "1. User types a question → clicks 'Ask'\n"
        "2. React POST /api/expenses/insights/ with { question }\n"
        "3. gemini_insights() view calls _summary_payload() to gather all spending data\n"
        "4. _build_gemini_prompt() formats data + question into a structured prompt\n"
        "5a. If GEMINI_API_KEY is set → call gemini-2.5-flash-lite, return AI text\n"
        "5b. If no key → _local_insight() computes top category % and returns text\n"
        "6. Response includes { insight, source } — source tells frontend which path was taken\n"
        "7. React displays insight in the insight-box with the source label"
    ),
    Spacer(1, 6*mm),
    HR(),
    Paragraph("Generated by Claude Code  •  Expense Analyzer Project Overview", subtitle_style),
]

doc.build(story)
print(f"PDF saved: {OUTPUT}")
