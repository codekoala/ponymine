from django.conf.urls.defaults import *
from views import projects, tickets, main
from forms import UpdateTicketForm

urlpatterns = patterns('',
    url(r'^project/new/$', projects.create_project, name='ponymine_create_project'),
    url(r'^project/(?P<path>.+)/settings/$', projects.configure_project,
        name='ponymine_configure_project'),
    url(r'^project/(?P<path>.+)/edit/$', projects.edit_project, name='ponymine_edit_project'),
    url(r'^project/(?P<path>.+)/tickets/$', projects.view_project_tickets,
        name='ponymine_view_project_tickets'),
    url(r'^project/(?P<path>.+)/tickets/page/(?P<page>\d+)/$', projects.view_project_tickets,
        name='ponymine_view_project_ticket_page'),
    url(r'^project/(?P<path>.+)/$', projects.project_summary,
        name='ponymine_view_project_summary'),

    url(r'^projects/(?P<page>\d+)/$', projects.project_list, name='ponymine_project_list_page'),
    url(r'^projects/$', projects.project_list, name='ponymine_project_list'),

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
