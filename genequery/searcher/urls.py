from django.conf.urls import patterns, url


urlpatterns = patterns('genequery.searcher.views',
                       url(r'^$', 'search_page_view', name='index'),
                       url(r'^search/$', 'search_processor_view', name='search'),
                       url(r'^search/get_overlap/$', 'get_overlap', name='get_overlap'),
                       )