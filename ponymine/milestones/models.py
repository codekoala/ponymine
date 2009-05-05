from django.db import models
from ponymine.models import Project, Ticket

class Milestone(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=75)
    due_date = models.DateField(blank=True, null=True)
    description = models.TextField()
    is_complete = models.BooleanField(default=False, blank=True)
    
    class Meta:
        ordering = ('-due_date', 'name')

if not getattr(Ticket, 'milestone', None):
    # Add a milestone column to our Ticket class if it hasn't been added yet
    Ticket.add_to_class('milestone', models.ForeignKey(Milestone, blank=True, null=True))