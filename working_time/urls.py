from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve as django_static_serve

urlpatterns = [
    # Examples:
    # url(r'^$', 'working_time.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', django_static_serve,
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
]
