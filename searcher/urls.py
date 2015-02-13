from django.conf.urls import patterns, url

urlpatterns = patterns('searcher.views',
                       url(r'^$', 'search_page_view', name='index'),
                       url(r'^search/$', 'search_processor_view', name='search'))
