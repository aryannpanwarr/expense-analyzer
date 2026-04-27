import json
from decimal import Decimal, InvalidOperation

import pandas as pd
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Expense


@ensure_csrf_cookie
def dashboard(request):
    return render(request, "dashboard.html")


def _expense_payload(expense):
    return {
        "id": expense.id,
        "date": expense.date.isoformat(),
        "category": expense.category,
        "description": expense.description,
        "amount": float(expense.amount),
    }


def _summary_payload():
    expenses = Expense.objects.all()
    total = expenses.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    category_rows = (
        expenses.values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    monthly_rows = (
        expenses.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    top_category = category_rows[0] if category_rows else None
    return {
        "total": float(total),
        "count": expenses.count(),
        "topCategory": {
            "category": top_category["category"],
            "total": float(top_category["total"]),
        }
        if top_category
        else None,
        "categories": [
            {"category": row["category"], "total": float(row["total"])}
            for row in category_rows
        ],
        "monthly": [
            {
                "month": row["month"].strftime("%b %Y"),
                "total": float(row["total"]),
            }
            for row in monthly_rows
        ],
        "recent": [_expense_payload(expense) for expense in expenses[:12]],
    }


def expense_list(request):
    return JsonResponse(_summary_payload())


def _json_body(request):
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def _validate_expense(data):
    date = parse_date(str(data.get("date", "")))
    category = str(data.get("category", "Other")).strip() or "Other"
    description = str(data.get("description", "")).strip()

    try:
        amount = Decimal(str(data.get("amount", "")))
    except InvalidOperation:
        amount = Decimal("0")

    valid_categories = {choice[0] for choice in Expense.CATEGORY_CHOICES}
    if category not in valid_categories:
        category = "Other"

    errors = []
    if not date:
        errors.append("Enter a valid date in YYYY-MM-DD format.")
    if not description:
        errors.append("Description is required.")
    if amount <= 0:
        errors.append("Amount must be greater than zero.")

    return errors, {
        "date": date,
        "category": category,
        "description": description,
        "amount": amount,
    }


@require_POST
def add_expense(request):
    errors, cleaned = _validate_expense(_json_body(request))
    if errors:
        return JsonResponse({"errors": errors}, status=400)

    expense = Expense.objects.create(**cleaned)
    return JsonResponse({"expense": _expense_payload(expense), "summary": _summary_payload()}, status=201)


@require_POST
def upload_expenses(request):
    csv_file = request.FILES.get("file")
    if not csv_file:
        return JsonResponse({"errors": ["Choose a CSV file to upload."]}, status=400)

    try:
        frame = pd.read_csv(csv_file)
    except Exception:
        return JsonResponse({"errors": ["Could not read the CSV file."]}, status=400)

    required = {"date", "category", "description", "amount"}
    missing = required.difference(frame.columns.str.lower())
    if missing:
        return JsonResponse(
            {"errors": [f"Missing required columns: {', '.join(sorted(missing))}."]},
            status=400,
        )

    frame.columns = [column.lower() for column in frame.columns]
    created = 0
    skipped = []
    for index, row in frame.iterrows():
        errors, cleaned = _validate_expense(row.to_dict())
        if errors:
            skipped.append(f"Row {index + 2}: {' '.join(errors)}")
            continue
        Expense.objects.create(**cleaned)
        created += 1

    return JsonResponse(
        {
            "created": created,
            "skipped": skipped[:8],
            "summary": _summary_payload(),
        }
    )


@require_POST
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return JsonResponse({"summary": _summary_payload()})


@require_http_methods(["POST"])
def gemini_insights(request):
    summary = _summary_payload()
    question = _json_body(request).get("question") or "How can I reduce expenses?"

    if not summary["count"]:
        return JsonResponse(
            {"insight": "Add or upload expenses first, then I can analyze your spending."}
        )

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        return JsonResponse({"insight": _local_insight(summary, question), "source": "local"})

    prompt = _build_gemini_prompt(summary, question)
    try:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        text = (response.text or "").strip()
    except Exception as exc:
        text = f"Gemini could not be reached right now. Local suggestion: {_local_insight(summary, question)}"
        return JsonResponse({"insight": text, "source": "fallback", "error": str(exc)})

    return JsonResponse({"insight": text, "source": "gemini"})


def _build_gemini_prompt(summary, question):
    return f"""
You are a helpful personal finance assistant for a student expense analyzer project.
Use only this spending data. Keep the answer practical, short, and friendly.

Question: {question}
Total spending: {summary["total"]}
Expense count: {summary["count"]}
Top category: {summary["topCategory"]}
Category totals: {summary["categories"]}
Monthly totals: {summary["monthly"]}
Recent expenses: {summary["recent"]}

Return:
1. Where the user is spending most
2. Two likely reasons
3. Three specific savings suggestions
"""


def _local_insight(summary, question):
    top = summary["topCategory"]
    if not top:
        return "There is not enough spending data yet."

    total = summary["total"] or 1
    percentage = (top["total"] / total) * 100
    return (
        f"Based on your data, you are spending most on {top['category']} "
        f"({percentage:.1f}% of total spending). For '{question}', start by setting "
        f"a weekly limit for {top['category']}, review repeated small expenses, and "
        "compare your monthly trend before making new purchases."
    )
