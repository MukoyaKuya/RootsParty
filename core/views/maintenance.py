from django.core.management import call_command
from django.http import HttpResponse
import traceback
import uuid
from core.models import Event, GatePass

def trigger_migration(request):
    token = request.GET.get('token')
    if token != 'roots-party-migration-fix-2026':
         return HttpResponse("Unauthorized", status=403)
    try:
        results = []
        
        # 1. Fake back to 49
        results.append("Faking back to 0049...")
        call_command('migrate', 'core', '0049', fake=True)
        
        # 2. Add UUID field (null=True) via 0050
        results.append("Running migration 0050 (Add UUID fields)...")
        call_command('migrate', 'core', '0050')
        
        # 3. Populate unique UUIDs for existing objects
        results.append("Populating unique UUIDs for existing objects...")
        
        events_count = 0
        for event in Event.objects.all():
            if not event.uuid:
                event.uuid = uuid.uuid4()
                event.save(update_fields=['uuid'])
                events_count += 1
        results.append(f"Updated {events_count} Events with new UUIDs.")
        
        gatepass_count = 0
        for gp in GatePass.objects.all():
            if not gp.uuid:
                gp.uuid = uuid.uuid4()
                gp.save(update_fields=['uuid'])
                gatepass_count += 1
        results.append(f"Updated {gatepass_count} GatePasses with new UUIDs.")
        
        # 4. Apply unique constraint via 0051 and remaining migrations
        results.append("Running remaining migrations (including 0051 unique constraint)...")
        call_command('migrate', 'core')
        
        results.append("Migration Successful!")
        return HttpResponse("<br>".join(results))
        
    except Exception as e:
        return HttpResponse(f"Migration Failed: {e}<br><pre>{traceback.format_exc()}</pre>")
