import warnings
import unicodedata

from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.core.files.base import ContentFile

from .choices import STATUS, PRIORITY, MONTH, CURRENCY
from .utils.datetime_helpers import tz, current_datetime, current_month, \
    current_year, get_month_abbr, get_month_days, get_month_name

from .utils.pdf_helpers import inverse_y, draw_header, draw_items_header, \
    draw_legal_parties_info, draw_item, draw_items, draw_footer, draw, \
    create_invoice, draw_bonuses


currency_sign = {
    'USD': '$',
    'EUR': unicodedata.lookup('EURO SIGN'),
    #  python unicodedata still not support ruble sign
    # 'RUB': unicodedata.lookup('RUBLE SIGN')
}


class SpentTime(models.Model):
    """
    Feature request:
        - workers can track their working time only for tasks,
          for which of them are participants(on Redmine maner),
          maybe this should be realized on the project level and
          potentially workers can work on all project tasks...
    """
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
            return '%.3f %s' % (self.duration * salary[0].hourly_rate,
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
    abbr = models.SlugField(blank=True, null=True,
                            help_text='company abbreviation')

    @property
    def slug(self):
        return self.abbr if self.abbr else self.title.replace(' ', '_')

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
    amount_equivalent = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(default=current_datetime,
                                help_text='invoice sending date')
    timestamp = models.DateTimeField(default=current_datetime,
                                     help_text='invoice timestamp')
    number = models.PositiveSmallIntegerField(default=1)

    @property
    def title(self):
        return '{user}_{company}_{month}_{year}_Invoice.pdf' \
            .format(
                user=self.worker.username,
                company=self.company.slug,
                month=get_month_abbr(self.month),
                year=self.year
            )

    @property
    def projects_amount(self):
        _, last_month_day = get_month_days(self.year, self.month)
        report_period_start = datetime(self.year, self.month, 1, tzinfo=tz)
        report_period_end = datetime(
            self.year, self.month, last_month_day, 23, 59, 59, tzinfo=tz)

        projects = set(self.company.projects.filter(
            tasks__times__worker=self.worker,
            tasks__times__start_time__gte=report_period_start,
            tasks__times__end_time__lte=report_period_end))

        data = list()
        for project in projects:
            project_info = {'project': project, 'hours': 0, 'amount': 0,
                            'currency': '-//-', 'hourly_rate': '-//-'}
            salary = self.company.salary_set.filter(worker=self.worker)
            if salary:
                if salary[0].currency != 'RUB':
                    project_info['hourly_rate'] = '%s%.2f' % (
                        currency_sign.get(salary[0].currency, '?'),
                        salary[0].hourly_rate)
                else:
                    project_info['hourly_rate'] = '%.2f %s' % (
                        salary[0].hourly_rate, salary[0].currency)
            for spent_time in SpentTime.objects.filter(
                    task__project=project, worker=self.worker,
                    start_time__gte=report_period_start,
                    end_time__lte=report_period_end):
                #  in most common cases, a company will pay salary for their
                #  employees in one currency, no matter from type of working
                #  activity or their positions, so we just save currency
                #  expecting that it is constant
                if spent_time.cost != '-//-':
                    amount, project_info['currency'] = spent_time.cost.split()
                    project_info['amount'] += float(amount)
                else:
                    project_info['currency'] = '?'
                    project_info['amount'] = 0
                project_info['hours'] += spent_time.duration

            if project_info['currency'] != 'RUB':
                project_info['currency'] = currency_sign.get(
                    project_info['currency'], '?')

            data.append(project_info)
        return data

    @property
    def amount_eq(self):
        if self.amount_equivalent and self.currency_equivalent:
            if self.currency_equivalent != 'RUB':
                return '%s%.2f' % (
                    currency_sign.get(self.currency_equivalent, '?'),
                    self.amount_equivalent)
            return '%.2f %s' % (
                self.amount_equivalent, self.currency_equivalent)

    @property
    def amount(self):
        projects_data = self.projects_amount
        if projects_data:
            worker_total_amount = sum([x['amount'] for x in projects_data])
            project_info = projects_data[0]
            if project_info['currency'] != 'RUB':
                return '%s%.2f' % (
                    project_info['currency'], worker_total_amount)
            else:
                return '%.2f %s' % (
                    worker_total_amount, project_info['currency'])
        return '?0.00'

    @property
    def bonuses(self):
        return self.company.bonuses.filter(
            date__year=self.year, date__month=self.month, worker=self.worker)

    def save(self, *args, **kwargs):
        if self.filename:
            self.filename.delete(save=False)

        self.filename = self.create_invoice()
        super(MonthlyInvoice, self).save(*args, **kwargs)

    inverse_y = inverse_y
    draw_header = draw_header
    draw_legal_parties_info = draw_legal_parties_info
    draw_items_header = draw_items_header
    draw_item = draw_item
    draw_items = draw_items
    draw_footer = draw_footer
    draw = draw
    create_invoice = create_invoice
    draw_bonuses = draw_bonuses

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
    entity = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='iv_data')


class CompanyInvoiceData(InvoiceData):
    entity = models.OneToOneField('Company', related_name='iv_data')


class Salary(models.Model):
    """
    Feature request:
        - salary should be as more as possible close to the user profile,
          we want fill this data on the user settings page
          as well as we fill the user invoice data there...
    """
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


class Bonus(models.Model):
    """
    Bonuses! =)
    """
    amount = models.FloatField()
    currency = models.CharField(max_length=3, choices=CURRENCY)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL)
    company = models.ForeignKey('Company', related_name='bonuses')
    date = models.DateTimeField(default=current_datetime,
                                help_text='bonus date')

    @property
    def currency_sign(self):
        return currency_sign.get(self.currency, '?')

    def __str__(self):
        return '%s - %.2f %s %s' % (
            self.worker, self.amount, self.currency,
            self.date.strftime('%Y-%m-%d'))

    class Meta:
        verbose_name = 'bonus'
        verbose_name_plural = 'bonuses'
