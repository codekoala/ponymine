from django.conf.urls.defaults import *
from views import projects, tickets, main
from forms import UpdateTicketForm

urlpatterns = patterns('',
    url(r'^project/new/$', projects.create_project, name='ponymine_create_project'),
    url(r'^project/(?P<path>.+)/edit/$', projects.edit_project, name='ponymine_edit_project'),
    url(r'^project/(?P<path>.+)/$', projects.view_project, name='ponymine_view_project'),
    url(r'^project/(?P<path>.+)/page/(?P<page>\d+)/$', projects.view_project,
        name='ponymine_view_project_page'),

    url(r'^ticket/(?P<path>.+)/new/$', tickets.create_ticket, name='ponymine_create_ticket'),
    url(r'^ticket/(?P<ticket_id>\d+)/edit/$', tickets.edit_ticket, name='ponymine_edit_ticket'),
    url(r'^ticket/(?P<ticket_id>\d+)/update/$',
        tickets.edit_ticket,
        {'form_class': UpdateTicketForm},
        name='ponymine_update_ticket'),
    url(r'^ticket/(?P<ticket_id>\d+)/$', tickets.view_ticket, name='ponymine_view_ticket'),

    url(r'^keyword/(?P<keyword>.*)/page/(?P<page>\d+)/$', tickets.tickets_with_keyword,
        name='ponymine_tickets_with_keyword_page'),
    url(r'^keyword/(?P<keyword>.*)/$', tickets.tickets_with_keyword, name='ponymine_tickets_with_keyword'),

    url(r'^$', main.overview, name='ponymine_overview'),
)
