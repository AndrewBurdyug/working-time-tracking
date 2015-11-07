import warnings

from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.core.files.base import ContentFile

from .choices import STATUS, PRIORITY, MONTH, CURRENCY
from .utils.datetime_helpers import tz, current_datetime, current_month, \
    current_year, get_month_abbr, get_month_days, get_month_name


class SpentTime(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(default=current_datetime)
    comment = models.CharField(max_length=200)
    duration = models.FloatField(default=0)
    task = models.ForeignKey('Task', related_name='times')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL)

    @property
    def cost(self):
        """
        Feature request:
            - cost is should be depend on salary in company and
              type of working activity, becasue since we can add more than
              one salary position in one company, we want get different
              hourly rates and show appropriate 'cost' of working time
        """
        # temporary implementation
        warnings.simplefilter("always")
        warnings.warn(
            'SpentTime.cost would be depend on type of working activity',
            FutureWarning)
        salary = self.task.project.company.salary_set.filter(
            worker=self.worker)
        if salary:
            return '%.2f %s' % (self.duration * salary[0].hourly_rate,
                                salary[0].currency)
        return '-//-'

    @property
    def period(self):
        return '%s - %s' % (self.start_time.astimezone(tz).strftime('%H:%M'),
                            self.end_time.astimezone(tz).strftime('%H:%M'))

    @property
    def day(self):
        return self.start_time.astimezone(tz).strftime('%Y-%m-%d')

    @property
    def title(self):
        return str(self)

    def save(self, *args, **kwargs):
        self.end_time = self.start_time + timedelta(hours=self.duration)
        super(SpentTime, self).save(*args, **kwargs)

    def __str__(self):
        return '%s - %sh' % (self.task, self.duration)

    def __lt__(self, other):
        return self.start_time < other.start_time

    class Meta:
        ordering = ['-end_time']


class Task(models.Model):
    title = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField(choices=STATUS)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY)
    start_date = models.DateField()
    project = models.ForeignKey('Project', related_name='tasks')
    assigned = models.ForeignKey(settings.AUTH_USER_MODEL)
    category = models.ForeignKey('Category', blank=True, null=True,
                                 on_delete=models.SET_NULL)
    progress = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return '%s - %s' % (self.project, self.title)

    class Meta:
        ordering = ['project__company', 'project__title', '-title', 'status']


class Category(models.Model):
    title = models.CharField(max_length=100)
    project = models.ForeignKey('Project', related_name='categories')

    def __str__(self):
        return '%s - %s' % (self.project, self.title)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['project__company', 'project__title']


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    company = models.ForeignKey('Company', related_name='projects',
                                blank=True, null=True)

    def __str__(self):
        return '%s - %s' % (self.company, self.title)

    class Meta:
        ordering = ['company__title', 'title']


class Company(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Companies'


class MonthlyReport(models.Model):
    month = models.PositiveSmallIntegerField(default=current_month,
                                             choices=MONTH)
    year = models.PositiveSmallIntegerField(default=current_year)
    filename = models.FileField(upload_to='reports', blank=True, null=True)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey('Project')

    @property
    def title(self):
        return '{user}_{project}_{month}_{year}.txt' \
            .format(
                user=self.worker.username,
                project=self.project.title,
                month=get_month_abbr(self.month),
                year=self.year
            )

    def save(self, *args, **kwargs):
        _, last_month_day = get_month_days(self.year, self.month)

        report_period_start = datetime(self.year, self.month, 1, tzinfo=tz)
        report_period_end = datetime(
            self.year, self.month, last_month_day, 23, 59, 59, tzinfo=tz)

        spent_times = SpentTime.objects.filter(
            task__project=self.project, worker=self.worker,
            start_time__gte=report_period_start,
            end_time__lte=report_period_end)

        data = {
            'month': get_month_name(self.month),
            'year': self.year,
            'spent_times': sorted(spent_times, reverse=True),
            'month_hours': sum([x.duration for x in spent_times])
        }

        tpl = get_template('timesheet/report.txt')
        report_text = tpl.render(Context(data))

        if self.filename:
            self.filename.delete(save=False)

        self.filename.save(
            self.title, ContentFile(report_text), save=False
        )
        super(MonthlyReport, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-month', 'project__title']


class MonthlyInvoice(models.Model):
    company = models.ForeignKey('Company')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL)
    filename = models.FileField(upload_to='invoices', blank=True, null=True)
    year = models.PositiveSmallIntegerField(default=current_year)
    month = models.PositiveSmallIntegerField(default=current_month,
                                             choices=MONTH)
    currency_equivalent = models.CharField(blank=True, null=True, max_length=3,
                                           choices=CURRENCY)
    date = models.DateTimeField(default=current_datetime,
                                help_text='invoice sending date')
    number = models.PositiveSmallIntegerField(default=1)

    @property
    def title(self):
        return '{user}_{company}_{month}_{year}_Invoice.pdf' \
            .format(
                user=self.worker.username,
                company=self.company.title,
                month=get_month_abbr(self.month),
                year=self.year
            )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-month', 'company__title']


class InvoiceData(models.Model):
    address = models.CharField(max_length=120, blank=True, null=True)
    tax_or_vat_id = models.CharField(max_length=20, blank=True, null=True)
    contact_name = models.CharField(max_length=120, blank=True, null=True)
    mention_name = models.CharField(max_length=120, blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    paypal = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.entity.__str__()

    class Meta:
        abstract = True
        verbose_name = 'invoice extra data'


class UserInvoiceData(InvoiceData):
    entity = models.OneToOneField(settings.AUTH_USER_MODEL)


class CompanyInvoiceData(InvoiceData):
    entity = models.OneToOneField('Company')


class Salary(models.Model):
    company = models.ForeignKey('Company')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL)
    position = models.CharField(blank=True, null=True, max_length=50)
    hourly_rate = models.FloatField()
    currency = models.CharField(max_length=3, choices=CURRENCY)

    def __str__(self):
        return '%s - %s %s per hour' % (
            self.worker, self.hourly_rate, self.currency)

    class Meta:
        verbose_name = 'salary'
        verbose_name_plural = 'salaries'
