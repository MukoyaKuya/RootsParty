from aspirants.models import AspirantRegistration
for a in AspirantRegistration.objects.all():
    print(f"ID: {a.id}, Constituency: {a.constituency}, County: {a.county}")
