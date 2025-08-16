import csv
from django.core.management.base import BaseCommand
from clients.models import Client as Tenant

class Command(BaseCommand):
    help = "Bulk create tenants from a CSV with columns: name,domain"

    def add_arguments(self, parser):
        parser.add_argument("csv_path")

    def handle(self, *args, **opts):
        path = opts["csv_path"]
        created = 0
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row["name"].strip()
                domain = row["domain"].strip()
                obj, is_created = Tenant.objects.get_or_create(domain=domain, defaults={"name": name})
                created += int(is_created)
                self.stdout.write(("%s %s" % ("CREATED" if is_created else "EXISTS", domain)))
        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}"))
