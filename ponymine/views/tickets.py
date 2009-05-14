from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from ponymine.forms import TicketForm, UpdateTicketForm, ChangeStatusForm
from ponymine.models import Project, Ticket, Status
from ponymine import utils
import copy

def view_ticket(request, ticket_id, template='ponymine/ticket_detail.html'):
    """
    Displays a ticket
    """
    data = {}
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    data['ticket'] = ticket
    data['project'] = ticket.project
    data['change_status_form'] = ChangeStatusForm()

    return render(template, data, context_instance=RequestContext(request))

@permission_required('ponymine.add_ticket')
def create_ticket(request, path, template='ponymine/edit_ticket.html',
    redirect_url=None):
    """
    Wraps `edit_ticket` so that we can use a different decorator
    """
    project = Project.objects.with_path(path)
    return edit_ticket(request,
                       project=project,
                       template=template,
                       redirect_url=redirect_url)

@permission_required('ponymine.change_ticket')
def edit_ticket(request, ticket_id=None, project=None,
    template='ponymine/edit_ticket.html', redirect_url=None,
    form_class=TicketForm):
    """
    Creates or modifies a ticket
    """
    data = {}

    # get the ticket
    if ticket_id:
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        project = ticket.project
    else:
        ticket = Ticket(project=project)

    data['ticket'] = ticket

    if request.method == "POST":
        form = form_class(request.POST, instance=ticket)
        if form.is_valid():
            # copy the existing ticket so we can make the change log
            old_ticket = copy.copy(ticket)

            # create or update the ticket
            new_ticket = form.save(commit=False)
            if not new_ticket.id:
                new_ticket.reported_by = request.user
            new_ticket.save()

            # log any differences between the tickets
            utils.create_change_logs(request,
                                     old_ticket,
                                     new_ticket,
                                     form.cleaned_data.get('notes', ''))

            # determine where the user should go after saving the ticket
            if not redirect_url:
                redirect_url = new_ticket.get_absolute_url()

            return HttpResponseRedirect(redirect_url)
    else:
        # set the ticket's status based on the query string
        status_id = request.GET.get('status', None)
        if status_id:
            ticket.status = Status.objects.get(pk=int(status_id))
        form = form_class(instance=ticket)

    # limit which users can be assigned a ticket
    project_member_ids = [u.id for u in project.members.all()]
    members = User.objects.filter(pk__in=project_member_ids)
    form.limit_assignable_users(members)

    data['form'] = form
    data['project'] = project

    return render(template, data, context_instance=RequestContext(request))

def tickets_with_keyword(request, keyword, page=1,
    template='ponymine/tickets_with_keyword.html'):
    """
    Searches for tickets with a particular keyword.
    """
    data = {}

    tickets = Ticket.objects.filter(keywords__icontains=keyword)
    paginator = Paginator(tickets, 50, orphans=5)
    page_obj = paginator.page(page)

    data['page'] = page_obj
    data['paginator'] = paginator
    data['object_list'] = page_obj.object_list

    return render(template, data, context_instance=RequestContext(request))
