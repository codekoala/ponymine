from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^project/(?P<path>.+)/$', views.view_project, name='ponymine_view_project'),
    url(r'^ticket/new/$', views.edit_ticket, name='ponymine_create_ticket'),
    url(r'^ticket/(?P<ticket_id>\d+)/edit/$', views.edit_ticket, name='ponymine_edit_ticket'),
    url(r'^ticket/(?P<ticket_id>\d+)/$', views.view_ticket, name='ponymine_view_ticket'),
    url(r'^$', views.overview, name='ponymine_overview'),
)