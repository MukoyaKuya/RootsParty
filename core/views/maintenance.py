from django.core.management import call_command
from django.http import HttpResponse
import traceback

def trigger_migration(request):
    token = request.GET.get('token')
    if token != 'roots-party-migration-fix-2026':
         return HttpResponse("Unauthorized", status=403)
    try:
        # Fake back to 49
        call_command('migrate', 'core', '0049', fake=True)
        # Actually migrate forward
        call_command('migrate', 'core')
        return HttpResponse("Migration Successful")
    except Exception as e:
        return HttpResponse(f"Migration Failed: {e}<br><pre>{traceback.format_exc()}</pre>")
