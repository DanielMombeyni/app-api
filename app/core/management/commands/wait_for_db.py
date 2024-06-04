"""Django command to wait for the database to be available."""

import time
from psycopg2 import OperationalError as Psycopg2Error  # type: ignore
from django.db.utils import OperationalError
from typing import Any
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args: Any, **options: Any) -> str | None:
        """Entry point for command."""
        self.stdout.write("Waiting for database...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stderr.write("Database unavailable, waiting 1s...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database available!"))
