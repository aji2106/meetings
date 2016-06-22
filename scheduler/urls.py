from django.conf.urls import url
from . import views

app_name = 'scheduler'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^schedule/$', views.schedule_config, name='schedule_config'),
    url(r'^schedule/save/$', views.schedule_save, name='schedule_save'),
    url(r'^meeting/$', views.meeting_config, name='meeting_config'),
    url(r'^meeting/new/$', views.meeting_save, name='meeting_save_new'),
    url(r'^meeting/(?P<meeting_id>\d+)/edit/$', views.meeting_edit, name='meeting_edit'),
    url(r'^meeting/(?P<meeting_id>\d*)/save/$', views.meeting_save, name='meeting_save'),
    url(r'^meeting/(?P<meeting_id>\d+)/delete/$', views.meeting_delete, name='meeting_delete'),
]
