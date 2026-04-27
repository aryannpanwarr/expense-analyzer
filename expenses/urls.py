from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/expenses/", views.expense_list, name="expense_list"),
    path("api/expenses/add/", views.add_expense, name="add_expense"),
    path("api/expenses/upload/", views.upload_expenses, name="upload_expenses"),
    path("api/expenses/insights/", views.gemini_insights, name="gemini_insights"),
    path("api/expenses/<int:expense_id>/delete/", views.delete_expense, name="delete_expense"),
]
