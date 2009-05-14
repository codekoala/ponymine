from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

UPLOAD_DIR = getattr(settings, 'PONYMINE_ATTACH_DIR', 'attachments/')
DEFAULT_TYPE = getattr(settings, 'PONYMINE_ATTACH_TYPE', 'text/plain')

class Attachment(models.Model):
    owner = models.ForeignKey(User)
    description = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=50, default=DEFAULT_TYPE)
    attachment = models.FileField(upload_to=UPLOAD_DIR)
    ip_address = models.IPAddressField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('file_type', 'attachment')