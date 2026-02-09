from django.core.management.base import BaseCommand
from core.models import PageContent
from users.models import Member


class Command(BaseCommand):
    help = "Clear the KPI override for the about page so it uses live database count."

    def handle(self, *args, **options):
        try:
            pc = PageContent.objects.get(page_name='about')
            pc.kpi_value = None
            pc.save()
            self.stdout.write(
                self.style.SUCCESS(
                    "Cleared KPI override for 'about' page. It will now use live database count."
                )
            )
        except PageContent.DoesNotExist:
            self.stdout.write(
                "No PageContent found for 'about' - count will use database by default."
            )
        count = Member.objects.count()
        self.stdout.write(f"Current member count in database: {count:,}")
