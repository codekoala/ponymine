from django.db import models
from django.contrib.auth.models import User, Permission

class ProjectManager(models.Manager):
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
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    class Meta:
        ordering = ('parent', 'name',)

class Role(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField()
    permissions = models.ManyToManyField(Permission)

    class Meta:
        ordering = ('name',)

class Membership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    role = models.ForeignKey(Role)

class Tracker(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)

class Status(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)

class PriorityManager(models.Manager):
    def default(self):
        return self.get_query_set().get(is_default=True)

class Priority(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField()
    is_default = models.BooleanField(default=False)

    objects = PriorityManager()

    def save(self, *args, **kwargs):
        if self.is_default:
            # mark all other priorities as not being the default
            Priority.objects.exclude(pk=self.id).update(is_default=False)

        super(Priority, self).save(*args, **kwargs)

    class Meta:
        ordering = ('name',)

class Category(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=30)
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)

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
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_created',)

class Log(models.Model):
    ticket = models.ForeignKey(Ticket)
    old_status = models.ForeignKey(Status, related_name='old_statuses')
    new_status = models.ForeignKey(Status, related_name='new_statuses')
    old_priority = models.ForeignKey(Priority, related_name='old_priorities')
    new_priority = models.ForeignKey(Priority, related_name='new_priorities')
    old_assigned_to = models.ForeignKey(User, related_name='old_assignees')
    new_assigned_to = models.ForeignKey(User, related_name='new_assignees')
    old_category = models.ForeignKey(Category, related_name='old_categories')
    new_category = models.ForeignKey(Category, related_name='new_categories')
    old_completion = models.CharField(max_length=4)
    new_completion = models.CharField(max_length=4)
    date_created = models.DateTimeField(auto_now_add=True)