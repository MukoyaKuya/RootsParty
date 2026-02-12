from django.core.management import call_command
from django.http import HttpResponse
import traceback
import uuid
from django.db import connection
from core.models import Event, GatePass

def trigger_migration(request):
    token = request.GET.get('token')
    if token != 'roots-party-migration-fix-2026':
         return HttpResponse("Unauthorized", status=403)
    try:
        results = []
        
        # Check current columns in core_event
        columns = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'core_event'")
            columns = [row[0] for row in cursor.fetchall()]
        
        results.append(f"Current columns in core_event: {columns}")
        
        if 'uuid' in columns:
            results.append("Column 'uuid' already exists. Faking up to 0051...")
            call_command('migrate', 'core', '0051', fake=True)
        else:
            results.append("Column 'uuid' missing. Running migrations normally...")
            call_command('migrate', 'core', '0049', fake=True)
            call_command('migrate', 'core', '0050')
            
            # Populate unique UUIDs
            results.append("Populating unique UUIDs...")
            for model in [Event, GatePass]:
                count = 0
                for obj in model.objects.filter(uuid__isnull=True):
                    obj.uuid = uuid.uuid4()
                    obj.save(update_fields=['uuid'])
                    count += 1
                results.append(f"Updated {count} {model.__name__} objects.")
                
            call_command('migrate', 'core', '0051')

        # Run remaining migrations
        results.append("Running remaining migrations...")
        call_command('migrate', 'core')
        
        results.append("Migration Successful!")
        return HttpResponse("<br>".join(results))
        
    except Exception as e:
        return HttpResponse(f"Migration Failed: {e}<br><pre>{traceback.format_exc()}</pre>")
