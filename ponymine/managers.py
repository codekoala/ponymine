from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

class ProjectManager(models.Manager):
    def get_query_set(self):
        return super(ProjectManager, self).get_query_set().filter(site__exact=Site.objects.get_current())

    def active(self, user=None):
        qs = self.get_query_set().filter(is_active=True)

        # refine the list based on the current user
        if isinstance(user, User):
            # superusers have access to everything
            if not user.is_superuser:
                user_project_ids = [m.project.id for m in user.membership_set.all()]
                qs = qs.filter(pk__in=user_project_ids)

        return qs.distinct()

    def for_user(self, user=None):
        """
        Returns a QuerySet for projects based on `user`.  If the user is logged
        in, they should get a QuerySet with all projects to which the user has
        access.  If the user is not logged in, only public projects will be
        returned.
        """
        if isinstance(user, User):
            qs = self.active(user)
        else:
            qs = self.public(user)
        return qs

    def public(self, user=None):
        return self.active(user).filter(is_public=True)

    def private(self, user=None):
        return self.active(user).filter(is_public=False)

    def with_path(self, path, user=None):
        """
        Retrieves a project based on its "path," which is a list or tuple of
        project slugs that are all parents of a particular project.  This
        makes it possible for multiple projects to have the same slug as long
        as they are children of different projects.
        """

        project = None

        # split the string version of the path if necessary
        if not isinstance(path, list):
            path = path.split('/')

        try:
            # iterate over all slugs
            for slug in path:
                if not project:
                    # the top-most project for this path
                    project = self.active(user).get(slug=slug)
                else:
                    # find the subproject of the current project with this slug
                    project = project.subprojects.active(user).get(slug=slug)
        except models.ObjectDoesNotExist:
            pass

        return project

class AttributeWithDefaultManager(models.Manager):
    def default(self):
        try:
            return self.get_query_set().get(is_default=True)
        except models.ObjectDoesNotExist:
            return None
