from django.conf.urls import patterns, url

urlpatterns = patterns('main.json_views',
                       url(r'^status_reports/$', 'status_collection'),
                       url(r'^status_reports/(?P<id>[0-9]+)$', 'status_member'),
                       )