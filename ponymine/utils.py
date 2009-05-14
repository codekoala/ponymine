from django.contrib.contenttypes.models import ContentType
from ponymine.models import Log, ChangeLog

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
