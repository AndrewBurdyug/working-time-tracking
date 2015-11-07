from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.timezone import get_current_timezone
from .models import SpentTime, Category, Task, Project, MonthlyReport, \
    MonthlyInvoice, Company, CompanyInvoiceData, UserInvoiceData


tz = get_current_timezone()
UserModel = get_user_model()


class SpentTimeAdmin(admin.ModelAdmin):
    list_display = ('day', 'times', 'duration_pretty', 'cost', 'task',
                    'comment')
    list_filter = ('start_time', 'task__project__company', 'task__project')
    date_hierarchy = 'start_time'

    def duration_pretty(self, obj):
        return '%.1f h' % obj.duration

    duration_pretty.short_description = 'Duration'


class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report')

    def report(self, obj):
        return '<a href="{url}">{url}</a'.format(url=obj.filename.url)

    report.short_description = 'Report'
    report.allow_tags = True


class MonthlyInvoiceAdmin(MonthlyReportAdmin):
    pass


class TaskAdmin(admin.ModelAdmin):
    list_display = ('title_pretty', 'progress', 'priority', 'status')
    list_filter = ('project__company', 'project')

    def title_pretty(self, obj):
        return str(obj)

    title_pretty.short_description = 'Title'


class CompanyInvoiceDataInline(admin.StackedInline):
    model = CompanyInvoiceData
    can_delete = False
    verbose_name_plural = 'additional info'


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('title', 'hourly_rate_pretty')
    inlines = (CompanyInvoiceDataInline, )

    def hourly_rate_pretty(self, obj):
        return '%.2f %s/h' % (obj.hourly_rate, obj.salary_currency)

    hourly_rate_pretty.short_description = 'Hourly Rate'


class UserInvoiceDataInline(admin.StackedInline):
    model = UserInvoiceData
    can_delete = False
    verbose_name_plural = 'additional info'


class ExtendedUserAdmin(UserAdmin):
    inlines = (UserInvoiceDataInline, )

admin.site.register(SpentTime, SpentTimeAdmin)
admin.site.register(Category)
admin.site.register(Task, TaskAdmin)
admin.site.register(Project)
admin.site.register(MonthlyReport, MonthlyReportAdmin)
admin.site.register(MonthlyInvoice, MonthlyInvoiceAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.unregister(UserModel)
admin.site.register(UserModel, ExtendedUserAdmin)
