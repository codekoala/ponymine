from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site

class ProjectManager(models.Manager):
    def get_query_set(self):
        return super(ProjectManager, self).get_query_set().filter(site__exact=Site.objects.get_current())

    def active(self):
        return self.get_query_set().filter(is_active=True)

    def public(self):
        return self.active().filter(is_public=True)

    def private(self):
        return self.active().filter(is_public=False)

class Project(models.Model):
    parent = models.ForeignKey('self', related_name='subprojects')
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.CharField(max_length=4000, blank=True)
    homepage = models.URLField(blank=True, verify_exists=True)
    members = models.ManyToManyField(User, through='Membership')
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(Site, default=Site.objects.get_current)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    class Meta:
        ordering = ('parent', 'name',)

class Attribute(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField()

    class Meta:
        # ordering should be inherited by all children
        ordering = ('name',)
        abstract = True

class Role(Attribute):
    permissions = models.ManyToManyField(Permission)

class Membership(models.Model):
    """
    Determines how a user is related to a project.
    """
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    role = models.ForeignKey(Role)

class Tracker(Attribute):
    """
    Represents a type of ticket--bug, feature request, maintenance, etc.
    """
    pass

class Status(Attribute):
    """
    Represents the state of a ticket--new, assigned, resolved, etc.
    """
    pass

class PriorityManager(models.Manager):
    def default(self):
        try:
            return self.get_query_set().get(is_default=True)
        except Priority.DoesNotExist:
            return None

class Priority(Attribute):
    """
    Represents the priority of a ticket--high, medium, low, etc.
    """
    is_default = models.BooleanField(default=False)

    objects = PriorityManager()

    def save(self, *args, **kwargs):
        """
        Ensures that there is only one default priority.
        """
        if self.is_default:
            # mark all other priorities as not being the default
            Priority.objects.exclude(pk=self.id).update(is_default=False)

        super(Priority, self).save(*args, **kwargs)

class Category(Attribute):
    """
    Per-project ticket categories--GUI, documentation, etc.
    """
    project = models.ForeignKey(Project)

class Ticket(models.Model):
    project = models.ForeignKey(Project, related_name='tickets')
    tracker = models.ForeignKey(Tracker)
    status = models.ForeignKey(Status)
    priority = models.ForeignKey(Priority, default=Priority.objects.default)
    assigned_to = models.ForeignKey(User, blank=True, null=True)
    category = models.ForeignKey(Category, blank=True, null=True)
    subject = models.CharField(max_length=100)
    description = models.CharField(max_length=5000)
    completion = models.CharField(max_length=4, default='0%')
    due_date = models.DateField(blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_created',)

class Log(models.Model):
    ticket = models.ForeignKey(Ticket)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

class ChangeLog(models.Model):
    log = models.ForeignKey(Log, related_name='changes')
    content_type = models.ForeignKey(ContentType)
    old_id = models.PositiveIntegerField()
    new_id = models.PositiveIntegerField()
    old_object = generic.GenericForeignKey(ct_field='content_type', fk_field='old_id')
    new_object = generic.GenericForeignKey(ct_field='content_type', fk_field='new_id')