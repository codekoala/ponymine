from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from managers import ProjectManager, AttributeWithDefaultManager

# we use this a lot...
BLNL = dict(blank=True, null=True)

class Project(models.Model):
    """
    Offers a way to group tickets according to particular projects.
    """
    parent = models.ForeignKey('self', related_name='subprojects', **BLNL)
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    homepage = models.URLField(verify_exists=True, **BLNL)
    members = models.ManyToManyField(User, through='Membership')
    is_public = models.BooleanField(default=False, help_text=_('If this project is a child of any project that is private, it too will be private automatically.'))
    is_active = models.BooleanField(default=True)
    site = models.ForeignKey(Site, default=Site.objects.get_current)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    def __unicode__(self):
        return self.hierarchy_str

    def get_absolute_url(self):
        return ('ponymine_view_project_summary', [], {'path': self.path})
    get_absolute_url = models.permalink(get_absolute_url)

    def is_member(self, user):
        return bool(user.is_superuser or user in self.members.all())

    def get_path_list(self):
        """
        Returns a list of project slugs that act as the "path" to this project
        """
        return tuple(p.slug for p in self.hierarchy)

    def _get_path(self):
        return '/'.join(self.get_path_list())
    path = property(_get_path)

    def _get_hierarchy(self):
        me = (self,)
        if self.parent:
            return self.parent.hierarchy + me
        return me
    hierarchy = property(_get_hierarchy)

    def _get_hierarchy_str(self):
        names = [p.name for p in self.hierarchy]
        return u': '.join(names)
    hierarchy_str = property(_get_hierarchy_str)

    def save(self, *args, **kwargs):
        """
        Ensures that a project which is a descendant of a private project is
        always marked private as well.
        """
        if self.is_public:
            for project in self.hierarchy:
                if not project.is_public:
                    self.is_public = False
                    print 'HERE!!'
                    break

        super(Project, self).__init__(*args, **kwargs)

    class Meta:
        ordering = ('name',)
        unique_together = ('parent', 'slug')
        permissions = (
            ('configure_project', _('Can configure project')),
        )

class Attribute(models.Model):
    """
    A generic, abstract model that many classes will inherit from.  This class
    has no table in the database.
    """
    name = models.CharField(max_length=30)
    slug = models.SlugField()

    def __unicode__(self):
        return self.name

    class Meta:
        # ordering should be inherited by all children
        ordering = ('name',)
        abstract = True

class AttributeWithDefault(Attribute):
    is_default = models.BooleanField(default=False)

    objects = AttributeWithDefaultManager()

    def save(self, *args, **kwargs):
        """
        Ensures that there is only one default object
        """
        if self.is_default:
            # mark all other objects as not being the default
            self.__class__.objects.exclude(pk=self.id).update(is_default=False)

        super(AttributeWithDefault, self).save(*args, **kwargs)

    class Meta:
        # ordering should be inherited by all children
        ordering = ('name',)
        abstract = True

class Role(AttributeWithDefault):
    """
    Behaves much like the Group object in the django.contrib.auth application,
    except it has some special functionality for Ponymine.
    """
    permissions = models.ManyToManyField(Permission)

class Membership(models.Model):
    """
    Determines how a user is related to a project.
    """
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    role = models.ForeignKey(Role, default=Role.objects.default)

class TicketType(AttributeWithDefault):
    """
    Represents a type of ticket--bug, feature request, maintenance, etc.
    """
    pass

class Status(AttributeWithDefault):
    """
    Represents the state of a ticket--new, assigned, resolved, etc.
    """
    is_closed = models.BooleanField(blank=True, default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order', 'name',)
        verbose_name_plural = 'statuses'

class Priority(AttributeWithDefault):
    """
    Represents the priority of a ticket--high, medium, low, etc.
    """
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('-order', 'name')
        verbose_name_plural = 'priorities'

class Component(Attribute):
    """
    Per-project ticket components--UI, documentation, etc.
    """
    project = models.ForeignKey(Project)

    class Meta:
        ordering = ('name',)
        unique_together = ('name', 'project')

class TicketManager(models.Manager):
    """
    This manager is here so we avoid cyclic imports (with Status)
    """
    def __init__(self, *args, **kwargs):
        super(TicketManager, self).__init__(*args, **kwargs)
        self.closed = [st.id for st in Status.objects.filter(is_closed=True)]

    def closed(self, user=None):
        qs = self.get_query_set().filter(status__id__in=self.closed)
        return self._filter_for_user(qs, user)

    def open(self, user=None):
        qs = self.get_query_set().exclude(status__id__in=self.closed)
        return self._filter_for_user(qs, user)

    def _filter_for_user(self, qs, user=None):
        """
        Finds tickets that this user has based on the projects that the user
        is a member of in some way.
        """
        if isinstance(user, User):
            user_project_ids = [m.project.id for m in user.membership_set.all()]
            qs = qs.filter(project__id__in=user_project_ids)
        return qs.distinct()

class Ticket(models.Model):
    project = models.ForeignKey(Project, related_name='tickets')
    ticket_type = models.ForeignKey(TicketType, default=TicketType.objects.default)
    component = models.ForeignKey(Component, **BLNL)
    reported_by = models.ForeignKey(User, related_name='reported_tickets', **BLNL)
    assigned_to = models.ForeignKey(User, related_name='assigned_tickets', **BLNL)
    status = models.ForeignKey(Status, default=Status.objects.default)
    priority = models.ForeignKey(Priority, default=Priority.objects.default)
    subject = models.CharField(max_length=100)
    description = models.TextField()
    keywords = models.CharField(max_length=200, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = TicketManager()

    def __unicode__(self):
        return u'%s #%i - %s' % (self.ticket_type, self.id, self.subject)

    def get_absolute_url(self):
        return ('ponymine_view_ticket', [], {'ticket_id': self.id})
    get_absolute_url = models.permalink(get_absolute_url)

    def _is_closed(self):
        return self.status.is_closed
    is_closed = property(_is_closed)

    def keyword_list(self):
        return self.keywords.split(',')

    class Meta:
        ordering = ('-priority__order', '-date_created',)

class Log(models.Model):
    """
    Maintains a history of changes to a ticket.
    """
    ticket = models.ForeignKey(Ticket)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, **BLNL)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

class ChangeLog(models.Model):
    """
    Keeps track of which attributes about a ticket have changed.
    """
    TYPES = {
        'component': _('Component'),
        'priority': _('Priority'),
        'project': _('Project'),
        'status': _('Status'),
        'ticket type': _('Ticket Type'),
        'user': _('Assigned To'),
    }

    log = models.ForeignKey(Log, related_name='changes')
    content_type = models.ForeignKey(ContentType, null=True)
    old_id = models.PositiveIntegerField(null=True)
    new_id = models.PositiveIntegerField(null=True)
    old_object = generic.GenericForeignKey(ct_field='content_type', fk_field='old_id')
    new_object = generic.GenericForeignKey(ct_field='content_type', fk_field='new_id')

    def _get_attribute_label(self):
        """
        Returns a label that makes sense for tickets based on the content
        type.  This also helps with internationalization.
        """
        return ChangeLog.TYPES.get(self.content_type.name,
                                   _(self.content_type.name))
    label = property(_get_attribute_label)

    def __unicode__(self):
        return u'%s: %s (%s => %s)' % (self.log.ticket,
                                       self.content_type,
                                       self.old_object,
                                       self.new_object)
