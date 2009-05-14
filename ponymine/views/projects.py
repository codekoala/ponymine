from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.forms.formsets import formset_factory
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from ponymine.forms import ProjectForm, MembershipForm
from ponymine.models import Project, Membership, Ticket

def project_list(request, page=1, template='ponymine/project_list.html'):
    """
    Displays a list of projects
    """
    data = {}

    # TODO: make this retrieve all projects that a user has access to
    # (think membership in private projects)
    projects = Project.objects.public()
    paginator = Paginator(projects, 50, orphans=5)
    page_obj = paginator.page(page)

    data['page'] = page_obj
    data['paginator'] = paginator
    data['project_list'] = page_obj.object_list

    return render(template, data, context_instance=RequestContext(request))

def view_project(request, path, page=1, template='ponymine/project_detail.html'):
    """
    Displays information about the project indicated by `path`
    """
    data = {}

    project = Project.objects.with_path(path)

    # raise a 404 if no project matches the path
    if not project:
        raise Http404()

    # get a list of tickets for this project
    tickets = Ticket.objects.filter(project=project)
    paginator = Paginator(tickets, 50, orphans=5)
    page_obj = paginator.page(page)

    data['project'] = project
    data['page'] = page_obj
    data['paginator'] = paginator
    data['ticket_list'] = page_obj.object_list

    return render(template, data, context_instance=RequestContext(request))

@permission_required('ponymine.add_project')
def create_project(request, template='ponymine/edit_project.html',
    redirect_url=None):
    """
    Wraps `edit_project` so that we can use a different decorator
    """
    return edit_project(request, template=template, redirect_url=redirect_url)

@permission_required('ponymine.change_project')
def edit_project(request, path=None, template='ponymine/edit_project.html',
    redirect_url=None, form_class=ProjectForm):
    """
    Allows authorized users to create and edit projects
    """
    data = {}
    project = None

    if path:
        project = Project.objects.with_path(path)

    # `with_path` may return None, so this ensures that we always have a project
    project = project or Project()

    user_count = User.objects.count()
    MembershipFormSet = formset_factory(MembershipForm,
                                        extra=5,
                                        max_num=user_count)

    if request.method == 'POST':
        form = form_class(request.POST, instance=project)
        memberships = MembershipFormSet(request.POST,
                                        prefix='memberships')

        if form.is_valid() and memberships.is_valid():
            new_proj = form.save()

            # clear the previous memberships
            Membership.objects.filter(project=new_proj).delete()

            # set the memberships for this project
            for info in memberships.cleaned_data:
                # make sure we're not supposed to be removing this membership
                if not info['remove']:
                    membership = Membership.objects.create(
                                    project=new_proj,
                                    user=info['user'],
                                    role=info['role'])

            # redirect the user to the proper page
            if not redirect_url:
                redirect_url = new_proj.get_absolute_url()

            return HttpResponseRedirect(redirect_url)
    else:
        form = form_class(instance=project)

        if project.id:
            mems = Membership.objects.filter(project=project)
            initial = [dict(user=m.user.id, role=m.role.id) for m in mems]
        else:
            initial = []
        memberships = MembershipFormSet(initial=initial,
                                        prefix='memberships')
        #~ raise Exception(initial)

    # try to reduce the chance of a project having itself as a parent
    form.update_parents(project)

    data['project'] = project
    data['form'] = form
    data['membership_forms'] = memberships

    return render(template, data, context_instance=RequestContext(request))
