from django.db import models
from ponymine.models import Project

class WikiPage(models.Model):
    project = models.ForeignKey(Project, related_name='wiki_pages')