from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import RedirectView

urlpatterns = patterns('',
                       url(r'^$', 'searcher.views.search_page_view', name='index'),
                       url(r'^about/$', 'main.views.about_page_view', name='about'),
                       url(r'^contacts/$', 'main.views.contacts_page_view', name='contacts'),
                       url(r'^searcher/', include(('searcher.urls', 'searcher', 'searcher'))),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT}),
                       )
