from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from ponymine.models import Log, ChangeLog, Project

def get_project_or_new(path, user=None):
    """
    Attempts to find a project described by `path`.  If one cannot be found,
    an empty Project object is returned.
    """
    project = None

    if path:
        project = Project.objects.with_path(path, user)

    # `with_path` may return None, so this ensures that we always have a project
    project = project or Project()

    return project

def check_membership(project, user):
    """
    Raises an HTTP 404 error if `user` is not a member of `project` and the
    project is not public.
    """
    if not project.is_public and not project.is_member(user):
        raise Http404

def create_change_logs(request, old_ticket, new_ticket, notes=''):
    """
    Looks for differences between two Ticket objects and creates a log of each
    important difference that is detected.
    """
    if old_ticket.id and old_ticket.id == new_ticket.id:
        log = Log.objects.create(
                    ticket=new_ticket,
                    notes=notes,
                    created_by=request.user
                )

        # ticket attributes to pay attention to
        to_check = ('project', 'ticket_type', 'component',
                    'assigned_to', 'status', 'priority')

        for attr in to_check:
            old_val = getattr(old_ticket, attr, None)
            new_val = getattr(new_ticket, attr, None)

            # don't log things that haven't changed
            if old_val == new_val:
                continue

            model = old_val or new_val
            if model:
                change = ChangeLog(log=log)
                ctype = ContentType.objects.get_for_model(model)
                change.content_type = ctype
                change.old_id = getattr(old_val, 'id', None)
                change.new_id = getattr(new_val, 'id', None)
                change.old_object = old_val
                change.new_object = new_val
                change.save()
