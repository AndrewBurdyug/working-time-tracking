"""Regenrate files."""

from django.core.management.base import BaseCommand, CommandError
from timesheet.models import MonthlyReport, MonthlyInvoice


class Command(BaseCommand):
    """Standard django command interface class."""

    help = 'Regenrate files of reports/invoices.'

    def add_arguments(self, parser):
        """Add arguments."""
        parser.add_argument('things', type=str,
                            help='choose "reports" or "invoices"')

    def handle(self, *args, **options):
        """Handle command with given args."""
        things = options['things']

        if things == 'reports':
            for item in MonthlyReport.objects.all():
                item.save()
                return

        if things == 'invoices':
            for item in MonthlyInvoice.objects.all():
                item.save()
                return

        raise CommandError('I do not known what doing with "%s"' % things)
