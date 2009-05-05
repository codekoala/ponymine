from django.db import models
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
    
    def with_path(self, path):
        """
        Retrieves a project based on its "path," which is a list or tuple of 
        project slugs that are all parents of a particular project.  This 
        makes it possible for multiple projects to have the same slug as long
        as they are children of different projects.
        """
        
        project = None
        
        try:
            # iterate over all slugs
            for slug in path:
                if not project:
                    # the top-most project for this path
                    project = self.active().get(slug=slug)
                else:
                    # find the subproject of the current project with this slug
                    project = project.subprojects.get(slug=slug)
        except models.ObjectDoesNotExist:
            pass
        
        return project

class PriorityManager(models.Manager):
    def default(self):
        try:
            return self.get_query_set().get(is_default=True)
        except models.ObjectDoesNotExist:
            return None

StatusManager = PriorityManager