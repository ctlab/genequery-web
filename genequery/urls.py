from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

urlpatterns = patterns('genequery',
                       url(r'^$', RedirectView.as_view(url=reverse_lazy('searcher:index')), name='index'),
                       url(r'^about/$', 'main.views.about_page_view', name='about'),
                       url(r'^contacts/$', 'main.views.contacts_page_view', name='contacts'),
                       url(r'^example/$', 'main.views.example_page_view', name='example'),
                       url(r'^downloads/$', 'main.views.downloads_page_view', name='downloads'),
                       url(r'^searcher/', include(('genequery.searcher.urls', 'searcher', 'searcher'))),
                       url(r'^admin/', include(admin.site.urls)))
urlpatterns += [url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                    {'document_root': settings.MEDIA_ROOT})]