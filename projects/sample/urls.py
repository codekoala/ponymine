from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),
    (r'^', include('ponymine.urls')),
)

if settings.DEBUG:
    """
    Serve static media using Django when DEBUG = True
    """
    urlpatterns += patterns('',
        (r'^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'),
         'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
