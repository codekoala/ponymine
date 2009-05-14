from django.core.paginator import Paginator
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from ponymine.models import Project, Ticket

def overview(request, template='ponymine/overview.html'):
    """
    Offers a quick overview of the goings on in Ponymine to the user.
    """
    data = {}

    # TODO: make this get all projects to which a user has access
    # (think membership of private projects)
    # get 5 projects
    proj_paginator = Paginator(Project.objects.public(), 5, orphans=3)
    proj_page = proj_paginator.page(1)

    # get 5 latest tickets
    tick_paginator = Paginator(Ticket.objects.open(), 5)
    tick_page = tick_paginator.page(1)

    data['projects'] = {
            'paginator': proj_paginator,
            'page': proj_page
        }
    data['latest_tickets'] = {
            'paginator': tick_paginator,
            'page': tick_page
        }

    # get a list of recent ticket if the user is authenticated
    if request.user.is_authenticated():
        qs = Ticket.objects.open()
        qs = qs.filter(assigned_to=request.user).order_by('-date_created')
        my_paginator = Paginator(qs, 5)
        my_page = my_paginator.page(1)

        data['my_tickets'] = {
            'paginator': my_paginator,
            'page': my_page
        }

    return render(template, data, context_instance=RequestContext(request))
