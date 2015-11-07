from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings

from .signals import save_spent_time, create_montly_report, \
    create_montly_invoice
from .choices import STATUS, PRIORITY, MONTH, CURRENCY
from .utils.datetime_helpers import tz, current_datetime, current_month, \
    current_year, get_month_abbr


class SpentTime(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(default=current_datetime)
    comment = models.CharField(max_length=200)
    duration = models.FloatField(default=0)
    task = models.ForeignKey('Task', related_name='times')

    @property
    def cost(self):
        employer = self.task.project.company
        if employer:
            return '%.2f %s' % (self.duration * employer.hourly_rate,
                                employer.salary_currency)

    @property
    def times(self):
        return '%s - %s' % (self.start_time.astimezone(tz).strftime('%H:%M'),
                            self.end_time.astimezone(tz).strftime('%H:%M'))

    @property
    def day(self):
        return self.start_time.astimezone(tz).strftime('%Y-%m-%d')

    @property
    def title(self):
        return str(self)

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
    hourly_rate = models.FloatField(blank=True, null=True)
    salary_currency = models.CharField(blank=True, null=True,
                                       max_length=3, choices=CURRENCY)
    invoice_abbr = models.CharField(max_length=20, blank=True, null=True)

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


# Please declare signals here, do not put them to __init__.py:
pre_save.connect(save_spent_time, sender=SpentTime)
pre_save.connect(create_montly_report, sender=MonthlyReport)
pre_save.connect(create_montly_invoice, sender=MonthlyInvoice)
