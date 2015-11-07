from datetime import datetime, timedelta

from django.core.files.base import ContentFile
from django.template import Context
from django.template.loader import get_template

from .utils.datetime_helpers import tz, get_month_name, get_month_days


def save_spent_time(sender, instance, **kwargs):
    """
    Adjust the end_time if it is not accurate
    """
    instance.end_time = instance.start_time + \
        timedelta(hours=instance.duration)


def create_montly_report(sender, instance, **kwargs):
    """
    Create montly report for user
    """
    _, last_month_day = get_month_days(instance.year, instance.month)

    report_period_start = datetime(
        instance.year, instance.month, 1, tzinfo=tz
    )
    report_period_end = datetime(
        instance.year, instance.month, last_month_day, 23, 59, 59, tzinfo=tz
    )

    tasks = instance.project.tasks.filter(assigned=instance.worker)
    spent_times = []

    for x in tasks:
        worker_times = x.times \
            .filter(start_time__gte=report_period_start) \
            .filter(end_time__lte=report_period_end)
        spent_times.extend(worker_times)

    data = {
        'month': get_month_name(instance.month),
        'year': instance.year,
        'spent_times': sorted(spent_times, reverse=True),
        'month_hours': sum([x.duration for x in spent_times])
    }

    tpl = get_template('timesheet/report.txt')
    report_text = tpl.render(Context(data))

    if instance.filename:
        instance.filename.delete(save=False)

    instance.filename.save(
        instance.title, ContentFile(report_text), save=False
    )


def create_montly_invoice(sender, instance, **kwargs):
    """
    Create montly invoice for user
    """
    _, last_month_day = get_month_days(instance.year, instance.month)

    report_period_start = datetime(
        instance.year, instance.month, 1, tzinfo=tz
    )
    report_period_end = datetime(
        instance.year, instance.month, last_month_day, 23, 59, 59, tzinfo=tz
    )

    spent_times = []
    for project in instance.company.projects.all():
        tasks = project.tasks.filter(assigned=instance.worker)
        for x in tasks:
            worker_times = x.times \
                .filter(start_time__gte=report_period_start) \
                .filter(end_time__lte=report_period_end)
            spent_times.extend(worker_times)

    # total_hours = sum([x.duration for x in spent_times])
    # invoice_id = '{0}-{1}'.format(instance.company.invoice_abbr,
    #                               instance.number)

    # invoice_file = create_invoice(
    #     worker_name=instance.worker.username,
    #     company_abbr=instance.company.invoice_abbr,
    #     invoice_number=invoice_id,
    #     year=instance.year, month=get_month_abbr(instance.month),
    #     hours=total_hours, hourly_rate=instance.company.hourly_rate,
    #     currency=instance.company.salary_currency,
    #     invoice_date=instance.date.strftime('%b %d, %Y')
    # )

    # if instance.filename:
    #     instance.filename.delete(save=False)

    # instance.filename = invoice_file
