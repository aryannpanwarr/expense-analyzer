import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_analyzer.settings")
django.setup()

if os.getenv("VERCEL") == "1":
    from django.core.management import call_command
    try:
        call_command("migrate", verbosity=0)
    except Exception:
        pass

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application  # Vercel entry point
