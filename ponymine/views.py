from django.http import Http404
from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from models import Project, Ticket

def overview(request, template='ponymine/overview.html'):
    """
    Offers a quick overview of the goings on in Ponymine to the user.
    """
    
    return render(template, {}, context_instance=RequestContext(request))

def view_project(request, path, template="ponymine/project_detail.html"):
    """
    Displays information about the project indicated by `path`
    """
    project = Project.objects.with_path(path.split('/'))
    
    # raise a 404 if no project matches the path
    if not project: raise Http404()
    
    return render(template, {
                    'project': project,
                  }, context_instance=RequestContext(request))

def view_ticket(request, ticket_id, template='ponymine/ticket_detail.html'):
    """
    Displays a ticket
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    
    return render(template, {
                    'ticket': ticket,
                  }, context_instance=RequestContext(request))