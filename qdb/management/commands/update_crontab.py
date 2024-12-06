import subprocess
from django.core.management.base import BaseCommand
from qdb.models import CronJob


class Command(BaseCommand):
    help = "Update django crontab from entries in database."

    def handle(self, *args, **options):
        """Create / update django user's crontab using data from the database."""
        # As currently designed for the LBS project, there can only be one CronJob record.
        # However, it's easier to write this to support multiple records, so this could be
        # reusable in other projects with minimal effort.
        entries = []
        cronjobs = CronJob.objects.all()
        for cronjob in cronjobs:
            # If job is disabled, start with a comment (#).
            if cronjob.enabled:
                enabled = ""
            else:
                enabled = "#"
            entry = (
                f"{enabled}{cronjob.minutes} {cronjob.hours} {cronjob.days_of_month}"
                f" {cronjob.months} {cronjob.days_of_week} {cronjob.command}"
            )
            entries.append(entry)

        # Django management commands recommend self.stdout.write, not print.
        # If this command is run normally, the output will be one line per entry,
        # or no output if there are no entries.
        for entry in entries:
            self.stdout.write(entry)

        # Replace django's crontab by piping all entries to stdin of the os crontab command.
        # input must be a string (in this case), not a list.
        entries_text = "\n".join(entries) + "\n"
        p = subprocess.run(
            ["crontab"], input=entries_text, capture_output=True, text=True
        )
        # If crontab can't handle the data, raise an exception to the caller with its error message.
        if p.returncode != 0:
            raise ValueError(p.stderr)
