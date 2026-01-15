from django.core.management.base import BaseCommand
from core.models import Vendor

class Command(BaseCommand):
    help = 'Marks the official Roots Party vendor as verified.'

    def handle(self, *args, **kwargs):
        vendor = Vendor.objects.filter(name="Roots Official").first()
        if vendor:
            vendor.is_verified = True
            vendor.save()
            self.stdout.write(self.style.SUCCESS(f"[OK] Marked '{vendor.name}' as verified"))
        else:
            self.stdout.write(self.style.WARNING("[FAILED] Roots Official vendor not found"))
